import Foundation
import simd

struct TileKey: Hashable, Codable, Sendable, Comparable {
    var z: Int
    var x: Int
    var y: Int
    var h: Int = 0
    var style: Int = 98
    var name: String { "s\(style)_z\(z)_x\(x)_y\(y)_h\(h)" }
    // This researched service template exposes the occupancy index at z13.
    // Its cells are z17; requesting z11/z12 indexes returns an empty response.
    var index: TileKey { TileKey(z:13,x:x >> (z-13),y:y >> (z-13),style:100) }
    var horizontal: TileKey { TileKey(z: z, x: x, y: y) }
    static func < (a: Self, b: Self) -> Bool { a.name < b.name }
}

struct GeoOrigin: Codable, Sendable {
    var latitude: Double
    var longitude: Double
    var basis: simd_double3x3 {
        let p = latitude * .pi / 180, l = longitude * .pi / 180
        return simd_double3x3(rows: [SIMD3(-sin(l), cos(l), 0),
            SIMD3(cos(p)*cos(l), cos(p)*sin(l), sin(p)),
            SIMD3(sin(p)*cos(l), sin(p)*sin(l), -cos(p))])
    }
    var ecef: SIMD3<Double> {
        let p = latitude * .pi / 180, l = longitude * .pi / 180
        let n = 6378137 / sqrt(1 - 0.0066943799901413165 * pow(sin(p), 2))
        return SIMD3(n*cos(p)*cos(l), n*cos(p)*sin(l), n*(1-0.0066943799901413165)*sin(p))
    }
    func coordinate(east: Double, south: Double) -> GeoOrigin {
        let lat = min(85.05112878, max(-85.05112878, latitude-south/6378137*180 / .pi))
        let lon = longitude+east/(6378137*cos(latitude * .pi/180))*180 / .pi
        return GeoOrigin(latitude: lat, longitude: (lon+540).truncatingRemainder(dividingBy:360)-180)
    }
    func tileCenter(_ key: TileKey) -> SIMD2<Double> {
        let scale = Double(1 << key.z)
        let lon = (Double(key.x)+0.5)/scale*360-180
        let lat = atan(sinh(.pi*(1-2*(Double(key.y)+0.5)/scale)))*180 / .pi
        var delta = lon-longitude
        if delta > 180 { delta -= 360 }; if delta < -180 { delta += 360 }
        return SIMD2(delta * .pi/180*6378137*cos(latitude * .pi/180),
                     (latitude-lat) * .pi/180*6378137)
    }
    func tileWidth(_ zoom: Int) -> Double {
        2 * .pi * 6378137*cos(latitude * .pi/180)/Double(1 << zoom)
    }
    func tileBounds(_ key: TileKey) -> SIMD4<Float> {
        let scale = Double(1 << key.z)
        var points = [SIMD3<Double>]()
        for dy in 0...1 { for dx in 0...1 {
            let lon = Double(key.x+dx)/scale*360-180
            let lat = atan(sinh(.pi*(1-2*Double(key.y+dy)/scale)))*180 / .pi
            let corner = GeoOrigin(latitude:lat,longitude:lon)
            points.append(basis*(corner.ecef-ecef))
        }}
        return SIMD4(Float(points.map(\.x).min()!),Float(points.map(\.x).max()!),
                     Float(points.map(\.z).min()!),Float(points.map(\.z).max()!))
    }
}

struct CameraState: Sendable {
    var eye = SIMD3<Double>(0, 100, 160)
    var yaw: Double = 0
    var pitch: Double = -0.45
    var aspect: Double = 0.6
    var fov: Double = 60 * .pi/180
    var forward: SIMD3<Double> { SIMD3(sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)) }
    var right: SIMD3<Double> { SIMD3(cos(yaw), 0, sin(yaw)) }
    func projection(far: Double) -> simd_float4x4 {
        let y = Float(1/tan(fov/2)), x = y/Float(max(0.1,aspect)), near: Float = 0.5, f = Float(far)
        if far == .infinity {
            return simd_float4x4(columns:(SIMD4(x,0,0,0),SIMD4(0,y,0,0),
                SIMD4(0,0,-1,-1),SIMD4(0,0,-near,0)))
        }
        return simd_float4x4(columns: (SIMD4(x,0,0,0), SIMD4(0,y,0,0),
            SIMD4(0,0,f/(near-f),-1), SIMD4(0,0,near*f/(near-f),0)))
    }
    var view: simd_float4x4 {
        let f = SIMD3<Float>(forward), r = SIMD3<Float>(right), u = simd_cross(r,f)
        let e = SIMD3<Float>(eye)
        return simd_float4x4(rows: [SIMD4(r.x,r.y,r.z,-simd_dot(r,e)),
            SIMD4(u.x,u.y,u.z,-simd_dot(u,e)), SIMD4(-f.x,-f.y,-f.z,simd_dot(f,e)), SIMD4(0,0,0,1)])
    }
}

struct TilePlanner {
    static func requestTier(_ key: TileKey, uncoveredRoots: Set<TileKey>) -> Int {
        if key.style == 100 { return 0 }
        if uncoveredRoots.contains(key.horizontal) { return 1 }
        return 2
    }
    static func requestRank(_ key: TileKey, distance: Double, alignment: Double, coarse: Bool,
                            futureDistance: Double = 0) -> Double {
        if key.style == 100 { return -10000+Double(key.z) }
        // Give fallback geometry a local head start. An unbounded coarse
        // preference makes every distant root delay nearby fine geometry.
        return distance+(1-alignment)*180-(coarse ? 150 : 0)+futureDistance*0.8+Double(key.h)*0.01
    }
    // Quadtree leaves partition the entire loading region, independently of yaw.
    // C3MM expands *every* occupied vertical cell, including discontinuous towers.
    static func plan(origin: GeoOrigin, camera: CameraState, distance: Double,
                     previous: Set<TileKey> = [], maximumZoom: Int = 20) -> [TileKey] {
        let location = origin.coordinate(east: camera.eye.x, south: camera.eye.z)
        let n = 1 << 18
        let xx = Int(floor((location.longitude+180)/360*Double(n)))
        let yy = Int(floor((1-asinh(tan(location.latitude * .pi/180)) / .pi)/2*Double(n)))
        let width = origin.tileWidth(18)
        let radius = Int(ceil(distance/width))+1
        var refined = Set<TileKey>()
        for leaf in previous where leaf.z > 18 {
            for z in 18..<leaf.z { refined.insert(TileKey(z:z,x:leaf.x>>(leaf.z-z),y:leaf.y>>(leaf.z-z))) }
        }
        var leaves = [TileKey]()
        func visit(_ key: TileKey) {
            let center = origin.tileCenter(key)
            let delta = center-SIMD2(camera.eye.x,camera.eye.z)
            let halfDiagonal = origin.tileWidth(key.z)*0.71
            let length = simd_length(delta)
            guard length-halfDiagonal <= distance else { return }
            let minimumDistance = max(0,length-halfDiagonal)
            let threshold = key.z == 18 ? (refined.contains(key) ? 240.0 : 200.0) : (refined.contains(key) ? 120.0 : 85.0)
            if key.z < maximumZoom && minimumDistance < threshold {
                for dy in 0..<2 { for dx in 0..<2 {
                    visit(TileKey(z:key.z+1,x:key.x*2+dx,y:key.y*2+dy))
                }}
            } else { leaves.append(key) }
        }
        for dy in -radius...radius { for dx in -radius...radius {
            let y = yy+dy
            if (0..<n).contains(y) { visit(TileKey(z:18,x:(xx+dx+n)%n,y:y)) }
        }}
        return leaves.sorted { a,b in
            let eye = SIMD2(camera.eye.x,camera.eye.z)
            return simd_length(origin.tileCenter(a)-eye) < simd_length(origin.tileCenter(b)-eye)
        }
    }
}

enum StreamingPolicy {
    static let coarseZoom = 16
    static let maximumCoverageRectangles = 256
    static func textureTarget(zoom: Int, source: Int, current: Int, headroom: Int,
                              constrained: Bool, pressure: Bool, upgradeAllowed: Bool) -> Int {
        let target = textureLimit(zoom:zoom,source:source,constrained:constrained || pressure,headroom:headroom)
        if pressure || !upgradeAllowed { return min(current,target) }
        return constrained ? target : max(current,target)
    }
    static func textureLimit(zoom: Int, source: Int, constrained: Bool, headroom: Int) -> Int {
        let lodLimit = zoom >= 20 ? min(source,8192) : (zoom == 19 ? 2048 : 1024)
        var limit = min(source, constrained ? (zoom >= 20 ? 1024 : 512) : lodLimit)
        // Reserve mip storage and a replacement alongside the currently displayed atlas.
        while limit > 512 && Double(limit)*Double(limit)*4*1.34 > Double(max(0,headroom)) { limit /= 2 }
        return max(1,limit)
    }
    static func retention(distance: Double) -> Double { distance <= 130 ? 60 : (distance <= 350 ? 40 : 20) }
    static func evictionScore(distance: Double, zoom: Int, age: Double, bytes: Int, needed: Bool, visible: Bool) -> Double {
        distance*4 + Double(max(0,zoom-18))*600 + min(age,120)*5 + Double(bytes)/1048576*8
            - (needed ? 800 : 0) - (visible ? 1600 : 0)
    }
}

// Packed geometry plus the original compressed atlas, never a full-size CPU bitmap.
// Independent byte and lifetime bounds apply even while corresponding GPU tiles live.
struct DecodedTileCache {
    struct Entry { var data: [String:Data]; var cost: Int; var used: Double }
    private(set) var entries: [TileKey:Entry] = [:]
    private(set) var bytes = 0
    mutating func value(for key: TileKey, now: Double) -> [String:Data]? {
        guard var entry = entries[key] else { return nil }
        entry.used = now; entries[key] = entry; return entry.data
    }
    mutating func insert(_ data: [String:Data], for key: TileKey, now: Double, budget: Int) {
        if let old = entries.removeValue(forKey:key) { bytes -= old.cost }
        let cost = data.values.reduce(0){$0+$1.count}
        if cost <= budget { entries[key] = Entry(data:data,cost:cost,used:now); bytes += cost }
        trim(now:now,budget:budget)
    }
    mutating func trim(now: Double, budget: Int) {
        for (key,entry) in entries.sorted(by:{$0.value.used<$1.value.used}) {
            if bytes > budget || now-entry.used > 60 { entries.removeValue(forKey:key); bytes -= entry.cost }
        }
    }
    mutating func removeAll() { entries.removeAll(); bytes = 0 }
}

struct TileInfo: Decodable, Sendable {
    struct Transform: Decodable, Sendable { var matrixR3x3: [Double]; var ecefTranslation: [Double] }
    var transform: Transform
    var min: [Double]
    var max: [Double]
    var meshTriangles: Int
    var splatVertices: Int
    var vertexCount: Int
    var atlasDimensions: [Int]?
    func validBuffers(_ data: [String:Data]) -> Bool {
        guard (0...1_500_000).contains(vertexCount), (0...500_000).contains(meshTriangles),
              (0...1_500_000).contains(splatVertices),
              transform.matrixR3x3.count == 9, transform.ecefTranslation.count == 3,
              min.count == 3, max.count == 3,
              (transform.matrixR3x3+transform.ecefTranslation+min+max).allSatisfy({$0.isFinite}),
              (0..<3).allSatisfy({min[$0] <= max[$0]}),
              let vertices = data["vertices"], let indices = data["indices"], let splats = data["splats"],
              vertices.count == vertexCount*32, indices.count == meshTriangles*12,
              splats.count == splatVertices*40, data["atlas"] != nil,
              vertices.count+indices.count+splats.count <= 64*1024*1024 else { return false }
        return true
    }
    func sphere(origin: GeoOrigin) -> TileSphere {
        let lower = SIMD3<Float>(Float(min[0]),Float(min[1]),Float(min[2]))
        let upper = SIMD3<Float>(Float(max[0]),Float(max[1]),Float(max[2]))
        let center = model(origin:origin)*SIMD4((lower+upper)/2,1)
        return TileSphere(center:SIMD3(center.x,center.y,center.z),radius:simd_length(upper-lower)/2)
    }
    func model(origin: GeoOrigin) -> simd_float4x4 {
        let r = transform.matrixR3x3
        let rotation = simd_double3x3(rows: [SIMD3(r[0],r[1],r[2]),SIMD3(r[3],r[4],r[5]),SIMD3(r[6],r[7],r[8])])
        let m = origin.basis*rotation
        let t = transform.ecefTranslation
        let shift = origin.basis*(SIMD3(t[0],t[1],t[2])-origin.ecef)
        return simd_float4x4(columns: (SIMD4(SIMD3<Float>(m.columns.0),0),
            SIMD4(SIMD3<Float>(m.columns.1),0),SIMD4(SIMD3<Float>(m.columns.2),0),SIMD4(SIMD3<Float>(shift),1)))
    }
}

struct TileSphere: Sendable { var center: SIMD3<Float>; var radius: Float }

struct TileDrawTiming: Sendable {
    var key: TileKey
    var trace: String?
    var neededAt: Double
}

enum RenderVisibility {
    static func withinDistance(_ position: SIMD3<Float>, eye: SIMD3<Float>, distance: Float,
                               radius: Float = 0) -> Bool {
        simd_length(SIMD2(position.x-eye.x,position.z-eye.z))-radius <= distance
    }
    static func visible(_ tile: TileSphere, viewProjection m: simd_float4x4,
                        eye: SIMD3<Float>, distance: Float) -> Bool {
        guard withinDistance(tile.center,eye:eye,distance:distance,radius:tile.radius) else { return false }
        let r0 = SIMD4(m[0,0],m[1,0],m[2,0],m[3,0])
        let r1 = SIMD4(m[0,1],m[1,1],m[2,1],m[3,1])
        let r2 = SIMD4(m[0,2],m[1,2],m[2,2],m[3,2])
        let r3 = SIMD4(m[0,3],m[1,3],m[2,3],m[3,3])
        // The shader clips the horizontal radius. There is no vertical far plane.
        for p in [r3+r0,r3-r0,r3+r1,r3-r1,r2] {
            if simd_dot(p,SIMD4(tile.center,1)) < -tile.radius*simd_length(SIMD3(p.x,p.y,p.z)) { return false }
        }
        return true
    }
}

struct HeightIndex: Decodable, Sendable {
    struct Position: Decodable, Sendable { var z: Int; var x: Int; var y: Int }
    var tile: Position
    var cells: [[Int]]
    func valid(for key: TileKey) -> Bool {
        tile.z == key.z && tile.x == key.x && tile.y == key.y && cells.count <= 65535 &&
            cells.allSatisfy { $0.count == 3 && (0..<16).contains($0[0]) &&
                (0..<16).contains($0[1]) && (0..<256).contains($0[2]) } && Set(cells).count == cells.count
    }
    func expand(_ key: TileKey) throws -> [TileKey] {
        guard (16...20).contains(key.z), tile.z == key.index.z,
              tile.x == key.index.x && tile.y == key.index.y,
              cells.allSatisfy({ $0.count == 3 }) else { throw StreamError.invalidIndex }
        if key.z == 16 {
            let localX = key.x*2%16, localY = 15-key.y*2%16
            let heights = Set(cells.filter {
                (localX..<localX+2).contains($0[0]) && (localY-1...localY).contains($0[1])
            }.map { $0[2]/2 })
            return heights.map { TileKey(z:key.z,x:key.x,y:key.y,h:$0) }.sorted()
        }
        let multiplier = 1 << (key.z-17)
        let localX = key.x/multiplier%16, localY = 15-key.y/multiplier%16
        return cells.filter { $0[0] == localX && $0[1] == localY }.flatMap { cell in
            (0..<multiplier).map { child in TileKey(z:key.z,x:key.x,y:key.y,h:cell[2]*multiplier+child) }
        }.sorted()
    }
}

enum StreamError: LocalizedError {
    case configuration, invalidIndex, authentication, http(Int), responseTooLarge, invalidGeometry, gpuBudget
    var errorDescription: String? {
        switch self {
        case .configuration: return "Apple Maps の取得設定がありません。設定を読み込んでください。"
        case .invalidIndex: return "高さインデックスの形式または座標が未対応です。"
        case .authentication: return "Apple Maps の取得認証が失効しました。取得設定を更新してください。"
        case .http(let code): return "Apple Maps に接続できませんでした（HTTP \(code)）。"
        case .responseTooLarge: return "取得データがタイル容量の上限を超えました。"
        case .invalidGeometry: return "3D モデルの配列が不正です。"
        case .gpuBudget: return "モデルがメモリ上限を超えました。描画範囲を狭めてください。"
        }
    }
}
