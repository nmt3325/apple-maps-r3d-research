import Foundation
import Metal
let device=MTLCreateSystemDefaultDevice()!
let lib=try device.makeLibrary(URL:URL(fileURLWithPath:"/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources/default.metallib"))
func f(_ name:String)throws -> MTLFunction {
 let base=lib.makeFunction(name:name)!
 if base.functionConstantsDictionary.isEmpty{return base}
 let vals=MTLFunctionConstantValues();var b=false
 for (_,v) in base.functionConstantsDictionary { vals.setConstantValue(&b,type:.bool,index:v.index) }
 return try lib.makeFunction(name:name,constantValues:vals)
}
let passes:[(String,String)] = [("screen_vertex","clear_tile"),("splat_vertex","splat_fragment"),("screen_vertex","intermediate_resolve_tile"),("screen_vertex","final_resolve_color"),("screen_vertex","final_resolve_depth")]
for (vert,frag) in passes {
 let desc=MTLRenderPipelineDescriptor();desc.vertexFunction=try f("Flyover::"+vert);desc.fragmentFunction=try f("Flyover::"+frag)
 desc.colorAttachments[0].pixelFormat = .rgba16Float
 desc.depthAttachmentPixelFormat = .depth32Float
 do {let state=try device.makeRenderPipelineState(descriptor:desc);print("PASS_PIPELINE_OK",vert,frag,state.label ?? "")}
 catch {print("PASS_PIPELINE_ERROR",vert,frag,error)}
}
