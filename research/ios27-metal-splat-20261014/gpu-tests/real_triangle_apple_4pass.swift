import Foundation
import Metal
let gpu=MTLCreateSystemDefaultDevice()!
let lib=try gpu.makeLibrary(URL:URL(fileURLWithPath:"/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources/default.metallib"))
func funcSpec(_ n:String)throws -> MTLFunction {
 let base=lib.makeFunction(name:"Flyover::"+n)!
 if base.functionConstantsDictionary.isEmpty{return base}
 let v=MTLFunctionConstantValues();var bool=false
 for (_,c) in base.functionConstantsDictionary {v.setConstantValue(&bool,type:.bool,index:c.index)}
 return try lib.makeFunction(name:base.name,constantValues:v)
}
let vert=try funcSpec("splat_vertex")
let frag=try funcSpec("splat_fragment")
func pipe(_ v:String,_ f:String)throws -> MTLRenderPipelineState {
 let d=MTLRenderPipelineDescriptor(); d.vertexFunction = v == "splat_vertex" ? vert : try funcSpec(v)
 d.fragmentFunction = f == "splat_fragment" ? frag : try funcSpec(f)
 d.colorAttachments[0].pixelFormat = .rgba16Float
 d.depthAttachmentPixelFormat = .depth32Float
 return try gpu.makeRenderPipelineState(descriptor:d)
}
let clear=try pipe("screen_vertex","clear_tile")
let splat=try pipe("splat_vertex","splat_fragment")
let mid=try pipe("screen_vertex","intermediate_resolve_tile")
let fin=try pipe("screen_vertex","final_resolve_color")
let res=64
let rtDesc=MTLTextureDescriptor.texture2DDescriptor(pixelFormat:.rgba16Float,width:res,height:res,mipmapped:false);rtDesc.usage=[.renderTarget,.shaderRead];rtDesc.storageMode = .shared
let rt=gpu.makeTexture(descriptor:rtDesc)!
let dpDesc=MTLTextureDescriptor.texture2DDescriptor(pixelFormat:.depth32Float,width:res,height:res,mipmapped:false);dpDesc.usage=[.renderTarget];dpDesc.storageMode = .private
let depth=gpu.makeTexture(descriptor:dpDesc)!
let shared=gpu.makeBuffer(length:80,options:.storageModeShared)!
let uniforms=gpu.makeBuffer(length:256,options:.storageModeShared)!
func writeF(_ b:MTLBuffer,_ offset:Int,_ v:Float){ b.contents().advanced(by:offset).assumingMemoryBound(to:Float.self).pointee=v }
func writeI(_ b:MTLBuffer,_ offset:Int,_ v:UInt32){ b.contents().advanced(by:offset).assumingMemoryBound(to:UInt32.self).pointee=v }
for k in 0..<4 {
 writeF(shared,k*16+k*4,1)
 writeF(uniforms,k*16+k*4,1)
}
writeF(uniforms,196,1) // c
writeF(uniforms,200,20) // p
writeF(uniforms,224,-0.9);writeF(uniforms,228,-0.9);writeF(uniforms,232,0)
writeF(uniforms,240,1.8);writeF(uniforms,244,1.8);writeF(uniforms,248,0)
writeI(uniforms,192,0)
let pos:[UInt16] = [2500,62500,32768,0,62500,27143,32768,0,29959,2500,32768,0]
let vertices = pos.withUnsafeBufferPointer {gpu.makeBuffer(bytes:$0.baseAddress!,length:$0.count*2,options:.storageModeShared)!}
var props=[UInt8](repeating:0,count:12);props[0]=239;props[1]=239;props[2]=239;props[3]=61
let property=props.withUnsafeBufferPointer { gpu.makeBuffer(bytes:$0.baseAddress!,length:$0.count,options:.storageModeShared)!}
var zero:UInt32=0
let order=gpu.makeBuffer(bytes:&zero,length:4,options:.storageModeShared)!
let sEncoder=vert.makeArgumentEncoder(bufferIndex:0)
let aEncoder=vert.makeArgumentEncoder(bufferIndex:1)
print("ARGUMENT_ENCODER_LENGTHS",sEncoder.encodedLength,aEncoder.encodedLength)
let sAB=gpu.makeBuffer(length:sEncoder.encodedLength,options:.storageModeShared)!
let aAB=gpu.makeBuffer(length:aEncoder.encodedLength,options:.storageModeShared)!
sEncoder.setArgumentBuffer(sAB,offset:0);sEncoder.setBuffer(shared,offset:0,index:0);sEncoder.setBuffer(uniforms,offset:0,index:1)
aEncoder.setArgumentBuffer(aAB,offset:0)
aEncoder.setBuffer(vertices,offset:0,index:0);aEncoder.setBuffer(property,offset:0,index:16384);aEncoder.setBuffer(order,offset:0,index:32768)
let rp=MTLRenderPassDescriptor();rp.colorAttachments[0].texture=rt;rp.colorAttachments[0].loadAction = .clear;rp.colorAttachments[0].storeAction = .store;rp.colorAttachments[0].clearColor=MTLClearColorMake(0,0,0,1)
rp.imageblockSampleLength = 28
rp.depthAttachment.texture=depth;rp.depthAttachment.loadAction = .clear;rp.depthAttachment.storeAction = .dontCare;rp.depthAttachment.clearDepth=1
let cmd=gpu.makeCommandQueue()!.makeCommandBuffer()!
let enc=cmd.makeRenderCommandEncoder(descriptor:rp)!
enc.useResources([shared,uniforms,vertices,property,order],usage:.read,stages:[.vertex,.fragment])
enc.setCullMode(.none)
for (pipe1,isSplat) in [(clear,false),(splat,true),(mid,false),(fin,false)] {
 enc.setRenderPipelineState(pipe1)
 if isSplat {
  enc.setVertexBuffer(sAB,offset:0,index:0);enc.setVertexBuffer(aAB,offset:0,index:1)
  enc.setFragmentBuffer(sAB,offset:0,index:0)
 }
 enc.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:3)
}
enc.endEncoding();cmd.commit();cmd.waitUntilCompleted()
if let err=cmd.error {print("GPU_FRAME_ERROR",err)} else {print("GPU_FRAME_COMPLETE",cmd.status.rawValue)}
var samples=[UInt16](repeating:0,count:res*res*4)
samples.withUnsafeMutableBufferPointer { p in rt.getBytes(p.baseAddress!,bytesPerRow:res*8,from:MTLRegionMake2D(0,0,res,res),mipmapLevel:0) }
func rgba(_ x:Int,_ y:Int)->[Float] {let idx=(y*res+x)*4; return (0..<4).map{Float(Float16(bitPattern:samples[idx+$0]))}}
for (x,y) in [(0,0),(30,30),(31,31),(32,32),(20,20),(12,12),(50,50)] {print("pixel",x,y,rgba(x,y))}

try! Data(bytes:samples,count:samples.count*MemoryLayout<UInt16>.size).write(to: URL(fileURLWithPath:"/Users/denken/ios27-maps-binary-lab/gpu-analysis/real_triangle_apple_4pass.raw"))
