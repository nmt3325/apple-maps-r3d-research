import Foundation
import simd

@main struct WorldChecks {
    static func main() throws {
        let origin = GeoOrigin(latitude:35.6586,longitude:139.7454)
        var camera = CameraState()
        let plan = TilePlanner.plan(origin:origin,camera:camera,distance:350)
        precondition(!plan.isEmpty && Set(plan).count == plan.count)
        precondition(Set(plan.map(\.z)) == Set([18,19,20]))
        var portrait = camera, landscape = camera
        portrait.aspect = 0.46; landscape.aspect = 1.5
        let portraitPlan = Set(TilePlanner.plan(origin:origin,camera:portrait,distance:600))
        let landscapePlan = Set(TilePlanner.plan(origin:origin,camera:landscape,distance:600))
        precondition(portraitPlan == landscapePlan,
            "Aspect changes must preserve the surrounding preload region")
        let nearFine = TileKey(z:20,x:931326,y:412987)
        let fallback = TileKey(z:18,x:232831,y:103246)
        precondition(TilePlanner.requestTier(fallback,uncoveredRoots:[fallback])
            < TilePlanner.requestTier(nearFine,uncoveredRoots:[fallback]),
            "Missing lightweight coverage must not wait behind detail requests")
        precondition(TilePlanner.requestTier(nearFine.index,uncoveredRoots:[fallback])
            < TilePlanner.requestTier(fallback,uncoveredRoots:[fallback]))
        func rank(_ key: TileKey, _ distance: Double, _ coarse: Bool) -> Double {
            TilePlanner.requestRank(key,distance:distance,alignment:1,coarse:coarse)
        }
        precondition(rank(fallback,100,true) < rank(nearFine,100,false), "Nearby fallback arrives first")
        precondition(rank(nearFine,100,false) < rank(fallback,600,true), "Far roots must not starve near detail")
        precondition(rank(nearFine.index,0,false) < rank(fallback,0,true), "Occupancy index arrives first")
        precondition(TilePlanner.requestRank(nearFine,distance:100,alignment:1,coarse:false,futureDistance:50)
            < TilePlanner.requestRank(nearFine,distance:100,alignment:1,coarse:false,futureDistance:200),
            "Prefer geometry along the predicted movement")
        for a in plan { for b in plan where a.z < b.z {
            precondition(!(b.x>>(b.z-a.z) == a.x && b.y>>(b.z-a.z) == a.y), "Overlapping LOD leaves")
        }}
        camera.eye.x += 600
        let moved = TilePlanner.plan(origin:origin,camera:camera,distance:350)
        precondition(Set(moved) != Set(plan), "Movement must request a different region")
        camera.yaw = .pi
        precondition(Set(TilePlanner.plan(origin:origin,camera:camera,distance:350)) == Set(moved), "Rotation must preserve the entire preload region")
        let surrounding = TilePlanner.plan(origin:origin,camera:camera,distance:600)
        for quadrant in 0..<4 {
            precondition(surrounding.contains { key in
                let delta = origin.tileCenter(key)-SIMD2(camera.eye.x,camera.eye.z)
                return simd_length(delta) > 250 && (delta.x >= 0 ? 1 : 0)+(delta.y >= 0 ? 2 : 0) == quadrant
            }, "All four directions must be loaded")
        }
        var shifted = CameraState(); shifted.eye.x += 40
        let cold = TilePlanner.plan(origin:origin,camera:shifted,distance:350)
        let warm = TilePlanner.plan(origin:origin,camera:shifted,distance:350,previous:Set(plan))
        precondition(warm.filter{$0.z == 20}.count > cold.filter{$0.z == 20}.count, "Keep high LOD through the hysteresis band")
        for a in warm { for b in warm where a.z < b.z {
            precondition(!(b.x>>(b.z-a.z) == a.x && b.y>>(b.z-a.z) == a.y), "Hysteresis must preserve partition")
        }}
        precondition(TilePlanner.plan(origin:origin,camera:shifted,distance:350,previous:Set(warm),maximumZoom:19).allSatisfy{$0.z <= 19})
        precondition(StreamingPolicy.textureLimit(zoom:20,source:4096,constrained:false,headroom:192*1048576) == 4096)
        precondition(StreamingPolicy.textureLimit(zoom:19,source:4096,constrained:false,headroom:192*1048576) == 2048)
        precondition(StreamingPolicy.textureLimit(zoom:18,source:4096,constrained:false,headroom:192*1048576) == 1024)
        precondition(StreamingPolicy.textureLimit(zoom:20,source:4096,constrained:true,headroom:96*1048576) == 1024)
        precondition(StreamingPolicy.textureLimit(zoom:19,source:4096,constrained:true,headroom:96*1048576) == 512)
        precondition(StreamingPolicy.textureLimit(zoom:20,source:4096,constrained:false,headroom:2*1048576) == 512)
        // Replay the observed 896 <-> 448 cycle against a fixed set of other residents.
        func atlasBytes(_ pixels: Int) -> Int { Int(Double(pixels)*Double(pixels)*4*1.34) }
        let textureBudget = 192*1048576
        let otherResidents = textureBudget-atlasBytes(896)-200_000
        var currentLimit = 896, transitions = 0
        for _ in 0..<1000 {
            let ownBytes = atlasBytes(currentLimit)
            let resident = otherResidents+ownBytes
            let target = StreamingPolicy.textureTarget(zoom:20,source:896,current:currentLimit,
                headroom:textureBudget-resident+ownBytes,constrained:false,pressure:true,upgradeAllowed:true)
            if target != currentLimit { currentLimit = target; transitions += 1 }
        }
        precondition(transitions <= 1, "Stable pressure must not cycle an atlas between two resolutions")
        precondition(StreamingPolicy.textureTarget(zoom:20,source:896,current:448,
            headroom:192*1048576,constrained:false,pressure:true,upgradeAllowed:true) == 448,
            "Pressure must not regrow an already reduced atlas")
        precondition(StreamingPolicy.textureTarget(zoom:20,source:896,current:448,
            headroom:192*1048576,constrained:false,pressure:false,upgradeAllowed:false) == 448,
            "Wait before regrowing after a reduction or a distance change")
        precondition(StreamingPolicy.textureTarget(zoom:20,source:896,current:448,
            headroom:192*1048576,constrained:false,pressure:false,upgradeAllowed:true) == 896,
            "Restore detail when pressure and the cooldown have ended")
        precondition(StreamingPolicy.textureTarget(zoom:20,source:4096,current:4096,
            headroom:0,constrained:true,pressure:true,upgradeAllowed:false) == 512,
            "Cooldown must not block a further emergency reduction")
        let farHigh = StreamingPolicy.evictionScore(distance:500,zoom:20,age:20,bytes:8*1048576,needed:true,visible:false)
        let nearCoarse = StreamingPolicy.evictionScore(distance:60,zoom:18,age:0,bytes:1048576,needed:true,visible:true)
        precondition(farHigh > nearCoarse)
        precondition(StreamingPolicy.retention(distance:80) == 60 && StreamingPolicy.retention(distance:300) == 40)
        var cache = DecodedTileCache()
        let a = TileKey(z:20,x:1,y:1), b = TileKey(z:20,x:2,y:1), c = TileKey(z:20,x:3,y:1)
        cache.insert(["vertices":Data(count:8)],for:a,now:0,budget:16)
        cache.insert(["vertices":Data(count:8)],for:b,now:1,budget:16)
        precondition(cache.value(for:a,now:2) != nil)
        cache.insert(["vertices":Data(count:8)],for:c,now:3,budget:16)
        precondition(cache.entries[b] == nil && cache.entries[a] != nil && cache.bytes == 16)
        cache.insert(["vertices":Data(count:4)],for:a,now:4,budget:16)
        precondition(cache.bytes == 12)
        cache.trim(now:5,budget:4); precondition(cache.bytes == 4 && cache.entries[a] != nil)
        cache.trim(now:65,budget:4); precondition(cache.bytes == 0)
        let dateline = GeoOrigin(latitude:0,longitude:179.99999)
        let wrapped = TilePlanner.plan(origin:dateline,camera:CameraState(),distance:600)
        precondition(wrapped.contains{$0.x < 8} && wrapped.contains{$0.x > (1 << $0.z)-8})
        precondition(wrapped.allSatisfy{$0.x >= 0 && $0.x < (1 << $0.z) && $0.y >= 0 && $0.y < (1 << $0.z)})
        let fine = TileKey(z:20,x:931326,y:412987)
        let index = fine.index
        let localX = fine.x/8%16, localY = 15-fine.y/8%16
        let heights = HeightIndex(tile:.init(z:13,x:index.x,y:index.y),cells:[[localX,localY,0],[localX,localY,2]])
        let candidates = try heights.expand(fine)
        precondition(Set(candidates.map(\.h)) == Set(Array(0...7)+Array(16...23)), "Do not stop at an empty intermediate height")
        let coarse = TileKey(z:18,x:fine.x/4,y:fine.y/4)
        let coarseCandidates = try heights.expand(coarse)
        precondition(Set(coarseCandidates.map(\.h)) == Set([0,1,4,5]))
        precondition(fine.index == coarse.index)
        let overview = TileKey(z:16,x:fine.x>>4,y:fine.y>>4)
        let overviewCandidates = try heights.expand(overview)
        precondition(Set(overviewCandidates.map(\.h)) == Set([0,1]),
            "z16 merges all occupied z17 cells and vertical parents without duplicates")
        var overviewHeights = heights
        overviewHeights.cells = [[localX,localY,0],[localX,localY,6],[localX^1,localY^1,7]]
        let discontinuousOverview = try overviewHeights.expand(overview)
        precondition(Set(discontinuousOverview.map(\.h)) == Set([0,3]),
            "z16 must preserve discontinuous upper layers across all four horizontal children")
        precondition(StreamingPolicy.maximumCoverageRectangles == 1 << (2*(20-StreamingPolicy.coarseZoom)))
        var wrong = heights; wrong.tile.x += 1
        do { _ = try wrong.expand(fine); preconditionFailure("Coordinate mismatch must fail") } catch { }
        let initial = CameraState(), ahead = initial.eye+initial.forward*100
        let elevatedPoint = SIMD3<Float>(100,10000,100)
        precondition(RenderVisibility.withinDistance(elevatedPoint,eye:SIMD3(0,-10000,0),distance:150))
        precondition(!RenderVisibility.withinDistance(SIMD3(151,0,0),eye:SIMD3(0,10000,0),distance:150))
        var overhead = CameraState()
        overhead.eye = SIMD3(0,10000,0); overhead.pitch = -.pi/2
        let overheadVP = overhead.projection(far:.infinity)*overhead.view
        precondition(RenderVisibility.visible(TileSphere(center:SIMD3(0,0,0),radius:1),
            viewProjection:overheadVP,eye:SIMD3<Float>(overhead.eye),distance:150),
            "A model directly below remains visible regardless of altitude")
        var upward = CameraState()
        upward.eye = SIMD3(0,0,0); upward.pitch = .pi/2
        precondition(RenderVisibility.visible(TileSphere(center:elevatedPoint,radius:1),
            viewProjection:upward.projection(far:.infinity)*upward.view,
            eye:SIMD3<Float>(upward.eye),distance:150), "Height must not impose a far distance")
        let viewProjection = initial.projection(far:350)*initial.view
        let point = SIMD4<Float>(SIMD3<Float>(ahead),1)
        let clip = simd_mul(viewProjection,point)
        precondition(abs(clip.x/clip.w) < 0.001 && abs(clip.y/clip.w) < 0.001 && clip.z/clip.w > 0 && clip.z/clip.w < 1)
        let info = TileInfo(transform:.init(matrixR3x3:[1,0,0,0,1,0,0,0,1],ecefTranslation:[origin.ecef.x,origin.ecef.y,origin.ecef.z]),
            min:[0,0,0],max:[1,1,1],meshTriangles:0,splatVertices:0,vertexCount:0)
        precondition(simd_length(info.model(origin:origin).columns.3-SIMD4<Float>(0,0,0,1)) < 0.001)
        print("PASS: LOD partition, movement, rotation, dateline, vertical gaps, index coordinates, camera, ECEF")
    }
}
