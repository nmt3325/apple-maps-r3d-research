"""Summarize retained iOS sessions without mixing launches or exposing locations."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import zipfile

MAX_LOG_BYTES = 64*1024*1024


def read_logs(path):
    if path.is_dir():
        files = sorted(path.glob('stream-*.jsonl'))
    elif path.suffix == '.zip':
        with zipfile.ZipFile(path) as archive:
            names = [i for i in archive.infolist() if i.filename.endswith('.jsonl') and not i.filename.startswith('__MACOSX/')]
            if sum(i.file_size for i in names) > MAX_LOG_BYTES:
                raise ValueError('Log archive exceeds read limit')
            payloads = [archive.read(i) for i in names]
    else:
        files = [path]
    if path.suffix != '.zip' or path.is_dir():
        payloads, remaining = [], MAX_LOG_BYTES
        for file in files:
            with file.open('rb') as stream:
                payload = stream.read(remaining+1)
            if len(payload) > remaining:
                raise ValueError('Logs exceed read limit')
            payloads.append(payload)
            remaining -= len(payload)
    if sum(map(len,payloads)) > MAX_LOG_BYTES:
        raise ValueError('Logs exceed read limit')
    rows = []
    for payload in payloads:
        lines = payload.splitlines()
        for index,line in enumerate(lines):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                if index != len(lines)-1 or payload.endswith(b'\n'):
                    raise
    return rows


def distribution(values):
    values = sorted(v for v in values if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v))
    if not values:
        return None
    return {'count':len(values),'medianMs':statistics.median(values),
            'p95Ms':values[int((len(values)-1)*.95)],'maxMs':values[-1],
            'atMost100Ms':sum(v<=100 for v in values)}


def summarize(rows):
    sessions = defaultdict(list)
    for row in rows:
        if row['event'] != 'export.snapshot':
            sessions[row['session_id']].append(row)
    output = []
    for session_id,entries in sorted(sessions.items(),key=lambda pair:min(r['unix_time'] for r in pair[1])):
        entries.sort(key=lambda r:r['sequence'])
        first,last = entries[0],entries[-1]
        coarse_zoom = next((r['fields']['coarse_zoom'] for r in entries if 'coarse_zoom' in r['fields']),18)
        latency_origin = next((r['fields']['latency_origin'] for r in entries if 'latency_origin' in r['fields']),'expanded_tile_plan')
        prefix = f's98_z{coarse_zoom}_'
        traces = defaultdict(dict)
        for row in entries:
            if row.get('trace_id'):
                traces[row['trace_id']][row['event']] = row
        metrics = {}
        for event,field in [('decode.end','duration_ms'),('pipeline.begin','queue_wait_ms'),
                            ('network.response','duration_ms'),('processing.begin','wait_ms'),
                            ('atlas.prepare_end','duration_ms'),
                            ('gpu.prepare_end','duration_ms'),('gpu.resident','needed_to_resident_ms'),
                            ('render.tile_first_submitted','needed_to_draw_ms'),
                            ('render.tile_first_completed','needed_to_completed_ms'),
                            ('render.tile_first_presented','needed_to_presented_ms')]:
            metrics[event] = distribution([r['fields'].get(field) for r in entries
                if r['event']==event and r.get('tile','').startswith(prefix)
                and (event!='decode.end' or r['fields'].get('function','decode_tile')=='decode_tile')])
        attempt = []
        for trace in traces.values():
            resident,begin = trace.get('gpu.resident'),trace.get('pipeline.begin')
            if resident and begin and resident.get('tile','').startswith(prefix):
                elapsed,wait = resident['fields'].get('needed_to_resident_ms'),begin['fields'].get('needed_wait_ms')
                if isinstance(elapsed,(int,float)) and isinstance(wait,(int,float)):
                    attempt.append(elapsed-wait)
                else:
                    attempt.append((resident['unix_time']-begin['unix_time'])*1000)
        textures = Counter(r['tile'] for r in entries if r['event']=='texture.replaced')
        errors = Counter(r['event'] for r in entries if r['event'].endswith('.error') and not r['fields'].get('cancelled',False))
        output.append({'session':session_id,'startUTC':datetime.fromtimestamp(first['unix_time'],timezone.utc).isoformat(),
            'hasSessionStart':any(r['event']=='session.start' for r in entries),
            'wallSpanSeconds':last['unix_time']-first['unix_time'],'records':len(entries),
            'compiledDecoder':next((r['fields'].get('compiled') for r in entries if r['event']=='decoder.ready'),None),
            'coarseZoom':coarse_zoom,'latencyOrigin':latency_origin,
            'coarseMetrics':metrics,'coarseAttemptToResident':distribution(attempt),
            'textureUpdates':sum(textures.values()),'maximumTextureUpdatesPerTile':max(textures.values(),default=0),
            'nonCancellationErrors':dict(errors),
            'measurement':'Needed-to-event includes the queue; attempt-to-resident excludes it. Simulator completion is not confirmed screen presentation.'})
    return {'schemaVersion':1,'sessions':output}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    result = summarize(read_logs(args.input))
    encoded = json.dumps(result,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(encoded)
    print(encoded)
