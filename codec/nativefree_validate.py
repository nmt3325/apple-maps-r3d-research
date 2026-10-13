"""Array invariants for independently decoded R3D geometry."""
import math
import struct


def validate_arrays(soup, mesh):
    if len(soup.xyz_f32) != 36 * soup.count or len(soup.attributes_f32) != 32 * soup.count:
        raise ValueError("Splat array shape mismatch")
    for (v,) in struct.iter_unpack('<f', soup.xyz_f32):
        if not math.isfinite(v):
            raise ValueError("Nonfinite Splat position")
    missing_colors = 0
    for i, (bits,) in enumerate(struct.iter_unpack('<I', soup.attributes_f32)):
        value = struct.unpack('<f', struct.pack('<I', bits))[0]
        if not math.isfinite(value):
            if bits != 0x7fc00000 or i % 8 not in (1, 2, 3):
                raise ValueError("Unexpected nonfinite Splat attribute")
            missing_colors += 1
    for key, count, channels in [('positions_f32', mesh['vertices'], 3),
                                 ('uv_f32', mesh['uvCount'], 2),
                                 ('normals_f32', mesh['normalCount'], 3)]:
        values = mesh[key]
        if len(values) != count * channels * 4:
            raise ValueError(f'{key} array length mismatch')
        if any(not math.isfinite(v[0]) for v in struct.iter_unpack('<f', values)):
            raise ValueError(f'{key} contains nonfinite values')
    for key, count in [('faces', mesh['vertices']), ('uv_indices', mesh['uvCount']),
                        ('normal_indices', mesh['normalCount'])]:
        if len(mesh[key]) != 3 * mesh['faceCount'] or any(not 0 <= v < count for v in mesh[key]):
            raise ValueError(f'{key} shape/index bounds mismatch')
    uv = [v[0] for v in struct.iter_unpack('<f', mesh['uv_f32'])]
    if not uv or min(uv) < -1e-6 or max(uv) > 1.001:
        raise ValueError("UV coordinates outside original atlas")
    normal_lengths = [math.sqrt(sum(v*v for v in xyz))
                      for xyz in struct.iter_unpack('<3f', mesh['normals_f32'])]
    if not normal_lengths or min(normal_lengths) < .99999 or max(normal_lengths) > 1.00001:
        raise ValueError("Invalid mesh normal length")
    return {'finiteGeometry': True, 'indexBounds': True, 'uvMin': min(uv), 'uvMax': max(uv),
            'normalLengthMin': min(normal_lengths), 'normalLengthMax': max(normal_lengths),
            'missingColorComponents': missing_colors,
            'missingColorPolicy': 'Preserve canonical NaNs in raw attributes; render missing RGB as zero'}
