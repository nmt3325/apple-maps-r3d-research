#!/usr/bin/env python3
"""Audit bounded GPU buffer snapshots from mapkit_probe, using only stdlib."""
import argparse
import collections
import hashlib
import json
import math
import plistlib
import re
import struct
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_local(directory, name):
    require(bool(name), 'missing snapshot filename')
    path = (directory / name).resolve()
    require(path.is_relative_to(directory.resolve()), 'snapshot path escapes its run directory')
    return path.read_bytes()


def is_splat(name):
    return 'Flyover::splat_vertex' in name and 'Flyover::splat_fragment' in name


def half(value):
    return struct.unpack('<e', struct.pack('<e', value))[0]


def capture_info(directory, rows):
    trace = directory/'mapkit.gputrace'
    if not trace.is_dir():
        return None
    meta = plistlib.loads((trace/'metadata').read_bytes())
    starts = [r for r in rows if r['event'] == 'capture_start' and r['success']]
    stops = [r for r in rows if r['event'] == 'capture_stop']
    delta = None
    if starts and stops and 'draw_calls_at_start' in starts[-1] and 'draw_calls_at_stop' in stops[-1]:
        delta = stops[-1]['draw_calls_at_stop'] - starts[-1]['draw_calls_at_start']
    files = [p for p in trace.rglob('*') if p.is_file()]
    stream_size = (trace/'capture').stat().st_size
    return dict(file_count=len(files), bytes=sum(p.stat().st_size for p in files),
        capture_stream_bytes=stream_size, capture_stream_sha256=digest((trace/'capture').read_bytes()),
        metadata_sha256=digest((trace/'metadata').read_bytes()),
        captured_frames=meta.get('DYCaptureEngine.captured_frames_count'),
        observed_draw_calls_in_capture_window=delta,
        has_command_data=stream_size > 8 and delta is not None and delta > 0,
        caveat='This is the instrumented MapKit host. Frame count alone does not establish a nonempty capture.')


def audit(directory):
    directory = Path(directory)
    raw = (directory/'events.jsonl').read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    starts = [r for r in rows if r['event'] == 'start']
    summaries = [r for r in rows if r['event'] == 'summary']
    require(len(starts) == 1 and len(summaries) == 1, 'expected one completed probe run')
    require(not any(r['event'] == 'map_error' for r in rows), 'MapKit reported a loading error')
    result = dict(scope='Instrumented macOS MapKit host; not Maps.app uniform capture',
        run=directory.name, events_sha256=digest(raw),
        scene={k:v for k,v in starts[0].items() if k not in ['uptime','pid','event']},
        event_counts=dict(collections.Counter(r['event'] for r in rows)),
        summary={k:v for k,v in summaries[0].items() if k not in ['uptime','event']},
        uniforms=[], resources=[], specialization_variants={},
        render_passes=[{k:v for k,v in r.items() if k not in ['uptime','event']} for r in rows if r['event']=='splat_render_pass'])
    uniforms = {}
    for row in rows:
        if row['event'] != 'candidate_splat_constants':
            continue
        require(is_splat(row['pipeline']), 'refusing SplatConstants interpretation on another pipeline')
        data = read_local(directory,row['uniform_file'])
        require(len(data) == 256, 'SplatConstants must be 256 bytes')
        sid, c, p = struct.unpack_from('<iff',data,192)
        require((sid,c,p) == (row['splat_id'],row['alpha_concentration'],row['alpha_pre_factor']), 'logged constants differ from snapshot')
        require(all(math.isfinite(v) for v in (c,p)) and c > 0 and p > 0, 'invalid alpha uniforms')
        minimum = struct.unpack_from('<3f',data,224)
        scale = struct.unpack_from('<3f',data,240)
        require(all(math.isfinite(v) for v in (*minimum,*scale)) and all(v >= 0 for v in scale), 'invalid position bounds')
        value = dict(splat_id=sid, sha256=digest(data), alpha_concentration=c, alpha_pre_factor=p,
            alpha_concentration_u32=hex(struct.unpack_from('<I',data,196)[0]),
            alpha_pre_factor_u32=hex(struct.unpack_from('<I',data,200)[0]),
            fragment_half_concentration=half(c), fragment_half_pre_factor=half(p),
            bounds_min=minimum, bounds_scale=scale,
            caveat='First instance in a bound constant array; IDs are render slots, not geographic tile IDs.')
        result['uniforms'].append(value)
        uniforms[sid] = value
    require(bool(uniforms), 'no actual Splat pipeline constants were observed')
    by_slot = collections.defaultdict(dict)
    for row in rows:
        if row['event'] == 'splat_resource':
            require(row['splat_id'] in uniforms, 'resource has no matching uniform snapshot')
            data = read_local(directory,row['file'])
            require(len(data) == row['saved_bytes'], 'resource byte length differs from log')
            by_slot[row['splat_id']][row['kind']] = (row,data)
    for sid, group in by_slot.items():
        names = ['positions-ushort4','properties-12','orders-int32']
        require(set(group) == set(names), 'missing one of the three Splat resources')
        hashes = {k:digest(v[1]) for k,v in group.items()}
        entry = dict(splat_id=sid, sha256=hashes, bytes={k:len(v[1]) for k,v in group.items()},
                     complete=all(v[0]['complete'] for v in group.values()))
        if not entry['complete']:
            entry['caveat'] = 'Bounded prefix only; whole-array claims are skipped.'
            result['resources'].append(entry)
            continue
        positions, properties, order_data = [group[name][1] for name in names]
        require(len(positions) % 24 == len(properties) % 12 == len(order_data) % 4 == 0, 'invalid record stride')
        count = len(positions)//24
        require(count > 0 and count == len(properties)//12 == len(order_data)//4, 'Splat resource counts disagree')
        order = [v[0] for v in struct.iter_unpack('<i',order_data)]
        require(set(order) == set(range(count)), 'Splat order is not a full in-range permutation')
        quantized = list(struct.iter_unpack('<4H',positions))
        uniform = uniforms[sid]
        def xyz(v):
            return [uniform['bounds_min'][i] + v[i]/65535*uniform['bounds_scale'][i] for i in range(3)]
        first = order[0]
        gpu_color = list(properties[first*12:first*12+4])
        model_view = struct.unpack_from('<16f',read_local(directory,next(
            r['uniform_file'] for r in rows if r['event']=='candidate_splat_constants' and r['splat_id']==sid)))
        center_depth = []
        for i in range(0,len(quantized),3):
            center = [sum(xyz(v)[k] for v in quantized[i:i+3])/3 for k in range(3)]
            center_depth.append(sum(center[k]*model_view[k*4+2] for k in range(3))+model_view[14])
        require(all(math.isfinite(v) for v in center_depth), 'invalid view-space depth')
        ordered_depth = [center_depth[i] for i in order]
        differences = [b-a for a,b in zip(ordered_depth,ordered_depth[1:])]
        # A conservative two-step bound, not a proof of the CPU sorting key.
        bound = 2*sum(abs(model_view[k*4+2])*uniform['bounds_scale'][k]/65535 for k in range(3))
        entry.update(records=count, vertices=len(quantized), order_is_permutation=True,
            order_first_16=order[:16], position_w_histogram=dict(collections.Counter(v[3] for v in quantized)),
            properties_padding_u16_histogram=dict(collections.Counter(struct.unpack_from('<H',properties,i)[0] for i in range(10,len(properties),12))),
            first_ordered_triangle_index=first,
            first_ordered_triangle_local_xyz=[xyz(v) for v in quantized[first*3:first*3+3]],
            first_ordered_triangle_gpu_color_bytes=gpu_color,
            first_ordered_triangle_rgba=list(reversed(gpu_color)),
            depth_order=dict(depth_min=min(ordered_depth),depth_max=max(ordered_depth),
                adjacent_pairs=len(differences),strict_front_to_back_inversions=sum(v>0 for v in differences),
                max_inversion=max([0,*differences]),pairwise_two_quantization_steps=bound,
                inversions_above_two_steps=sum(v>bound for v in differences),
                interpretation='Consistent with approximately front-to-back view-z ordering if inversions stay within this bound; the CPU comparator is unproven.'),
            note='Color byte reversal and q/65535*boundsScale+boundsMin follow this build’s AIR. Positions are tile-local, not latitude/longitude.')
        result['resources'].append(entry)
    require(bool(result['resources']), 'no resolvable GPU resources')
    flag_names = {1:'useMetalBarycentricCoordinate',2:'colorAdjustmentEnabled',3:'usePbrRendering',4:'useClipPlanes'}
    for row in rows:
        if row['event'] != 'function_specialized' or not row['success'] or 'Flyover::splat_' not in row['name']:
            continue
        variant = {}
        for index,name in flag_names.items():
            if row['name'] == 'Flyover::splat_fragment' and index != 1:
                continue  # The fragment only declares function constant 1.
            v = row['constants'].get(f'index:{index}')
            if not v or v['metal_type'] != 53:
                continue
            match = re.search(r'0x([0-9a-fA-F]{2})',v['hex'])
            if match:
                variant[name] = bool(int(match[1],16))
        if variant:
            variants = result['specialization_variants'].setdefault(row['name'],[])
            if variant not in variants:
                variants.append(variant)
    result['capture'] = capture_info(directory,rows)
    result['limitations'] = [
        'Hooks retain bounded buffer objects and affect scheduling/lifetimes; this is not a performance benchmark.',
        'No R3D tile ID, exact LOD policy, native decoder parity, or final frame parity is established by these checks.',
        'Constant sampling deduplicates by render slot and alpha pair; it is not every draw or every instance.',
        'Specialization variants are observed successful function creations; unobserved values are omitted, not assumed false.'
    ]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    result = audit(args.run)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(run=result['run'], uniforms=len(result['uniforms']),
        resources=len(result['resources']),
        complete_resource_groups=sum(r['complete'] for r in result['resources']),
        nonempty_capture=result['capture']['has_command_data'] if result['capture'] else None)))


if __name__ == '__main__':
    main()
