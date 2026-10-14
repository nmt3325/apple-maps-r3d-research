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
        print("PASS: full resolution, preview, retained geometry, atomic atlas replacement, resident mip reduction, allocation cost")
    }
}
