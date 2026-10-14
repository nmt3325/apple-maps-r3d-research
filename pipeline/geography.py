"""Shared metric coordinate frame for original polygon and Splat geometry."""
import math
import numpy as np

ESQ = 6.6943799901413165e-3
A = 6378137.0


def origin_frame(lat, lon, height=0.0):
    if not math.isfinite(lat) or not math.isfinite(lon) or not -85.05112878 <= lat <= 85.05112878 or not -180 <= lon <= 180:
        raise ValueError('Invalid WGS84 scene origin')
    p, l = math.radians(lat), math.radians(lon)
    n = A / math.sqrt(1 - ESQ * math.sin(p)**2)
    ecef = np.array([(n+height)*math.cos(p)*math.cos(l),
                     (n+height)*math.cos(p)*math.sin(l),
                     (n*(1-ESQ)+height)*math.sin(p)])
    east = [-math.sin(l), math.cos(l), 0]
    north = [-math.sin(p)*math.cos(l), -math.sin(p)*math.sin(l), math.cos(p)]
    up = [math.cos(p)*math.cos(l), math.cos(p)*math.sin(l), math.sin(p)]
    basis = np.array([east, up, [-v for v in north]])
    return ecef, basis


def world_positions(local, transform, frame):
    rotation = np.array(transform['matrixR3x3']).reshape(3, 3)
    translation = np.array(transform['ecefTranslation'])
    origin, basis = frame
    return (local.astype(np.float64) @ rotation.T + translation - origin) @ basis.T


def world_normals(local, transform, frame):
    rotation = np.array(transform['matrixR3x3']).reshape(3, 3)
    return local.astype(np.float64) @ rotation.T @ frame[1].T


def ecef_to_geodetic(points):
    x, y, z = np.asarray(points, dtype=np.float64).T
    longitude = np.arctan2(y, x)
    p = np.hypot(x, y)
    latitude = np.arctan2(z, p*(1-ESQ))
    for _ in range(8):
        n = A / np.sqrt(1 - ESQ*np.sin(latitude)**2)
        h = p / np.cos(latitude) - n
        latitude = np.arctan2(z, p*(1-ESQ*n/(n+h)))
    n = A / np.sqrt(1 - ESQ*np.sin(latitude)**2)
    h = p / np.cos(latitude) - n
    return np.column_stack([np.degrees(longitude), np.degrees(latitude), h])
