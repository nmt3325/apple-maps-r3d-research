import SwiftUI
import MetalKit

@MainActor
final class ExplorerModel: ObservableObject {
    @Published var message = "Apple Maps に接続中"
    @Published var fps = 0.0
    @Published var drawnTiles = 0
    @Published var residentTiles = 0
    @Published var memoryMB = 0
    @Published var requests = 0
    @Published var completed = 0
    @Published var quality = 1
    @Published var configured = false
    @Published var paused = false { didSet { if paused { stopNavigation() } } }
    @Published var viewDistance = 350.0
    @Published var locationLabel = "東京タワー"
    @Published var rendererError: String?
    var camera = CameraState()
    var origin = GeoOrigin(latitude:35.6586,longitude:139.7454)
    var navigation = CameraNavigation()
    var elevation = 0.0
    @Published var elevationSpeed = 35.0
    @Published var active = true
    var device: MTLDevice?
    var factory: GPUFactory?
    let decoder = TileDecoder()
    var client: AppleMapsClient?
    var tiles: [TileKey:GPUTile] = [:]
    var knownBounds: [TileKey:TileSphere] = [:]
    var accessed: [TileKey:Double] = [:]
    var empty: [TileKey:Date] = [:]
    var failures: [TileKey:Date] = [:]
    var indices: [TileKey:HeightIndex] = [:]
    var indexAccess: [TileKey:Double] = [:]
    var expanded: [TileKey:[TileKey]] = [:]
    var desired: [TileKey] = []
    var roots = Set<TileKey>()
    var needed = Set<TileKey>()
    var pending: [TileKey:Task<Void,Never>] = [:]
    var fetching = Set<TileKey>()
    let processing = PipelineSlots(limit:2)
    var queue: [TileKey] = []
    var generation = 0
    var lastPlan = 0.0
    var lastStatistics = 0.0
    var authFailed = false
    var memoryConstrainedUntil = 0.0
    var budget: Int { quality == 0 || CACurrentMediaTime() < memoryConstrainedUntil ? 96*1024*1024 : 192*1024*1024 }
    var textureLimit: Int { budget <= 96*1024*1024 ? 512 : 1024 }

    init() {
        device = MTLCreateSystemDefaultDevice()
        if let device { factory = GPUFactory(device:device) }
        else { rendererError = "この端末では Metal を使用できません。" }
        if let config = CredentialStore.load() { configure(config) }
        else { message = StreamError.configuration.localizedDescription }
        #if DEBUG
        if CommandLine.arguments.contains("-streaming-validation") {
            Task { await ValidationScenario.run(self) }
        }
        #endif
    }
    func configure(_ config: FetchConfiguration) {
        invalidate()
        client = AppleMapsClient(config); configured = true; authFailed = false
        message = "Apple Maps から 3D データを直接取得中"
    }
    func importConfiguration(_ url: URL) {
        let access = url.startAccessingSecurityScopedResource()
        defer { if access { url.stopAccessingSecurityScopedResource() } }
        do {
            let data = try Data(contentsOf:url)
            try CredentialStore.save(data)
            let config = try JSONDecoder().decode(FetchConfiguration.self,from:data)
            configure(config)
        } catch { message = "取得設定を読み込めませんでした。形式を確認してください。" }
    }
    func invalidate() {
        generation += 1
        pending.values.forEach{$0.cancel()}; pending.removeAll(); fetching.removeAll(); queue.removeAll()
        tiles.removeAll(); knownBounds.removeAll(); accessed.removeAll(); empty.removeAll(); failures.removeAll()
        indices.removeAll(); indexAccess.removeAll(); expanded.removeAll()
        desired.removeAll(); roots.removeAll(); needed.removeAll(); lastPlan = 0
    }
    func relocate(latitude: Double, longitude: Double, label: String) {
        guard latitude.isFinite, longitude.isFinite, abs(latitude) <= 85.05112878, abs(longitude) <= 180 else {
            message = "緯度・経度の範囲を確認してください。"; return
        }
        stopNavigation(); invalidate(); origin = GeoOrigin(latitude:latitude,longitude:longitude)
        camera.eye = SIMD3(0,100,160); camera.yaw = 0; camera.pitch = -0.45
        locationLabel = label; completed = 0
    }
    func step(dt: Double, now: Double) {
        if !paused {
            navigation.step(dt:dt,camera:&camera)
            camera.eye.y = max(2,camera.eye.y+elevation*elevationSpeed*dt)
        }
        if simd_length(SIMD2(camera.eye.x,camera.eye.z)) > 3000 {
            let coordinate = origin.coordinate(east:camera.eye.x,south:camera.eye.z)
            let oldEye = camera.eye, yaw = camera.yaw, pitch = camera.pitch
            let oldNavigation = navigation, oldElevation = elevation
            relocate(latitude:coordinate.latitude,longitude:coordinate.longitude,label:locationLabel)
            camera.eye = SIMD3(0,oldEye.y,0); camera.yaw = yaw; camera.pitch = pitch
            navigation = oldNavigation; navigation.rebase(by:SIMD3(oldEye.x,0,oldEye.z))
            elevation = oldElevation
        }
        if now-lastPlan > 0.25 && configured && !paused && !authFailed {
            lastPlan = now; updatePlan(now:now)
        }
        if now-lastStatistics > 1 {
            lastStatistics = now
            residentTiles = tiles.count
            memoryMB = tiles.values.reduce(0){$0+$1.cost}/1024/1024
            requests = pending.count
        }
    }
    func updatePlan(now: Double) {
        desired = TilePlanner.plan(origin:origin,camera:camera,distance:viewDistance)
        roots = Set(desired.map { key in TileKey(z:18,x:key.x>>(key.z-18),y:key.y>>(key.z-18)) })
        let horizontal = Set(desired).union(roots)
        // Occupancy indexes use distinct zooms for each LOD. Keep a bounded set.
        let activeIndices = Set(horizontal.map(\.index))
        for key in indices.keys where !activeIndices.contains(key) && now-(indexAccess[key] ?? 0) > 20 {
            indices.removeValue(forKey:key); indexAccess.removeValue(forKey:key)
        }
        if indices.count > 32 {
            for key in indexAccess.sorted(by:{$0.value<$1.value}).prefix(indices.count-32).map(\.key) where !activeIndices.contains(key) {
                indices.removeValue(forKey:key); indexAccess.removeValue(forKey:key)
            }
        }
        expanded = expanded.filter{horizontal.contains($0.key)}
        var newNeeded = activeIndices
        for key in horizontal {
            if let index = indices[key.index] {
                indexAccess[key.index] = now
                do {
                    let candidates = try index.expand(key)
                    expanded[key] = candidates; newNeeded.formUnion(candidates)
                } catch { message = error.localizedDescription }
            }
        }
        needed = newNeeded
        knownBounds = knownBounds.filter{needed.contains($0.key)}
        for (key,task) in pending where !needed.contains(key) { task.cancel() }
        empty = empty.filter{$0.value > Date() && needed.contains($0.key)}
        failures = failures.filter{$0.value > Date() && needed.contains($0.key)}
        for key in tiles.keys where needed.contains(key) && inView(key) { accessed[key] = now }
        for key in tiles.keys where (!needed.contains(key) || !inView(key)) && now-(accessed[key] ?? 0) > 2 { evict(key) }
        enforceBudget(reserving:0)
        rebuildQueue()
        pump()
    }
    func rebuildQueue() {
        let eye = SIMD2(camera.eye.x,camera.eye.z)
        let frameOrigin = origin, coarseRoots = roots
        let direction = SIMD2(sin(camera.yaw),-cos(camera.yaw))
        let candidates = needed.filter { key in
            pending[key] == nil && tiles[key] == nil && empty[key] == nil && failures[key] == nil && indices[key] == nil && inView(key)
        }
        // Compute geographic distances once per candidate, not on every
        // comparison while sorting a queue with hundreds of height layers.
        queue = candidates.map { key -> (key:TileKey,rank:Double) in
            let delta = frameOrigin.tileCenter(key)-eye, d = simd_length(delta)
            let alignment = d > 0 ? simd_dot(delta/d,direction) : 1
            return (key,TilePlanner.requestRank(key,distance:d,alignment:alignment,
                coarse:coarseRoots.contains(key.horizontal)))
        }.sorted { a,b in
            a.rank == b.rank ? a.key < b.key : a.rank < b.rank
        }.map(\.key)
    }
    func pump() {
        guard active && !paused && !authFailed, let client, let factory else { return }
        while pending.count < 4 && fetching.count < 2 && !queue.isEmpty {
            let key = queue.removeFirst(), epoch = generation, frameOrigin = origin, texture = textureLimit
            let decoder = decoder
            fetching.insert(key)
            pending[key] = Task { [weak self] in
                do {
                    let raw = try await client.fetch(key)
                    try Task.checkCancellation()
                    guard let self, self.generation == epoch else { return }
                    self.fetching.remove(key)
                    self.pump()
                    if let raw {
                        try await self.processing.withSlot {
                            try Task.checkCancellation()
                            let decoded: [String:Data]
                            do { decoded = try await decoder.invoke(key.style == 100 ? "height_index" : "decode_tile",data:raw) }
                            catch {
                                if !(error is CancellationError) { await client.rejectCached(key) }
                                throw error
                            }
                            try Task.checkCancellation()
                            if key.style == 100 {
                                guard let data = decoded["json"] else { throw StreamError.invalidIndex }
                                let index = try JSONDecoder().decode(HeightIndex.self,from:data)
                                guard index.tile.z == key.z && index.tile.x == key.x && index.tile.y == key.y else { throw StreamError.invalidIndex }
                                if self.generation == epoch && self.needed.contains(key) { self.indices[key] = index }
                            } else {
                                guard let json = decoded["json"] else { throw StreamError.invalidGeometry }
                                let info = try JSONDecoder().decode(TileInfo.self,from:json)
                                guard info.min.count == 3, info.max.count == 3,
                                      info.transform.matrixR3x3.count == 9, info.transform.ecefTranslation.count == 3 else { throw StreamError.invalidGeometry }
                                if self.generation == epoch && self.needed.contains(key) {
                                    self.knownBounds[key] = info.sphere(origin:frameOrigin)
                                }
                                // Keep only the cheap bounds for an offscreen model.
                                // Its original bytes remain in the bounded disk cache.
                                if !self.inView(key) {
                                    return
                                }
                                let preparation = Task.detached(priority:.utility) {
                                    try Task.checkCancellation()
                                    return try factory.prepare(key:key,decoded:decoded,origin:frameOrigin,textureLimit:texture)
                                }
                                let tile = try await withTaskCancellationHandler(operation:{try await preparation.value},onCancel:{preparation.cancel()})
                                try Task.checkCancellation()
                                if self.generation == epoch && self.needed.contains(key) {
                                    guard tile.cost <= self.budget else { throw StreamError.gpuBudget }
                                    self.enforceBudget(reserving:tile.cost)
                                    // Prefer reducing the range over evicting visible geometry indefinitely.
                                    if self.tiles.values.reduce(0,{$0+$1.cost})+tile.cost > self.budget {
                                        self.viewDistance = max(120,self.viewDistance*0.8)
                                        self.message = "メモリに合わせて描画範囲を調整しました"
                                    } else {
                                        self.tiles[key] = tile; self.accessed[key] = CACurrentMediaTime()
                                        self.completed += 1
                                    }
                                }
                            }
                        }
                    } else if self.generation == epoch { self.empty[key] = Date().addingTimeInterval(60) }
                } catch is CancellationError { }
                catch {
                    guard let self, self.generation == epoch else { return }
                    if let failure = error as? StreamError, case .authentication = failure {
                        self.authFailed = true; self.pending.values.forEach{$0.cancel()}
                    }
                    if (error as? URLError)?.code != .cancelled {
                        self.failures[key] = Date().addingTimeInterval(20)
                        self.message = error.localizedDescription
                    }
                }
                guard let self, self.generation == epoch else { return }
                self.fetching.remove(key)
                self.pending.removeValue(forKey:key)
                if self.active && !self.paused && !self.authFailed {
                    self.updatePlan(now:CACurrentMediaTime())
                    if self.pending.isEmpty && self.queue.isEmpty && self.failures.isEmpty {
                        self.message = self.tiles.isEmpty ? "この範囲には対応する 3D データがありません" : "視界内の 3D モデルを表示中"
                    }
                }
            }
        }
    }
    func evict(_ key: TileKey) { tiles.removeValue(forKey:key); accessed.removeValue(forKey:key) }
    func enforceBudget(reserving: Int) {
        var cost = tiles.values.reduce(0){$0+$1.cost}
        let victims = tiles.keys.filter{!needed.contains($0)}.sorted{(accessed[$0] ?? 0)<(accessed[$1] ?? 0)}
        for key in victims where cost+reserving > budget {
            cost -= tiles[key]?.cost ?? 0; evict(key)
        }
    }
    func complete(_ horizontal: TileKey) -> Bool {
        guard let candidates = expanded[horizontal] else { return false }
        return candidates.allSatisfy{tiles[$0] != nil || empty[$0] != nil || knownBounds[$0] != nil && !inView($0)}
    }
    func inView(_ key: TileKey) -> Bool {
        guard let sphere = knownBounds[key] else { return true }
        return MetalRenderer.visible(sphere,viewProjection:camera.projection(far:viewDistance)*camera.view)
    }
    func renderTiles() -> [GPUTile] {
        selection().tiles
    }
    func centerFocus() -> SIMD3<Double> {
        let displayed = selection(), eye = SIMD3<Float>(camera.eye), direction = SIMD3<Float>(camera.forward)
        var nearest = Float(viewDistance), point: SIMD3<Double>?
        for tile in displayed.tiles where NavigationPicking.sphere(origin:eye,direction:direction,center:tile.center,radius:tile.radius) {
            let inverse = simd_inverse(tile.model)
            let localEye4 = inverse*SIMD4(eye,1), localDirection4 = inverse*SIMD4(direction,0)
            let localEye = SIMD3(localEye4.x,localEye4.y,localEye4.z), localDirection = SIMD3(localDirection4.x,localDirection4.y,localDirection4.z)
            let masks = displayed.masks[tile.key.horizontal]?.dropFirst() ?? ArraySlice<SIMD4<Float>>()
            func accept(_ hit: SIMD3<Float>, alpha: Float? = nil) {
                guard hit.x < nearest else { return }
                let worldPoint = eye+direction*hit.x
                guard !masks.contains(where:{worldPoint.x >= $0.x && worldPoint.x < $0.y && worldPoint.z >= $0.z && worldPoint.z < $0.w}) else { return }
                if let alpha {
                    guard min(0.99,alpha*81*(1-hit.y-hit.z)*hit.y*hit.z) >= 0.003 else { return }
                }
                nearest = hit.x; point = camera.eye+camera.forward*Double(hit.x)
            }
            if let vertices = tile.vertices, let indices = tile.indices {
                let floats = vertices.contents().assumingMemoryBound(to:Float.self)
                let indexes = indices.contents().assumingMemoryBound(to:UInt32.self)
                func position(_ index: UInt32) -> SIMD3<Float>? {
                    let i = Int(index)*8
                    guard i+2 < vertices.length/4 else { return nil }
                    return SIMD3(floats[i],floats[i+1],floats[i+2])
                }
                for i in stride(from:0,to:tile.triangles*3,by:3) {
                    guard let a = position(indexes[i]), let b = position(indexes[i+1]), let c = position(indexes[i+2]) else { continue }
                    if let hit = NavigationPicking.triangle(origin:localEye,direction:localDirection,
                        a:a,b:b,c:c) { accept(hit) }
                }
            }
            if let splats = tile.splats {
                let floats = splats.contents().assumingMemoryBound(to:Float.self)
                for i in stride(from:0,to:(tile.splatVertices/3)*3,by:3) {
                    let offset = i*10, alpha = floats[offset+6]
                    guard alpha > 0 else { continue }
                    func position(_ offset: Int) -> SIMD3<Float> { SIMD3(floats[offset],floats[offset+1],floats[offset+2]) }
                    if let hit = NavigationPicking.triangle(origin:localEye,direction:localDirection,
                        a:position(offset),b:position(offset+10),c:position(offset+20)) { accept(hit,alpha:alpha) }
                }
            }
        }
        return point ?? CameraNavigation.fallbackFocus(camera:camera,distance:viewDistance)
    }
    func beginNavigation(viewportHeight: Double) {
        guard active, !paused else { return }
        navigation.begin(camera:camera,focus:centerFocus(),viewportHeight:viewportHeight)
    }
    func pan(_ delta: SIMD2<Double>) {
        guard active, !paused, navigation.interacting else { return }
        navigation.pan(delta,camera:&camera)
    }
    func applyNavigation(_ update: NavigationTouchUpdate, viewportHeight: Double) {
        guard active, !paused, navigation.interacting else { return }
        navigation.apply(update,viewportHeight:viewportHeight,camera:&camera)
    }
    func endPan(velocity: SIMD2<Double>) {
        guard active, !paused, navigation.interacting else { return }
        navigation.endPan(pointsPerSecond:velocity,camera:camera)
    }
    func orbit(azimuth: Double = 0, elevation: Double = 0) {
        guard active, !paused, navigation.interacting else { return }
        navigation.orbit(azimuth:azimuth,elevation:elevation,camera:&camera)
    }
    func zoom(_ scale: Double) {
        guard active, !paused, navigation.interacting else { return }
        navigation.zoom(scale:scale,camera:&camera)
    }
    func stopNavigation() { navigation.stop(); elevation = 0 }
    func resetCamera() {
        let aspect = camera.aspect
        stopNavigation(); camera = CameraState(); camera.aspect = aspect
    }
    func selection() -> (tiles:[GPUTile], masks:[TileKey:[SIMD4<Float>]]) {
        var selected = Set<TileKey>()
        var masks = [TileKey:[SIMD4<Float>]]()
        for root in roots {
            let children = desired.filter { $0.x>>($0.z-18) == root.x && $0.y>>($0.z-18) == root.y }
            let fineReady = children.filter{ $0 != root && complete($0) }
            // Render each arriving coarse height instead of waiting for every
            // height (including empty layers) before showing the first model.
            let useCoarse = !children.allSatisfy{complete($0)}
            if useCoarse {
                selected.formUnion(expanded[root] ?? [])
                let rectangles = fineReady.map{origin.tileBounds($0)}
                masks[root] = [SIMD4(Float(rectangles.count),0,0,0)]+rectangles
            }
            // Refine each completed leaf immediately. The fallback's fragments
            // are masked in these rectangles, preventing duplicate Splat blending.
            for key in children where !useCoarse || key != root && complete(key) {
                selected.formUnion(expanded[key] ?? [])
            }
        }
        return (selected.compactMap{tiles[$0]},masks)
    }
    func setActive(_ value: Bool) {
        active = value; stopNavigation()
        if !value { pending.values.forEach{$0.cancel()} }
        else { lastPlan = 0 }
    }
    func memoryWarning() {
        memoryConstrainedUntil = CACurrentMediaTime()+60
        viewDistance = max(120,viewDistance*0.7)
        let visible = Set(renderTiles().map(\.key))
        for key in tiles.keys where !visible.contains(key) { evict(key) }
        var cost = tiles.values.reduce(0){$0+$1.cost}
        let eye = SIMD3<Float>(camera.eye)
        for key in tiles.values.sorted(by:{simd_distance_squared($0.center,eye)>simd_distance_squared($1.center,eye)}).map(\.key)
            where cost > budget {
            cost -= tiles[key]?.cost ?? 0; evict(key)
        }
        message = "メモリに合わせて表示範囲と画質を調整しました"
        lastPlan = 0
    }
    func qualityChanged() {
        invalidate()
        message = "画質に合わせてモデルを更新中"
    }
    func retry() {
        authFailed = false; failures.removeAll(); lastPlan = 0
        message = "Apple Maps に再接続中"
    }
    func restoreStandardConfiguration() {
        CredentialStore.restoreStandard()
        configure(.standard)
    }
    func clearCache() {
        invalidate()
        if let client { Task { await client.clearCache(); self.lastPlan = 0 } }
    }
}
