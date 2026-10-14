import Foundation
import simd

@main struct WorldChecks {
    static func main() throws {
        let origin = GeoOrigin(latitude:35.6586,longitude:139.7454)
        var camera = CameraState()
        let plan = TilePlanner.plan(origin:origin,camera:camera,distance:350)
        precondition(!plan.isEmpty && Set(plan).count == plan.count)
        precondition(Set(plan.map(\.z)) == Set([18,19,20]))
        for a in plan { for b in plan where a.z < b.z {
            precondition(!(b.x>>(b.z-a.z) == a.x && b.y>>(b.z-a.z) == a.y), "Overlapping LOD leaves")
        }}
        camera.eye.x += 600
        let moved = TilePlanner.plan(origin:origin,camera:camera,distance:350)
        precondition(Set(moved) != Set(plan), "Movement must request a different region")
        camera.yaw = .pi
        precondition(Set(TilePlanner.plan(origin:origin,camera:camera,distance:350)) != Set(moved))
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
        var wrong = heights; wrong.tile.x += 1
        do { _ = try wrong.expand(fine); preconditionFailure("Coordinate mismatch must fail") } catch { }
        let initial = CameraState(), ahead = initial.eye+initial.forward*100
        let clip = initial.projection(far:350)*initial.view*SIMD4(SIMD3<Float>(ahead),1)
        precondition(abs(clip.x/clip.w) < 0.001 && abs(clip.y/clip.w) < 0.001 && clip.z/clip.w > 0 && clip.z/clip.w < 1)
        let info = TileInfo(transform:.init(matrixR3x3:[1,0,0,0,1,0,0,0,1],ecefTranslation:[origin.ecef.x,origin.ecef.y,origin.ecef.z]),
            min:[0,0,0],max:[1,1,1],meshTriangles:0,splatVertices:0,vertexCount:0)
        precondition(simd_length(info.model(origin:origin).columns.3-SIMD4<Float>(0,0,0,1)) < 0.001)
        print("PASS: LOD partition, movement, rotation, dateline, vertical gaps, index coordinates, camera, ECEF")
    }
}
