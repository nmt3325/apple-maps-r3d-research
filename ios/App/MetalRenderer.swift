import MetalKit
import simd

struct FrameUniforms {
    var viewProjection: simd_float4x4
    var eye: SIMD4<Float>
    var forward: SIMD4<Float>
    var right: SIMD4<Float>
    var up: SIMD4<Float>
    var parameters: SIMD4<Float>
}

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
}

final class GPUFactory: @unchecked Sendable {
    let device: MTLDevice
    init(device: MTLDevice) { self.device = device }
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
        if info.meshTriangles > 0 {
            guard let source = CGImageSourceCreateWithData(image as CFData,nil),
                  let bitmap = CGImageSourceCreateThumbnailAtIndex(source,0,[
                    kCGImageSourceCreateThumbnailFromImageAlways:true,
                    kCGImageSourceThumbnailMaxPixelSize:textureLimit,
                    kCGImageSourceShouldCacheImmediately:true] as CFDictionary) else { throw StreamError.invalidGeometry }
            texture = try MTKTextureLoader(device:device).newTexture(cgImage:bitmap,options:[
                .SRGB:true,.generateMipmaps:true,.textureStorageMode:MTLStorageMode.private.rawValue])
        }
        let model = info.model(origin:origin)
        let lower = SIMD3<Float>(Float(info.min[0]),Float(info.min[1]),Float(info.min[2]))
        let upper = SIMD3<Float>(Float(info.max[0]),Float(info.max[1]),Float(info.max[2]))
        let center = model*SIMD4((lower+upper)/2,1)
        let textureBytes = texture.map { Int(Double($0.width*$0.height*4)*1.34) } ?? 0
        return GPUTile(key:key,vertices:vertices,indices:indices,splats:splats,atlas:texture,
            model:model,center:SIMD3(center.x,center.y,center.z),radius:simd_length(upper-lower)/2,
            triangles:info.meshTriangles,splatVertices:info.splatVertices,cost:vb.count+ib.count+sb.count+textureBytes)
    }
}

@MainActor
final class MetalRenderer: NSObject, MTKViewDelegate {
    let device: MTLDevice
    let queue: MTLCommandQueue
    let meshPipeline: MTLRenderPipelineState
    let splatPipeline: MTLRenderPipelineState
    let skyPipeline: MTLRenderPipelineState
    let solidDepth: MTLDepthStencilState
    let transparentDepth: MTLDepthStencilState
    let skyDepth: MTLDepthStencilState
    let inFlight = DispatchSemaphore(value:3)
    weak var world: ExplorerModel?
    var lastTime = CACurrentMediaTime()
    var frameTime = 0.0
    var frameCount = 0
    let started = CACurrentMediaTime()
    init(device: MTLDevice) throws {
        self.device = device
        guard let queue = device.makeCommandQueue(), let library = device.makeDefaultLibrary() else { throw StreamError.gpuBudget }
        self.queue = queue
        func pipeline(_ vertex: String, _ fragment: String, blend: Bool = false) throws -> MTLRenderPipelineState {
            let descriptor = MTLRenderPipelineDescriptor()
            descriptor.vertexFunction = library.makeFunction(name:vertex)
            descriptor.fragmentFunction = library.makeFunction(name:fragment)
            descriptor.colorAttachments[0].pixelFormat = .bgra8Unorm_srgb
            descriptor.depthAttachmentPixelFormat = .depth32Float
            descriptor.colorAttachments[0].isBlendingEnabled = blend
            if blend {
                descriptor.colorAttachments[0].sourceRGBBlendFactor = .sourceAlpha
                descriptor.colorAttachments[0].destinationRGBBlendFactor = .oneMinusSourceAlpha
                descriptor.colorAttachments[0].sourceAlphaBlendFactor = .one
                descriptor.colorAttachments[0].destinationAlphaBlendFactor = .oneMinusSourceAlpha
            }
            return try device.makeRenderPipelineState(descriptor:descriptor)
        }
        meshPipeline = try pipeline("meshVertex","meshFragment")
        splatPipeline = try pipeline("splatVertex","splatFragment",blend:true)
        skyPipeline = try pipeline("skyVertex","skyFragment")
        func depth(_ compare: MTLCompareFunction, write: Bool) -> MTLDepthStencilState {
            let descriptor = MTLDepthStencilDescriptor()
            descriptor.depthCompareFunction = compare; descriptor.isDepthWriteEnabled = write
            return device.makeDepthStencilState(descriptor:descriptor)!
        }
        solidDepth = depth(.lessEqual,write:true)
        transparentDepth = depth(.lessEqual,write:false)
        skyDepth = depth(.always,write:false)
        super.init()
    }
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        world?.camera.aspect = size.width/max(1,size.height)
    }
    func draw(in view: MTKView) {
        let now = CACurrentMediaTime(), elapsed = now-lastTime
        let dt = min(0.05,elapsed)
        lastTime = now
        guard let world, world.active else { return }
        world.step(dt:dt,now:now)
        // Do not block the main thread if the GPU is behind.
        guard inFlight.wait(timeout:.now()) == .success else { return }
        guard let drawable = view.currentDrawable, let pass = view.currentRenderPassDescriptor,
              let command = queue.makeCommandBuffer(), let encoder = command.makeRenderCommandEncoder(descriptor:pass) else {
            inFlight.signal(); return
        }
        let semaphore = inFlight
        command.addCompletedHandler { _ in semaphore.signal() }
        let camera = world.camera
        let vp = camera.projection(far:world.viewDistance)*camera.view
        var frame = FrameUniforms(viewProjection:vp,eye:SIMD4(SIMD3<Float>(camera.eye),1),
            forward:SIMD4(SIMD3<Float>(camera.forward),0),right:SIMD4(SIMD3<Float>(camera.right),0),
            up:SIMD4(SIMD3<Float>(simd_cross(camera.right,camera.forward)),0),
            parameters:SIMD4(Float(camera.aspect),Float(tan(camera.fov/2)),Float(now-started),Float(world.viewDistance)))
        encoder.setVertexBytes(&frame,length:MemoryLayout<FrameUniforms>.stride,index:1)
        encoder.setFragmentBytes(&frame,length:MemoryLayout<FrameUniforms>.stride,index:1)
        encoder.setCullMode(.none)
        encoder.setRenderPipelineState(skyPipeline); encoder.setDepthStencilState(skyDepth)
        encoder.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:3)
        let selection = world.selection()
        let tiles = selection.tiles.filter { Self.visible($0,viewProjection:vp) }
        func coverage(_ tile: GPUTile) {
            // Metal reads at most 16 child rectangles under a z18 root.
            let mask = selection.masks[tile.key.horizontal] ?? [SIMD4<Float>.zero]
            let padded = mask+Array(repeating:SIMD4<Float>.zero,count:max(0,17-mask.count))
            padded.withUnsafeBytes { bytes in encoder.setFragmentBytes(bytes.baseAddress!,length:bytes.count,index:3) }
        }
        encoder.setRenderPipelineState(meshPipeline); encoder.setDepthStencilState(solidDepth)
        for tile in tiles where tile.triangles > 0 {
            guard let vertices = tile.vertices, let indices = tile.indices, let texture = tile.atlas else { continue }
            coverage(tile)
            var model = tile.model
            encoder.setVertexBytes(&model,length:64,index:2)
            encoder.setVertexBuffer(vertices,offset:0,index:0)
            encoder.setFragmentTexture(texture,index:0)
            encoder.drawIndexedPrimitives(type:.triangle,indexCount:tile.triangles*3,indexType:.uint32,indexBuffer:indices,indexBufferOffset:0)
        }
        encoder.setRenderPipelineState(splatPipeline); encoder.setDepthStencilState(transparentDepth)
        let eye = SIMD3<Float>(camera.eye)
        for tile in tiles.sorted(by:{simd_distance_squared($0.center,eye)>simd_distance_squared($1.center,eye)}) where tile.splatVertices > 0 {
            guard let vertices = tile.splats else { continue }
            coverage(tile)
            var model = tile.model
            encoder.setVertexBytes(&model,length:64,index:2)
            encoder.setVertexBuffer(vertices,offset:0,index:0)
            encoder.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:tile.splatVertices)
        }
        encoder.endEncoding(); command.present(drawable); command.commit()
        frameTime += elapsed; frameCount += 1
        if frameTime >= 1 {
            world.fps = Double(frameCount)/frameTime
            world.drawnTiles = tiles.count
            frameTime = 0; frameCount = 0
        }
    }
    static func visible(_ tile: GPUTile, viewProjection m: simd_float4x4) -> Bool {
        visible(TileSphere(center:tile.center,radius:tile.radius),viewProjection:m)
    }
    static func visible(_ tile: TileSphere, viewProjection m: simd_float4x4) -> Bool {
        let r0 = SIMD4(m[0,0],m[1,0],m[2,0],m[3,0])
        let r1 = SIMD4(m[0,1],m[1,1],m[2,1],m[3,1])
        let r2 = SIMD4(m[0,2],m[1,2],m[2,2],m[3,2])
        let r3 = SIMD4(m[0,3],m[1,3],m[2,3],m[3,3])
        for p in [r3+r0,r3-r0,r3+r1,r3-r1,r2,r3-r2] {
            if simd_dot(p,SIMD4(tile.center,1)) < -tile.radius*simd_length(SIMD3(p.x,p.y,p.z)) { return false }
        }
        return true
    }
}
