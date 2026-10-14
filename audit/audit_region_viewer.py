"""Validate independent region geometry, geolocation and shared layer placement."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image
import pillow_heif
from scipy.spatial import cKDTree

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO/'pipeline'))
from geography import origin_frame, world_positions, world_normals, ecef_to_geodetic
from build_viewer import read_array


def surface_distances(points, triangles):
    """Distances to candidate source triangles; 24 nearest centroids per sample."""
    centers = triangles.mean(axis=1)
    tree = cKDTree(centers)
    _, indices = tree.query(points, k=min(24,len(triangles)))
    if indices.ndim == 1:
        indices=indices[:,None]
    tri = triangles[indices]
    p = points[:,None,:]
    a,b,c=tri[:,:,0],tri[:,:,1],tri[:,:,2]
    ab,ac=b-a,c-a
    n=np.cross(ab,ac)
    denom=np.sum(n*n,axis=2)
    dot=np.sum((p-a)*n,axis=2)
    plane=dot*dot/np.maximum(denom,1e-24)
    proj=p-n*(dot/np.maximum(denom,1e-24))[:,:,None]
    ap=proj-a
    d00=np.sum(ab*ab,axis=2);d01=np.sum(ab*ac,axis=2);d11=np.sum(ac*ac,axis=2)
    d20=np.sum(ap*ab,axis=2);d21=np.sum(ap*ac,axis=2)
    divisor=d00*d11-d01*d01
    u=(d11*d20-d01*d21)/np.maximum(divisor,1e-24)
    v=(d00*d21-d01*d20)/np.maximum(divisor,1e-24)
    valid=(u>=0)&(v>=0)&(u+v<=1)&(denom>1e-24)
    result=np.where(valid,plane,np.inf)
    for x,y in ((a,b),(b,c),(c,a)):
        edge=y-x
        t=np.clip(np.sum((p-x)*edge,axis=2)/np.maximum(np.sum(edge*edge,axis=2),1e-24),0,1)
        closest=x+t[:,:,None]*edge
        result=np.minimum(result,np.sum((p-closest)**2,axis=2))
    return np.sqrt(result.min(axis=1))


def audit(decoded, viewer, raw_dir, bounds):
    pillow_heif.register_heif_opener()
    manifest=json.loads((decoded/'manifest.json').read_text())
    scene=json.loads((viewer/'scene.json').read_text())
    if manifest.get('nativeGoldenInput') is not False or scene.get('nativeGoldenInput') is not False:
        raise ValueError('Independent inputs required')
    frame=origin_frame(*scene['origin'])
    table={t['source']:t for t in scene['tiles']}
    rows=[];all_distances=[]
    south,west,north,east=bounds
    for tile in manifest['results']:
        raw=(raw_dir/tile['source']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=tile['sourceSHA256']:
            raise ValueError('Original R3D hash differs from decoded provenance')
        directory=decoded/tile['directory'];render=table[tile['source']]
        positions=read_array(directory,tile,'mesh-xyz-f32le.bin','<f4',3)
        uv=read_array(directory,tile,'mesh-uv-f32le.bin','<f4',2)
        normals=read_array(directory,tile,'mesh-normals-f32le.bin','<f4',3)
        ip=read_array(directory,tile,'mesh-position-indices-u32le.bin','<u4')
        iu=read_array(directory,tile,'mesh-uv-indices-u32le.bin','<u4')
        inn=read_array(directory,tile,'mesh-normal-indices-u32le.bin','<u4')
        spline=read_array(directory,tile,'splat-xyz-f32le.bin','<f4',3)
        material=read_array(directory,tile,'splat-material20.bin','u1',20)
        unique,inverse=np.unique(np.column_stack([ip,iu,inn]),axis=0,return_inverse=True)
        expected=world_positions(positions,tile['georeference'],frame)
        expected_splat=world_positions(spline,tile['georeference'],frame)
        data=(viewer/render['mesh']).read_bytes();header=struct.unpack_from('<4I',data)
        magic,version,n,f=header
        if magic!=0x56334452 or version!=1 or n!=len(unique) or f!=tile['meshTriangles'] or len(data)!=16+32*n+12*f:
            raise ValueError('Rendered mesh length mismatch')
        actual=np.frombuffer(data,'<f4',3*n,16).reshape(-1,3)
        actual_uv=np.frombuffer(data,'<f4',2*n,16+12*n).reshape(-1,2)
        actual_normals=np.frombuffer(data,'<f4',3*n,16+20*n).reshape(-1,3)
        indices=np.frombuffer(data,'<u4',3*f,16+32*n)
        if not np.array_equal(actual,expected[unique[:,0]].astype('<f4')) or not np.array_equal(actual_uv,uv[unique[:,1]]) or not np.array_equal(indices,inverse.astype('<u4')):
            raise ValueError('Rendered polygon differs from original independently decoded arrays')
        if not np.array_equal(actual_normals,world_normals(normals,tile['georeference'],frame)[unique[:,2]].astype('<f4')):
            raise ValueError('Rendered mesh normal transformation mismatch')
        data=(viewer/render['splats']).read_bytes();h=struct.unpack_from('<4I',data);sn=h[2]
        if h!=(0x53534452,1,tile['splatRecords'],0) or len(data)!=16+40*sn:
            raise ValueError('Rendered Splat length mismatch')
        actual_splat=np.frombuffer(data,'<f4',9*sn,16).reshape(-1,3)
        rgba=np.frombuffer(data,'u1',4*sn,16+36*sn).reshape(-1,4)
        if not np.array_equal(actual_splat,expected_splat.astype('<f4')) or not np.array_equal(rgba,material[:,:4]):
            raise ValueError('Rendered Splat geometry/color mismatch')
        with Image.open(directory/'atlas-0.heic') as image:
            source=np.asarray(image.convert('RGB'))
        with Image.open(viewer/render['texture']) as image:
            texture=np.asarray(image.convert('RGB'))
        if not np.array_equal(source,texture):
            raise ValueError('PNG texture pixels differ from the original HEIC decode')
        combined=np.concatenate([actual,actual_splat])
        if not np.isfinite(combined).all() or not np.isfinite(actual_uv).all() or indices.max()>=n:
            raise ValueError('Nonfinite or invalid rendered geometry')
        geo=ecef_to_geodetic(combined.astype(np.float64)@frame[1]+frame[0])
        if not ((geo[:,0]>=west)&(geo[:,0]<=east)&(geo[:,1]>=south)&(geo[:,1]<=north)).all():
            raise ValueError('Decoded geometry is outside expected geographic region')
        # Float32 display conversion is the only layer placement error allowed.
        mesh_error=float(np.max(np.abs(actual.astype(np.float64)-expected[unique[:,0]])))
        splat_error=float(np.max(np.abs(actual_splat.astype(np.float64)-expected_splat)))
        if max(mesh_error,splat_error)>0.001:
            raise ValueError('Layer coordinate conversion exceeds 1 mm')
        visible=np.flatnonzero(rgba[:,3]>0)
        selected=visible[np.linspace(0,len(visible)-1,min(512,len(visible)),dtype=int)] if len(visible) else visible
        centers=actual_splat.reshape(-1,3,3)[selected].mean(axis=1)
        distances=surface_distances(centers,actual[indices.reshape(-1,3)]) if len(centers) else np.empty(0)
        all_distances.extend(distances.tolist())
        rows.append({'tile':tile['source'],'sourceSHA256':tile['sourceSHA256'],
                     'vertices':n,'polygonFaces':f,'splatRecords':sn,'finite':True,'indicesExact':True,'uvExact':True,
                     'textureRGBPixelsExact':True,'sharedCoordinateFrame':True,
                     'maxMeshFrameRoundingMeters':mesh_error,'maxSplatFrameRoundingMeters':splat_error,
                     'geodeticMin':geo.min(axis=0).tolist(),'geodeticMax':geo.max(axis=0).tolist(),
                     'surfaceDistanceSampleCount':len(centers),
                     'surfaceDistanceMedianMeters':float(np.median(distances)) if len(distances) else None})
    distance=np.array(all_distances)
    return {'tiles':len(rows),'origin':scene['origin'],'geographicBoundsSWNE':bounds,
            'polygonFaces':sum(x['polygonFaces'] for x in rows),'splatRecords':sum(x['splatRecords'] for x in rows),
            'allGeometryFinite':True,'allIndicesAndUVExact':True,'allTexturesDecodedRGBExact':True,
            'sharedFramePlacementVerified':True,'nativeGoldenInput':False,
            'surfaceDistanceSampleCount':len(distance),
            'surfaceDistanceMetersPercentiles':dict(zip(['p50','p90','p95','p99','max'],np.percentile(distance,[50,90,95,99,100]).tolist())),
            'surfaceDistanceScope':'Deterministic samples of visible Splat centroids to original mesh triangles among 24 nearest centroids; diagnostic, not equality of the two distinct geometry layers',
            'results':rows}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('decoded',type=Path);p.add_argument('viewer',type=Path);p.add_argument('raw_dir',type=Path)
    p.add_argument('--bounds',type=float,nargs=4,required=True,metavar=('SOUTH','WEST','NORTH','EAST'))
    p.add_argument('--report',type=Path,required=True);args=p.parse_args()
    report=audit(args.decoded,args.viewer,args.raw_dir,args.bounds)
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))


if __name__=='__main__':main()
