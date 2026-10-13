"""Explain normal rounding differences with independent Decimal trigonometry."""
from decimal import Decimal, localcontext
from functools import lru_cache
import math
import struct


def f32(value):
    return struct.unpack('<f', struct.pack('<f', float(value)))[0]


def bits(value):
    return struct.unpack('<I', struct.pack('<f', value))[0]


def value(word):
    return struct.unpack('<f', struct.pack('<I', word))[0]


def decimal_sincos(argument):
    with localcontext() as context:
        context.prec = 90
        x = Decimal.from_float(argument)
        sine = sine_term = x
        cosine = cosine_term = Decimal(1)
        for n in range(1, 110):
            sine_term *= -x * x / ((2 * n) * (2 * n + 1))
            cosine_term *= -x * x / ((2 * n - 1) * (2 * n))
            sine += sine_term
            cosine += cosine_term
        return f32(sine), f32(cosine)


@lru_cache(maxsize=65536)
def trace(word, step):
    theta = f32((word >> 16) * step)
    sin_theta, cos_theta = decimal_sincos(theta)
    phi = f32(f32(f32((word & 65535) * step) / max(sin_theta, f32(1e-6))) + f32(-math.pi))
    sin_phi, cos_phi = decimal_sincos(phi)
    correct = (f32(cos_phi * sin_theta), f32(sin_phi * sin_theta), cos_theta)
    return {'packedNormal': hex(word), 'thetaBits': hex(bits(theta)),
            'sinThetaBits': hex(bits(sin_theta)), 'phiBits': hex(bits(phi)),
            'sinPhiBits': hex(bits(sin_phi)), 'correct': correct,
            'correctBits': [hex(bits(v)) for v in correct]}


def explain(packed, step, actual, golden):
    rows = []
    cache = {}
    for i, ((a,), (b,)) in enumerate(zip(struct.iter_unpack('<I', actual),
                                        struct.iter_unpack('<I', golden))):
        if a == b:
            continue
        word = struct.unpack_from('<I', packed, i // 3 * 4)[0]
        if word not in cache:
            cache[word] = trace(word, step)
        evidence = cache[word]
        axis = i % 3
        if axis != 1 or bits(evidence['correct'][axis]) != a or abs(a - b) > 1:
            raise ValueError("Normal difference is not explained by one-ULP sine rounding")
        sin_phi = int(evidence['sinPhiBits'], 16)
        sin_theta = value(int(evidence['sinThetaBits'], 16))
        candidates = [candidate for candidate in (sin_phi - 1, sin_phi + 1)
                      if bits(f32(value(candidate) * sin_theta)) == b]
        if not candidates:
            raise ValueError("Golden normal differs beyond adjacent float32 sine rounding")
        rows.append({'index': i, 'actualBits': hex(a), 'goldenBits': hex(b),
                     **{k: v for k, v in evidence.items() if k != 'correct'},
                     'compatibleNativeSinPhiBits': [hex(v) for v in candidates],
                     'reason': 'Native paired float32 trigonometry differs from correctly rounded sine by one ULP'})
    return rows
