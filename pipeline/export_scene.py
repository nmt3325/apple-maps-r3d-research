"""Export original polygon and Splat triangles as GLB and attribute-preserving PLY."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import numpy as np


def geometry(path, splat=False):
    data = path.read_bytes()
    magic, version, n, f = struct.unpack_from('<4I', data)
    expected = 16+40*n if splat else 16+32*n+12*f
    if version != 1 or magic != (0x53534452 if splat else 0x56334452) or len(data) != expected:
        raise ValueError(f'Invalid geometry buffer: {path.name}')
    if splat:
        return np.frombuffer(data, '<f4', 9*n, 16).reshape(-1, 3), np.frombuffer(data, 'u1', 4*n, 16+36*n).reshape(-1, 4)
    return (np.frombuffer(data, '<f4', 3*n, 16).reshape(-1, 3),
            np.frombuffer(data, '<f4', 2*n, 16+12*n).reshape(-1, 2),
            np.frombuffer(data, '<f4', 3*n, 16+20*n).reshape(-1, 3),
            np.frombuffer(data, '<u4', 3*f, 16+32*n))


def export(viewer, decoded, output):
    scene = json.loads((viewer/'scene.json').read_text())
    source = json.loads((decoded/'manifest.json').read_text())
    by_hash = {t['sourceSHA256']:t for t in source['results']}
    output.mkdir(parents=True, exist_ok=True)
    gltf = {'asset':{'version':'2.0','generator':'Independent Linux R3D exporter'},
            'extensionsUsed':['KHR_materials_unlit'], 'extensionsRequired':['KHR_materials_unlit'],
            'scene':0, 'scenes':[{'nodes':[]}], 'nodes':[], 'meshes':[], 'materials':[],
            'textures':[], 'images':[], 'bufferViews':[], 'accessors':[],
            'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':33071,'wrapT':33071}],
            'extras':{'originWGS84':scene['origin'], 'frame':scene['frame'],
                      'splatRendering':'Original triangles/RGBA, standard alpha blend; viewer barycentric alpha is not representable in core glTF'}}
    binary = bytearray()
    def view(data, target=None):
        binary.extend(b'\0'*((-len(binary))%4))
        offset = len(binary); binary.extend(data)
        v = {'buffer':0,'byteOffset':offset,'byteLength':len(data)}
        if target: v['target'] = target
        gltf['bufferViews'].append(v)
        return len(gltf['bufferViews'])-1
    def accessor(array, kind, component=5126, normalized=False, bounds=False):
        a = {'bufferView':view(array.tobytes(),34963 if kind=='SCALAR' else 34962),
             'componentType':component,'count':len(array),'type':kind}
        if normalized: a['normalized'] = True
        if bounds: a.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
        gltf['accessors'].append(a)
        return len(gltf['accessors'])-1
    def add_mesh(name, primitive, layer):
        index = len(gltf['meshes']);gltf['meshes'].append({'name':name,'primitives':[primitive]})
        gltf['scenes'][0]['nodes'].append(len(gltf['nodes']))
        gltf['nodes'].append({'name':name,'mesh':index,'extras':{'layer':layer}})
    splat_mat = {'name':'Original Splat RGBA','doubleSided':True,'alphaMode':'BLEND',
                 'pbrMetallicRoughness':{'metallicFactor':0,'roughnessFactor':1},'extensions':{'KHR_materials_unlit':{}}}
    gltf['materials'].append(splat_mat)
    vertices, colors, attributes = [], [], []
    for tile in scene['tiles']:
        row = by_hash[tile['sourceSHA256']]
        xyz, uv, normals, indices = geometry(viewer/tile['mesh'])
        if len(indices):
            uv = uv.copy();uv[:,1] = np.float32(1)-uv[:,1]  # glTF image coordinate origin is top-left
            image = len(gltf['images'])
            gltf['images'].append({'bufferView':view((viewer/tile['texture']).read_bytes()),'mimeType':'image/png'})
            texture = len(gltf['textures']);gltf['textures'].append({'sampler':0,'source':image})
            material = len(gltf['materials'])
            gltf['materials'].append({'name':tile['source']+' original atlas','doubleSided':True,
                  'pbrMetallicRoughness':{'baseColorTexture':{'index':texture},'metallicFactor':0,'roughnessFactor':1},
                  'extensions':{'KHR_materials_unlit':{}}})
            add_mesh(tile['source']+' polygons',{'attributes':{'POSITION':accessor(xyz,'VEC3',bounds=True),
                        'TEXCOORD_0':accessor(uv,'VEC2'),'NORMAL':accessor(normals,'VEC3')},
                        'indices':accessor(indices,'SCALAR',5125),'material':material,'mode':4},'polygon')
        splat_xyz, rgba = geometry(viewer/tile['splats'], True)
        add_mesh(tile['source']+' splats',{'attributes':{'POSITION':accessor(splat_xyz,'VEC3',bounds=True),
                    'COLOR_0':accessor(np.repeat(rgba,3,axis=0),'VEC4',5121,True)},'material':0,'mode':4},'splat')
        raw = (decoded/row['directory']/'splat-attributes-f32le.bin').read_bytes()
        spec = row['arrays']['splat-attributes-f32le.bin']
        if len(raw) != spec['bytes'] or hashlib.sha256(raw).hexdigest() != spec['sha256']:
            raise ValueError('Splat attribute integrity mismatch')
        attrs = np.frombuffer(raw,'<f4').reshape(-1,8)
        if len(splat_xyz) != 3*len(attrs): raise ValueError('Splat attribute shape mismatch')
        vertices.append(splat_xyz);colors.append(np.repeat(rgba,3,axis=0));attributes.append(np.repeat(attrs,3,axis=0))
    gltf['buffers'] = [{'byteLength':len(binary)}]
    header = json.dumps(gltf,separators=(',',':'),allow_nan=False).encode()
    header += b' '*((-len(header))%4);binary.extend(b'\0'*((-len(binary))%4))
    glb = struct.pack('<3I',0x46546c67,2,12+8+len(header)+8+len(binary))
    glb += struct.pack('<2I',len(header),0x4e4f534a)+header+struct.pack('<2I',len(binary),0x004e4942)+binary
    (output/'scene.glb').write_bytes(glb)
    xyz = np.concatenate(vertices);rgba = np.concatenate(colors);attrs = np.concatenate(attributes)
    dtype = np.dtype([('xyz','<f4',(3,)),('rgba','u1',(4,)),('attributes','<f4',(8,))])
    records = np.empty(len(xyz),dtype=dtype);records['xyz']=xyz;records['rgba']=rgba;records['attributes']=attrs
    face_dtype = np.dtype([('count','u1'),('indices','<u4',(3,))])
    faces = np.empty(len(xyz)//3,dtype=face_dtype);faces['count']=3;faces['indices']=np.arange(len(xyz),dtype='<u4').reshape(-1,3)
    ply_header = ['ply','format binary_little_endian 1.0', 'comment Original Splat triangles and eight attributes; east/up/south meters',
                  'comment origin_wgs84 '+','.join(map(str,scene['origin'])),f'element vertex {len(xyz)}']
    ply_header += [f'property float {c}' for c in ('x','y','z')]+[f'property uchar {c}' for c in ('red','green','blue','alpha')]
    ply_header += [f'property float attribute_{i}' for i in range(8)]
    ply_header += [f'element face {len(faces)}','property list uchar uint vertex_indices','end_header']
    (output/'splats.ply').write_bytes(('\n'.join(ply_header)+'\n').encode()+records.tobytes()+faces.tobytes())
    report = {'tiles':len(scene['tiles']),'polygonTriangles':scene['totals']['meshTriangles'],
              'splatTriangles':len(faces),'splatAttributesPerRecord':8,'origin':scene['origin'],
              'outputs':{name:{'bytes':(output/name).stat().st_size,'sha256':hashlib.sha256((output/name).read_bytes()).hexdigest()}
                         for name in ('scene.glb','splats.ply')},'nativeGoldenInput':False}
    (output/'export.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('viewer',type=Path);ap.add_argument('--decoded',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True);args = ap.parse_args()
    print(json.dumps(export(args.viewer,args.decoded,args.out_dir),indent=2))
