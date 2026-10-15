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
    let emptyCoverage: MTLBuffer
    let inFlight = DispatchSemaphore(value:3)
    weak var world: ExplorerModel?
    var lastTime = CACurrentMediaTime()
    var frameTime = 0.0
    var frameCount = 0
    var frameID = 0
    var skippedGPU = 0
    var skippedDrawable = 0
    var lastReport = CACurrentMediaTime()
    var intervalFrames = 0
    var maximumFrameMS = 0.0
    var totalCPUms = 0.0
    var lastSubmitted = Set<TileKey>()
    let started = CACurrentMediaTime()
    init(device: MTLDevice) throws {
        self.device = device
        guard let queue = device.makeCommandQueue(), let library = device.makeDefaultLibrary() else { throw StreamError.gpuBudget }
        self.queue = queue
        guard let emptyCoverage = device.makeBuffer(length:(StreamingPolicy.maximumCoverageRectangles+1)*16,
            options:.storageModeShared) else { throw StreamError.gpuBudget }
        emptyCoverage.contents().initializeMemory(as:UInt8.self,repeating:0,count:emptyCoverage.length)
        self.emptyCoverage = emptyCoverage
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
        DiagnosticsLog.shared.event("render.initialized",fields:["device":device.name,"in_flight_limit":3])
    }
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        world?.camera.aspect = size.width/max(1,size.height)
        DiagnosticsLog.shared.event("render.resize",fields:["width":size.width,"height":size.height])
    }
    func draw(in view: MTKView) {
        let now = CACurrentMediaTime(), elapsed = now-lastTime
        let dt = min(0.05,elapsed)
        lastTime = now
        guard let world, world.active else { return }
        world.step(dt:dt,now:now)
        frameID += 1
        let currentFrame = frameID, cpuStart = DiagnosticsLog.now
        maximumFrameMS = max(maximumFrameMS,elapsed*1000)
        let report = now-lastReport >= 1
        if report {
            DiagnosticsLog.shared.event("render.interval",fields:["frame":currentFrame,"frames_submitted":intervalFrames,
                "interval_s":now-lastReport,"gpu_backpressure_skips":skippedGPU,"drawable_skips":skippedDrawable,
                "max_frame_interval_ms":maximumFrameMS,"cpu_total_ms":totalCPUms])
            lastReport = now; intervalFrames = 0; skippedGPU = 0; skippedDrawable = 0; maximumFrameMS = 0; totalCPUms = 0
        }
        // Do not block the main thread if the GPU is behind.
        guard inFlight.wait(timeout:.now()) == .success else { skippedGPU += 1; return }
        guard let drawable = view.currentDrawable, let pass = view.currentRenderPassDescriptor,
              let command = queue.makeCommandBuffer(), let encoder = command.makeRenderCommandEncoder(descriptor:pass) else {
            skippedDrawable += 1; inFlight.signal(); return
        }
        let camera = world.camera
        let vp = camera.projection(far:.infinity)*camera.view
        var frame = FrameUniforms(viewProjection:vp,eye:SIMD4(SIMD3<Float>(camera.eye),1),
            forward:SIMD4(SIMD3<Float>(camera.forward),0),right:SIMD4(SIMD3<Float>(camera.right),0),
            up:SIMD4(SIMD3<Float>(simd_cross(camera.right,camera.forward)),0),
            parameters:SIMD4(Float(camera.aspect),Float(tan(camera.fov/2)),Float(now-started),Float(world.renderDistance)))
        encoder.setVertexBytes(&frame,length:MemoryLayout<FrameUniforms>.stride,index:1)
        encoder.setFragmentBytes(&frame,length:MemoryLayout<FrameUniforms>.stride,index:1)
        encoder.setCullMode(.none)
        encoder.setRenderPipelineState(skyPipeline); encoder.setDepthStencilState(skyDepth)
        encoder.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:3)
        let selection = world.selection()
        let tiles = selection.tiles.filter {
            RenderVisibility.visible(TileSphere(center:$0.center,radius:$0.radius),viewProjection:vp,
                eye:SIMD3<Float>(camera.eye),distance:Float(world.renderDistance))
        }
        var coverageBuffers: [TileKey:MTLBuffer] = [:]
        for (key,mask) in selection.masks {
            precondition(mask.count <= StreamingPolicy.maximumCoverageRectangles+1)
            let padded = mask+Array(repeating:SIMD4<Float>.zero,
                count:StreamingPolicy.maximumCoverageRectangles+1-mask.count)
            let buffer = padded.withUnsafeBytes { device.makeBuffer(bytes:$0.baseAddress!,length:$0.count,options:.storageModeShared) }
            guard let buffer else { encoder.endEncoding(); inFlight.signal(); return }
            coverageBuffers[key] = buffer
        }
        func coverage(_ tile: GPUTile) {
            encoder.setFragmentBuffer(coverageBuffers[tile.key.horizontal] ?? emptyCoverage,offset:0,index:3)
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
        encoder.endEncoding(); command.present(drawable)
        let firstDraws = world.didSubmitTiles(tiles,frame:currentFrame)
        if !firstDraws.isEmpty {
            #if !targetEnvironment(simulator)
            drawable.addPresentedHandler { presented in
                let now = DiagnosticsLog.now
                for timing in firstDraws {
                    let latency = (now-timing.neededAt)*1000
                    DiagnosticsLog.shared.event("render.tile_first_presented",tile:timing.key.name,trace:timing.trace,
                        fields:["frame":currentFrame,"needed_to_presented_ms":latency,
                                "lightweight":timing.key.z == StreamingPolicy.coarseZoom,"deadline_ms":100,
                                "deadline_met":latency <= 100,"presented_time_s":presented.presentedTime])
                }
            }
            #else
            command.addCompletedHandler { completed in
                guard completed.status == .completed else { return }
                let now = DiagnosticsLog.now
                for timing in firstDraws {
                    let latency = (now-timing.neededAt)*1000
                    DiagnosticsLog.shared.event("render.tile_first_completed",tile:timing.key.name,trace:timing.trace,
                        fields:["frame":currentFrame,"needed_to_completed_ms":latency,
                                "lightweight":timing.key.z == StreamingPolicy.coarseZoom,"deadline_ms":100,"deadline_met":latency <= 100])
                }
            }
            #endif
        }
        let submittedAt = DiagnosticsLog.now
        let semaphore = inFlight
        command.addCompletedHandler { completed in
            semaphore.signal()
            if report || completed.status == .error {
                var fields: [String:Any] = ["frame":currentFrame,"status":completed.status.rawValue,
                    "submit_to_complete_ms":DiagnosticsLog.milliseconds(since:submittedAt),
                    "gpu_ms":max(0,completed.gpuEndTime-completed.gpuStartTime)*1000]
                if let error = completed.error { fields.merge(DiagnosticsLog.errorFields(error),uniquingKeysWith:{$1}) }
                DiagnosticsLog.shared.event("render.gpu_complete",fields:fields)
            }
        }
        command.commit(); intervalFrames += 1
        totalCPUms += DiagnosticsLog.milliseconds(since:cpuStart)
        let submitted = Set(tiles.map(\.key))
        if submitted != lastSubmitted {
            let appeared = submitted.subtracting(lastSubmitted).sorted().map(\.name)
            let disappeared = lastSubmitted.subtracting(submitted).sorted().map(\.name)
            // Chunk changes so even a relocation cannot exceed a single record's bound.
            for (kind,keys) in [("appeared",appeared),("disappeared",disappeared)] {
                for offset in stride(from:0,to:keys.count,by:128) {
                    DiagnosticsLog.shared.event("render.visibility",fields:["frame":currentFrame,"change":kind,
                        "tiles":Array(keys[offset..<min(offset+128,keys.count)])])
                }
            }
            lastSubmitted = submitted
        }
        if report {
            DiagnosticsLog.shared.event("render.frame",fields:["frame":currentFrame,"selected_tiles":selection.tiles.count,
                "frustum_culled_tiles":selection.tiles.count-tiles.count,"submitted_tiles":tiles.count,
                "triangles":tiles.reduce(0){$0+$1.triangles},"splat_vertices":tiles.reduce(0){$0+$1.splatVertices},
                "coverage_masks":selection.masks.count,"drawable_width":view.drawableSize.width,
                "drawable_height":view.drawableSize.height,"target_fps":view.preferredFramesPerSecond,
                "camera":world.cameraLogFields()])
        }
        frameTime += elapsed; frameCount += 1
        if frameTime >= 1 {
            world.fps = Double(frameCount)/frameTime
            world.drawnTiles = tiles.count
            frameTime = 0; frameCount = 0
        }
    }
}
