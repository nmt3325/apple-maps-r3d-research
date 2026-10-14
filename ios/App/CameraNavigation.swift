import Foundation
import simd

enum NavigationTouchPhase { case begin, move, end, cancel }
enum NavigationTwoFingerOperation { case tilt, twist, zoom }

struct NavigationTouchUpdate {
    var count: Int
    var modeChanged = false
    var operation: NavigationTwoFingerOperation? = nil
    var delta = SIMD2<Double>.zero
    var twist = 0.0
    var zoom = 1.0
    var releaseVelocity = SIMD2<Double>.zero
}

struct NavigationTouchInput {
    private(set) var count = 0
    private var center = SIMD2<Double>.zero
    private var angle = 0.0
    private var span = 0.0
    private var lastTime = 0.0
    private var lastMotionTime = 0.0
    private var velocity = SIMD2<Double>.zero
    private var operation: NavigationTwoFingerOperation?
    private var startCenter = SIMD2<Double>.zero
    private var startAngle = 0.0
    private var startSpan = 0.0
    private static func wrapped(_ angle: Double) -> Double { atan2(sin(angle),cos(angle)) }
    mutating func update(points: [SIMD2<Double>], time: Double) -> NavigationTouchUpdate {
        let nextCenter: SIMD2<Double> = points.isEmpty ? .zero : points.reduce(.zero,+)/Double(points.count)
        let pair = points.count == 2 ? points[1]-points[0] : .zero
        let nextAngle = atan2(pair.y,pair.x), nextSpan = simd_length(pair)
        var result = NavigationTouchUpdate(count:points.count)
        if points.count != count {
            result.modeChanged = true
            if points.isEmpty, count == 1, time-lastMotionTime <= 0.15 { result.releaseVelocity = velocity }
            // A change in finger count resets the baseline, never becoming a swipe or twist.
            count = points.count; velocity = .zero; lastMotionTime = time
            operation = nil; startCenter = nextCenter; startAngle = nextAngle; startSpan = nextSpan
        } else if count == 1 {
            result.delta = nextCenter-center
            if simd_length_squared(result.delta) > 0 {
                velocity = result.delta/max(0.008,time-lastTime); lastMotionTime = time
            }
        } else if count == 2 {
            let totalTilt = nextCenter.y-startCenter.y
            let totalTwist = Self.wrapped(nextAngle-startAngle)
            let totalZoom = startSpan > 8 && nextSpan > 8 ? nextSpan/startSpan : 1
            var justLocked = false
            if operation == nil {
                // Ignore small finger wobble, then lock the dominant intent for this touch pair.
                let scores: [(NavigationTwoFingerOperation,Double)] = [
                    (.tilt,abs(totalTilt)/6), (.twist,abs(totalTwist)/0.06),
                    (.zoom,abs(log(totalZoom))/log(1.06))]
                if let winner = scores.max(by:{$0.1 < $1.1}), winner.1 >= 1 {
                    operation = winner.0; justLocked = true
                }
            }
            result.operation = operation
            switch operation {
            case .tilt:
                result.delta.y = justLocked ? totalTilt : nextCenter.y-center.y
            case .twist:
                result.twist = justLocked ? totalTwist : Self.wrapped(nextAngle-angle)
            case .zoom:
                if justLocked { result.zoom = totalZoom }
                else if span > 8, nextSpan > 8 { result.zoom = nextSpan/span }
            case nil: break
            }
        }
        center = nextCenter; angle = nextAngle; span = nextSpan; lastTime = time
        return result
    }
}

// Camera math is independent of UIKit so gestures and inertia can be checked on macOS.
struct CameraNavigation: Sendable {
    var focus = SIMD3<Double>.zero
    private(set) var velocity = SIMD3<Double>.zero
    private(set) var interacting = false
    private var metersPerPoint = 1.0

    mutating func begin(camera: CameraState, focus: SIMD3<Double>, viewportHeight: Double) {
        stop(); interacting = true; self.focus = focus
        metersPerPoint = 2 * max(1,simd_distance(camera.eye,focus)) * tan(camera.fov/2) / max(1,viewportHeight)
    }
    func horizontalDelta(_ points: SIMD2<Double>, camera: CameraState) -> SIMD3<Double> {
        let forward = SIMD3(sin(camera.yaw),0,-cos(camera.yaw))
        return (-camera.right*points.x+forward*points.y)*metersPerPoint
    }
    mutating func pan(_ points: SIMD2<Double>, camera: inout CameraState) {
        let delta = horizontalDelta(points,camera:camera)
        camera.eye += delta; focus += delta
    }
    mutating func apply(_ update: NavigationTouchUpdate, viewportHeight: Double, camera: inout CameraState) {
        if update.count == 1 { pan(update.delta,camera:&camera) }
        else if update.count == 2 {
            switch update.operation {
            case .tilt: orbit(azimuth:0,elevation:-update.delta.y * .pi / max(1,viewportHeight),camera:&camera)
            case .twist: orbit(azimuth:-update.twist,elevation:0,camera:&camera)
            case .zoom: zoom(scale:update.zoom,camera:&camera)
            case nil: break
            }
        }
    }
    mutating func endPan(pointsPerSecond: SIMD2<Double>, camera: CameraState) {
        interacting = false
        velocity = horizontalDelta(pointsPerSecond,camera:camera)
        let speed = simd_length(velocity)
        if speed > 2000 { velocity *= 2000/speed }
    }
    mutating func endOrbit() { interacting = false; velocity = .zero }
    mutating func orbit(azimuth: Double, elevation: Double, camera: inout CameraState) {
        let radius = max(0.5,simd_distance(camera.eye,focus))
        // Keep the eye above the ground while preserving the actual orbit target.
        let upperPitch = min(1.4,asin(min(1,max(-1,(focus.y-2)/radius))))
        camera.yaw = (camera.yaw+azimuth).truncatingRemainder(dividingBy:2 * .pi)
        camera.pitch = min(upperPitch,max(-1.5,camera.pitch+elevation))
        camera.eye = focus-camera.forward*radius
    }
    mutating func zoom(scale: Double, camera: inout CameraState) {
        guard scale.isFinite, scale > 0 else { return }
        var radius = min(5000,max(2,simd_distance(camera.eye,focus)/scale))
        // Limit the zoom distance at the ground instead of changing the camera's pitch.
        if camera.forward.y < -0.0001 { radius = max(radius,(2-focus.y)/(-camera.forward.y)) }
        else if camera.forward.y > 0.0001 { radius = min(radius,max(0.5,(focus.y-2)/camera.forward.y)) }
        camera.eye = focus-camera.forward*radius
    }
    mutating func step(dt: Double, camera: inout CameraState) {
        guard !interacting, dt.isFinite, dt > 0, simd_length_squared(velocity) > 0 else { return }
        // Exact integral of exponential decay: the glide is the same at 30 and 60 fps.
        let decay = exp(-5*dt), delta = velocity*((1-decay)/5)
        camera.eye += delta; focus += delta; velocity *= decay
        if simd_length(velocity) < 0.05 { velocity = .zero }
    }
    mutating func rebase(by shift: SIMD3<Double>) { focus -= shift }
    mutating func stop() { interacting = false; velocity = .zero }
    static func fallbackFocus(camera: CameraState, distance: Double) -> SIMD3<Double> {
        let ray = camera.forward
        if ray.y < -0.0001 {
            let groundDistance = -camera.eye.y/ray.y
            if groundDistance > 0, groundDistance <= max(600,distance) { return camera.eye+ray*groundDistance }
        }
        return camera.eye+ray*min(600,max(10,distance))
    }
}

enum NavigationPicking {
    // Return distance and barycentric coordinates, also used to reject transparent Splats.
    static func triangle(origin: SIMD3<Float>, direction: SIMD3<Float>, a: SIMD3<Float>, b: SIMD3<Float>, c: SIMD3<Float>) -> SIMD3<Float>? {
        let edge1 = b-a, edge2 = c-a, p = simd_cross(direction,edge2)
        let determinant = simd_dot(edge1,p)
        guard abs(determinant) > 1e-8 else { return nil }
        let t = origin-a, u = simd_dot(t,p)/determinant
        guard u >= 0, u <= 1 else { return nil }
        let q = simd_cross(t,edge1), v = simd_dot(direction,q)/determinant
        guard v >= 0, u+v <= 1 else { return nil }
        let distance = simd_dot(edge2,q)/determinant
        return distance >= 0.5 ? SIMD3(distance,u,v) : nil
    }
    static func sphere(origin: SIMD3<Float>, direction: SIMD3<Float>, center: SIMD3<Float>, radius: Float) -> Bool {
        let delta = center-origin, along = simd_dot(delta,direction)
        return along+radius >= 0 && simd_length_squared(delta)-along*along <= radius*radius
    }
}
