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
    @Published var paused = false
    @Published var viewDistance = 350.0
    @Published var locationLabel = "東京タワー"
    @Published var rendererError: String?
    var camera = CameraState()
    var origin = GeoOrigin(latitude:35.6586,longitude:139.7454)
    var movement = SIMD2<Double>.zero
    var elevation = 0.0
    var speed = 35.0
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
        pending.values.forEach{$0.cancel()}; pending.removeAll(); queue.removeAll()
        tiles.removeAll(); knownBounds.removeAll(); accessed.removeAll(); empty.removeAll(); failures.removeAll()
        indices.removeAll(); indexAccess.removeAll(); expanded.removeAll()
        desired.removeAll(); roots.removeAll(); needed.removeAll(); lastPlan = 0
    }
    func relocate(latitude: Double, longitude: Double, label: String) {
        guard latitude.isFinite, longitude.isFinite, abs(latitude) <= 85.05112878, abs(longitude) <= 180 else {
            message = "緯度・経度の範囲を確認してください。"; return
        }
        invalidate(); origin = GeoOrigin(latitude:latitude,longitude:longitude)
        camera.eye = SIMD3(0,100,160); camera.yaw = 0; camera.pitch = -0.45
        locationLabel = label; completed = 0
    }
    func step(dt: Double, now: Double) {
        if !paused {
            camera.eye += (camera.right*movement.x+camera.forward*movement.y)*speed*dt
            camera.eye.y = max(2,camera.eye.y+elevation*speed*dt)
        }
        if simd_length(SIMD2(camera.eye.x,camera.eye.z)) > 3000 {
            let coordinate = origin.coordinate(east:camera.eye.x,south:camera.eye.z)
            let altitude = camera.eye.y, yaw = camera.yaw, pitch = camera.pitch
            relocate(latitude:coordinate.latitude,longitude:coordinate.longitude,label:locationLabel)
            camera.eye = SIMD3(0,altitude,0); camera.yaw = yaw; camera.pitch = pitch
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
        queue = needed.filter { key in
            pending[key] == nil && tiles[key] == nil && empty[key] == nil && failures[key] == nil && indices[key] == nil && inView(key)
        }.sorted { a,b in
            func rank(_ key: TileKey) -> Double {
                if key.style == 100 { return -10000+Double(key.z) }
                let delta = frameOrigin.tileCenter(key)-eye, d = simd_length(delta)
                let alignment = d > 0 ? simd_dot(delta/d,direction) : 1
                return (coarseRoots.contains(key.horizontal) ? -5000 : 0)+d+(1-alignment)*120+Double(key.h)*0.01
            }
            return rank(a)<rank(b)
        }
    }
    func pump() {
        guard active && !paused && !authFailed, let client, let factory else { return }
        while pending.count < 2 && !queue.isEmpty {
            let key = queue.removeFirst(), epoch = generation, frameOrigin = origin, texture = textureLimit
            let decoder = decoder
            pending[key] = Task { [weak self] in
                do {
                    let raw = try await client.fetch(key)
                    try Task.checkCancellation()
                    guard let self, self.generation == epoch else { return }
                    if let raw {
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
                                self.pending.removeValue(forKey:key)
                                self.updatePlan(now:CACurrentMediaTime())
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
    func selection() -> (tiles:[GPUTile], masks:[TileKey:[SIMD4<Float>]]) {
        var selected = Set<TileKey>()
        var masks = [TileKey:[SIMD4<Float>]]()
        for root in roots {
            let children = desired.filter { $0.x>>($0.z-18) == root.x && $0.y>>($0.z-18) == root.y }
            let fineReady = children.filter{ $0 != root && complete($0) }
            let useCoarse = !children.allSatisfy{complete($0)} && complete(root)
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
        active = value; movement = .zero; elevation = 0
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
    func clearCache() {
        invalidate()
        if let client { Task { await client.clearCache(); self.lastPlan = 0 } }
    }
}
