import Foundation
import MetalKit
import ImageIO
import UniformTypeIdentifiers

@main struct GPUChecks {
    static func main() throws {
        guard let device = MTLCreateSystemDefaultDevice() else {
            print("SKIP: runner has no Metal device; simulator/device builds still required")
            return
        }
        let width = 4096, height = 2048
        let bytes = Data(repeating:127,count:width*height*4)
        let provider = CGDataProvider(data:bytes as CFData)!
        let image = CGImage(width:width,height:height,bitsPerComponent:8,bitsPerPixel:32,
            bytesPerRow:width*4,space:CGColorSpaceCreateDeviceRGB(),
            bitmapInfo:CGBitmapInfo(rawValue:CGImageAlphaInfo.noneSkipLast.rawValue),
            provider:provider,decode:nil,shouldInterpolate:true,intent:.defaultIntent)!
        let png = NSMutableData()
        let destination = CGImageDestinationCreateWithData(png,UTType.png.identifier as CFString,1,nil)!
        CGImageDestinationAddImage(destination,image,nil)
        precondition(CGImageDestinationFinalize(destination))
        let origin = GeoOrigin(latitude:35.6586,longitude:139.7454)
        let json: [String:Any] = ["transform":["matrixR3x3":[1,0,0,0,1,0,0,0,1],
            "ecefTranslation":[origin.ecef.x,origin.ecef.y,origin.ecef.z]],
            "min":[0,0,0],"max":[1,1,1],"meshTriangles":1,"splatVertices":0,"vertexCount":1]
        let decoded = ["json":try JSONSerialization.data(withJSONObject:json),
            "vertices":Data(count:32),"indices":Data(count:12),"splats":Data(),"atlas":png as Data]
        let factory = GPUFactory(device:device)
        let preview = try factory.prepare(key:TileKey(z:20,x:1,y:1),decoded:decoded,origin:origin,textureLimit:1024)
        precondition(preview.sourcePixels == 4096 && preview.atlas!.width == 1024)
        precondition(preview.atlas!.mipmapLevelCount > 1)
        let earlyAtlas = try factory.prepareAtlas(image:decoded["atlas"]!,limit:256)!
        let earlyTile = try factory.prepare(key:TileKey(z:16,x:1,y:1),decoded:decoded,origin:origin,
            textureLimit:256,preparedAtlas:earlyAtlas)
        precondition(earlyTile.atlas === earlyAtlas.texture && earlyTile.sourcePixels == 4096)
        let original = try factory.texture(image:decoded["atlas"]!,limit:4096)
        let refined = preview.replacing(atlas:original,limit:4096)
        precondition(refined.atlas!.width == 4096 && refined.atlas!.height == 2048)
        precondition(preview.vertices === refined.vertices && preview.indices === refined.indices)
        precondition(preview.atlas!.width == 1024, "Previous frame's atlas stays alive")
        precondition(refined.cost == refined.geometryCost+original.allocatedSize)
        let reduced = try factory.reducedTexture(original,limit:512)
        precondition(reduced.width == 512 && reduced.height == 256 && reduced.mipmapLevelCount == 10)
        precondition(reduced.allocatedSize < original.allocatedSize)
        let oddDescriptor = MTLTextureDescriptor.texture2DDescriptor(pixelFormat:.rgba8Unorm,
            width:896,height:832,mipmapped:true)
        oddDescriptor.storageMode = .private; oddDescriptor.usage = .shaderRead
        let oddAtlas = device.makeTexture(descriptor:oddDescriptor)!
        let oddReduced = try factory.reducedTexture(oddAtlas,limit:512)
        let oddReplacement = preview.replacing(atlas:oddReduced,limit:512)
        precondition(oddReduced.width == 448 && oddReduced.height == 416)
        precondition(oddReplacement.textureLimit == 448, "Record the actual mip size, not the requested cap")
        precondition(StreamingPolicy.textureTarget(zoom:20,source:896,current:oddReplacement.textureLimit,
            headroom:192*1048576,constrained:false,pressure:true,upgradeAllowed:true) == 448)
        try checkHorizontalClipping(device)
        print("PASS: full resolution, preview, retained geometry, mip reduction, allocation cost, horizontal-only shader clipping")
    }

    static func checkHorizontalClipping(_ device: MTLDevice) throws {
        let source = URL(fileURLWithPath:#filePath).deletingLastPathComponent().deletingLastPathComponent()
            .appendingPathComponent("App/Shaders.metal")
        let library = try device.makeLibrary(source:String(contentsOf:source,encoding:.utf8),options:nil)
        let descriptor = MTLRenderPipelineDescriptor()
        descriptor.vertexFunction = library.makeFunction(name:"meshVertex")
        descriptor.fragmentFunction = library.makeFunction(name:"meshFragment")
        descriptor.colorAttachments[0].pixelFormat = .rgba8Unorm
        descriptor.depthAttachmentPixelFormat = .depth32Float
        let meshPipeline = try device.makeRenderPipelineState(descriptor:descriptor)
        descriptor.vertexFunction = library.makeFunction(name:"splatVertex")
        descriptor.fragmentFunction = library.makeFunction(name:"splatFragment")
        let splatPipeline = try device.makeRenderPipelineState(descriptor:descriptor)
        let queue = device.makeCommandQueue()!
        let atlasDescriptor = MTLTextureDescriptor.texture2DDescriptor(pixelFormat:.rgba8Unorm,width:1,height:1,mipmapped:false)
        atlasDescriptor.storageMode = .shared; atlasDescriptor.usage = .shaderRead
        let atlas = device.makeTexture(descriptor:atlasDescriptor)!
        let red: [UInt8] = [255,0,0,255]
        red.withUnsafeBytes { atlas.replace(region:MTLRegionMake2D(0,0,1,1),mipmapLevel:0,
            withBytes:$0.baseAddress!,bytesPerRow:4) }
        struct TestFrame {
            var viewProjection: simd_float4x4
            var eye,forward,right,up,parameters: SIMD4<Float>
        }
        for (splat,pipeline) in [(false,meshPipeline),(true,splatPipeline)] {
          for altitude in [10000.0,20000.0] {
            for (east,masked) in [(0.0,false),(300.0,false),(0.0,true)] {
                var camera = CameraState(); camera.eye = SIMD3(0,altitude,0); camera.pitch = -.pi/2; camera.aspect = 1
                var frame = TestFrame(viewProjection:camera.projection(far:.infinity)*camera.view,
                    eye:SIMD4(SIMD3<Float>(camera.eye),1),forward:.zero,right:.zero,up:.zero,parameters:SIMD4(1,1,0,150))
                var model = matrix_identity_float4x4
                let positions: [[Float]] = [[Float(east-60),0,-60],[Float(east+60),0,-60],[Float(east),0,60]]
                var vertices: [Float] = []
                for (index,position) in positions.enumerated() {
                    vertices += position
                    if splat {
                        vertices += [1,0,0,1]
                        vertices += (0..<3).map { $0 == index ? Float(1) : Float(0) }
                    } else { vertices += [0,1,0,0.5,0.5] }
                }
                let colorDescriptor = MTLTextureDescriptor.texture2DDescriptor(pixelFormat:.rgba8Unorm,width:1024,height:1024,mipmapped:false)
                colorDescriptor.storageMode = .shared; colorDescriptor.usage = .renderTarget
                let color = device.makeTexture(descriptor:colorDescriptor)!
                let depthDescriptor = MTLTextureDescriptor.texture2DDescriptor(pixelFormat:.depth32Float,width:1024,height:1024,mipmapped:false)
                depthDescriptor.storageMode = .private; depthDescriptor.usage = .renderTarget
                let pass = MTLRenderPassDescriptor()
                pass.colorAttachments[0].texture = color; pass.colorAttachments[0].loadAction = .clear
                pass.colorAttachments[0].storeAction = .store; pass.colorAttachments[0].clearColor = MTLClearColorMake(0,0,0,1)
                pass.depthAttachment.texture = device.makeTexture(descriptor:depthDescriptor)
                pass.depthAttachment.loadAction = .clear; pass.depthAttachment.clearDepth = 1
                let command = queue.makeCommandBuffer()!, encoder = command.makeRenderCommandEncoder(descriptor:pass)!
                encoder.setRenderPipelineState(pipeline); encoder.setCullMode(.none)
                vertices.withUnsafeBytes { encoder.setVertexBytes($0.baseAddress!,length:$0.count,index:0) }
                encoder.setVertexBytes(&frame,length:MemoryLayout<TestFrame>.stride,index:1)
                encoder.setVertexBytes(&model,length:64,index:2)
                encoder.setFragmentBytes(&frame,length:MemoryLayout<TestFrame>.stride,index:1)
                var coverage = [SIMD4<Float>](repeating:.zero,count:StreamingPolicy.maximumCoverageRectangles+1)
                if masked {
                    coverage[0].x = Float(StreamingPolicy.maximumCoverageRectangles)
                    for index in 1..<coverage.count { coverage[index] = SIMD4(1000,1100,1000,1100) }
                    coverage[StreamingPolicy.maximumCoverageRectangles] = SIMD4(-100,100,-100,100)
                }
                let masks = coverage.withUnsafeBytes { device.makeBuffer(bytes:$0.baseAddress!,length:$0.count,options:.storageModeShared)! }
                encoder.setFragmentBuffer(masks,offset:0,index:3)
                encoder.setFragmentTexture(atlas,index:0)
                encoder.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:3)
                encoder.endEncoding(); command.commit(); command.waitUntilCompleted()
                precondition(command.status == .completed)
                var pixels = [UInt8](repeating:0,count:1024*1024*4)
                pixels.withUnsafeMutableBytes { color.getBytes($0.baseAddress!,bytesPerRow:1024*4,
                    from:MTLRegionMake2D(0,0,1024,1024),mipmapLevel:0) }
                let colored = stride(from:0,to:pixels.count,by:4).filter{pixels[$0]>128}.count
                precondition(east == 0 && !masked ? colored > 0 : colored == 0,
                    "Horizontal clipping and the final child coverage mask must discard pixels at any altitude")
            }
          }
        }
    }
}
