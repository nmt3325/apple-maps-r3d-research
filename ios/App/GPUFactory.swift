import MetalKit
import ImageIO
import simd

struct GPUTile: @unchecked Sendable {
    let key: TileKey
    let vertices: MTLBuffer?
    let indices: MTLBuffer?
    let splats: MTLBuffer?
    let atlas: MTLTexture?
    let model: simd_float4x4
    let center: SIMD3<Float>
    let radius: Float
    let triangles: Int
    let splatVertices: Int
    let cost: Int
    let sourcePixels: Int
    let textureLimit: Int
    var geometryCost: Int { (vertices?.length ?? 0)+(indices?.length ?? 0)+(splats?.length ?? 0) }
    func replacing(atlas: MTLTexture, limit: Int) -> GPUTile {
        GPUTile(key:key,vertices:vertices,indices:indices,splats:splats,atlas:atlas,model:model,
            center:center,radius:radius,triangles:triangles,splatVertices:splatVertices,
            cost:geometryCost+atlas.allocatedSize,sourcePixels:sourcePixels,textureLimit:limit)
    }
}

final class GPUFactory: @unchecked Sendable {
    let device: MTLDevice
    init(device: MTLDevice) { self.device = device }
    func texture(image: Data, limit: Int) throws -> MTLTexture {
        try Task.checkCancellation()
        guard let source = CGImageSourceCreateWithData(image as CFData,nil),
              let bitmap = CGImageSourceCreateThumbnailAtIndex(source,0,[
                kCGImageSourceCreateThumbnailFromImageAlways:true,
                kCGImageSourceThumbnailMaxPixelSize:limit,
                kCGImageSourceShouldCacheImmediately:true] as CFDictionary) else { throw StreamError.invalidGeometry }
        return try MTKTextureLoader(device:device).newTexture(cgImage:bitmap,options:[
            .SRGB:true,.generateMipmaps:true,.textureStorageMode:MTLStorageMode.private.rawValue])
    }
    // Reuse resident mips under pressure, even after the CPU cache entry expired.
    func reducedTexture(_ source: MTLTexture, limit: Int) throws -> MTLTexture {
        var level = 0
        while max(source.width>>level,source.height>>level) > limit && level+1 < source.mipmapLevelCount { level += 1 }
        let descriptor = MTLTextureDescriptor.texture2DDescriptor(pixelFormat:source.pixelFormat,
            width:max(1,source.width>>level),height:max(1,source.height>>level),mipmapped:true)
        descriptor.storageMode = .private; descriptor.usage = .shaderRead
        guard let target = device.makeTexture(descriptor:descriptor), let queue = device.makeCommandQueue(),
              let command = queue.makeCommandBuffer(), let blit = command.makeBlitCommandEncoder() else { throw StreamError.gpuBudget }
        blit.copy(from:source,sourceSlice:0,sourceLevel:level,to:target,destinationSlice:0,
            destinationLevel:0,sliceCount:1,levelCount:target.mipmapLevelCount)
        blit.endEncoding(); command.commit(); command.waitUntilCompleted()
        guard command.status == .completed else { throw StreamError.gpuBudget }
        return target
    }
    func prepare(key: TileKey, decoded: [String:Data], origin: GeoOrigin, textureLimit: Int) throws -> GPUTile {
        guard let json = decoded["json"], let vb = decoded["vertices"], let ib = decoded["indices"],
              let sb = decoded["splats"], let image = decoded["atlas"] else { throw StreamError.invalidGeometry }
        let info = try JSONDecoder().decode(TileInfo.self,from:json)
        guard vb.count == info.vertexCount*32, ib.count == info.meshTriangles*12,
              sb.count == info.splatVertices*40, info.transform.matrixR3x3.count == 9,
              info.transform.ecefTranslation.count == 3, info.min.count == 3, info.max.count == 3,
              vb.count+ib.count+sb.count <= 64*1024*1024 else { throw StreamError.invalidGeometry }
        func buffer(_ data: Data) throws -> MTLBuffer? {
            guard !data.isEmpty else { return nil }
            let result = data.withUnsafeBytes { bytes in device.makeBuffer(bytes:bytes.baseAddress!,length:data.count,options:.storageModeShared) }
            guard let result else { throw StreamError.gpuBudget }
            return result
        }
        let vertices = try buffer(vb), indices = try buffer(ib), splats = try buffer(sb)
        var texture: MTLTexture?
        var sourcePixels = 0
        if info.meshTriangles > 0 {
            guard let source = CGImageSourceCreateWithData(image as CFData,nil),
                  let properties = CGImageSourceCopyPropertiesAtIndex(source,0,nil) as? [CFString:Any],
                  let width = properties[kCGImagePropertyPixelWidth] as? Int,
                  let height = properties[kCGImagePropertyPixelHeight] as? Int else { throw StreamError.invalidGeometry }
            sourcePixels = max(width,height)
            texture = try self.texture(image:image,limit:textureLimit)
        }
        let model = info.model(origin:origin)
        let lower = SIMD3<Float>(Float(info.min[0]),Float(info.min[1]),Float(info.min[2]))
        let upper = SIMD3<Float>(Float(info.max[0]),Float(info.max[1]),Float(info.max[2]))
        let center = model*SIMD4((lower+upper)/2,1)
        let textureBytes = texture?.allocatedSize ?? 0
        return GPUTile(key:key,vertices:vertices,indices:indices,splats:splats,atlas:texture,
            model:model,center:SIMD3(center.x,center.y,center.z),radius:simd_length(upper-lower)/2,
            triangles:info.meshTriangles,splatVertices:info.splatVertices,cost:vb.count+ib.count+sb.count+textureBytes,
            sourcePixels:sourcePixels,textureLimit:min(sourcePixels,textureLimit))
    }
}

