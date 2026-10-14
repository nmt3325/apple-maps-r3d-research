import Foundation
import Metal
let p = "/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources/default.metallib"
let gpu = MTLCreateSystemDefaultDevice()!
let lib = try gpu.makeLibrary(URL: URL(fileURLWithPath: p))
func specialized(_ name: String) throws -> MTLFunction {
    guard let base = lib.makeFunction(name: name) else { throw NSError(domain:"missing function",code:1) }
    print("function=\(name), constants=\(base.functionConstantsDictionary.map{$0.key} ?? [])")
    let vals = MTLFunctionConstantValues()
    var toggle = false
    for (key,k) in base.functionConstantsDictionary {
        vals.setConstantValue(&toggle, type: .bool, index:k.index)
        print("  constant \(key), index \(k.index): false")
    }
    return try lib.makeFunction(name: name, constantValues: vals)
}
do {
    let v = try specialized("Flyover::splat_vertex")
    let f = try specialized("Flyover::splat_fragment")
    let desc = MTLRenderPipelineDescriptor()
    desc.vertexFunction=v; desc.fragmentFunction=f
    desc.colorAttachments[0].pixelFormat = .rgba16Float
    desc.depthAttachmentPixelFormat = .depth32Float
    var refl: MTLRenderPipelineReflection?
    let pipe = try gpu.makeRenderPipelineState(descriptor:desc,options:.bindingInfo,reflection:&refl)
    print("PIPELINE_OK buffers=\(pipe.maxTotalThreadsPerThreadgroup)")
    print("Reflection: \(String(describing: refl))")
} catch { print("PIPELINE_ERROR: \(error)") }
