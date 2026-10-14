"""Read back GLB/PLY and compare every exported array/image to independent inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from export_scene import geometry

def audit(viewer, decoded, output):
    scene = json.loads((viewer/'scene.json').read_text());source = json.loads((decoded/'manifest.json').read_text())
    source = {t['sourceSHA256']:t for t in source['results']}
    glb = (output/'scene.glb').read_bytes();magic,version,length = struct.unpack_from('<3I',glb)
    assert (magic,version,length)==(0x46546c67,2,len(glb))
    jsize,jtype = struct.unpack_from('<2I',glb,12);assert jtype==0x4e4f534a
    gltf = json.loads(glb[20:20+jsize]);bsize,btype = struct.unpack_from('<2I',glb,20+jsize)
    assert btype==0x004e4942 and 28+jsize+bsize==len(glb)
    binary = glb[28+jsize:]
    def read_accessor(index):
        a = gltf['accessors'][index];v = gltf['bufferViews'][a['bufferView']]
        channels = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        dtype = {5126:'<f4',5125:'<u4',5121:'u1'}[a['componentType']]
        array = np.frombuffer(binary,dtype,a['count']*channels,v.get('byteOffset',0)+a.get('byteOffset',0))
        return array if channels==1 else array.reshape(-1,channels)
    def equal(actual,expected): assert actual.dtype==expected.dtype and actual.shape==expected.shape and actual.tobytes()==expected.tobytes()
    expected_xyz=[];expected_rgba=[];expected_attrs=[];faces=0
    assert len(gltf['meshes'])==2*len(scene['tiles']) and len(gltf['images'])==len(scene['tiles'])
    for i,tile in enumerate(scene['tiles']):
        xyz,uv,normals,idx = geometry(viewer/tile['mesh']);faces+=len(idx)//3
        uv=uv.copy();uv[:,1]=np.float32(1)-uv[:,1]
        polygon = gltf['meshes'][2*i]['primitives'][0];attr=polygon['attributes']
        equal(read_accessor(attr['POSITION']),xyz);equal(read_accessor(attr['NORMAL']),normals)
        equal(read_accessor(attr['TEXCOORD_0']),uv);equal(read_accessor(polygon['indices']),idx)
        image = gltf['images'][i];v = gltf['bufferViews'][image['bufferView']]
        png = binary[v['byteOffset']:v['byteOffset']+v['byteLength']]
        assert png==(viewer/tile['texture']).read_bytes()
        xyz,rgba = geometry(viewer/tile['splats'],True);rgba=np.repeat(rgba,3,axis=0)
        splat = gltf['meshes'][2*i+1]['primitives'][0]['attributes']
        equal(read_accessor(splat['POSITION']),xyz);equal(read_accessor(splat['COLOR_0']),rgba)
        row = source[tile['sourceSHA256']]
        attrs = np.fromfile(decoded/row['directory']/'splat-attributes-f32le.bin',dtype='<f4').reshape(-1,8)
        expected_xyz.append(xyz);expected_rgba.append(rgba);expected_attrs.append(np.repeat(attrs,3,axis=0))
    ply = (output/'splats.ply').read_bytes();header,payload=ply.split(b'end_header\n',1)
    xyz=np.concatenate(expected_xyz);rgba=np.concatenate(expected_rgba);attrs=np.concatenate(expected_attrs)
    assert f'element vertex {len(xyz)}'.encode() in header and f'element face {len(xyz)//3}'.encode() in header
    dtype=np.dtype([('xyz','<f4',(3,)),('rgba','u1',(4,)),('attributes','<f4',(8,))])
    vsize=len(xyz)*dtype.itemsize;records=np.frombuffer(payload[:vsize],dtype)
    equal(records['xyz'],xyz);equal(records['rgba'],rgba);equal(records['attributes'],attrs)
    fdtype=np.dtype([('count','u1'),('indices','<u4',(3,))]);triangles=np.frombuffer(payload[vsize:],fdtype)
    assert len(triangles)==len(xyz)//3 and np.all(triangles['count']==3)
    equal(triangles['indices'],np.arange(len(xyz),dtype='<u4').reshape(-1,3))
    return {'pass':True,'tiles':len(scene['tiles']),'polygonTriangles':faces,'splatTriangles':len(triangles),
            'GLB':'All XYZ, normals, indices, flipped UV, RGBA and PNG bytes exact',
            'PLY':'All XYZ, RGBA, eight attribute float bits including NaN, and triangle indices exact',
            'nativeGoldenInput':False,'SHA256':{name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in ('scene.glb','splats.ply')}}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('viewer',type=Path)
    ap.add_argument('--decoded',type=Path,required=True);ap.add_argument('--exports',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True);args=ap.parse_args()
    result=audit(args.viewer,args.decoded,args.exports);args.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
