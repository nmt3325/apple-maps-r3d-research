import Foundation
import simd

@main struct NavigationChecks {
    static func main() {
        func pair(center: SIMD2<Double>, angle: Double = 0, span: Double = 100) -> [SIMD2<Double>] {
            let offset = SIMD2(cos(angle),sin(angle))*(span/2)
            return [center-offset,center+offset]
        }
        var input = NavigationTouchInput()
        _ = input.update(points:[SIMD2(100,200)],time:0)
        let pan = input.update(points:[SIMD2(130,215)],time:0.05)
        precondition(pan.delta == SIMD2(30,15) && !pan.modeChanged)
        let release = input.update(points:[],time:0.06)
        precondition(release.releaseVelocity == SIMD2(600,300), "Flick must retain the measured velocity")
        _ = input.update(points:[SIMD2(100,200)],time:1)
        _ = input.update(points:[SIMD2(130,215)],time:1.05)
        precondition(input.update(points:[],time:1.5).releaseVelocity == .zero, "Holding still must suppress inertia")

        _ = input.update(points:[SIMD2(100,200)],time:2)
        let second = input.update(points:[SIMD2(100,200),SIMD2(200,200)],time:2.01)
        precondition(second.modeChanged && second.delta == .zero && second.twist == 0 && second.zoom == 1)
        let tilt = input.update(points:[SIMD2(100,170),SIMD2(200,170)],time:2.02)
        precondition(tilt.operation == .tilt && tilt.delta.y == -30 && tilt.twist == 0 && tilt.zoom == 1)
        let ignoredTwist = input.update(points:[SIMD2(150,120),SIMD2(150,220)],time:2.03)
        precondition(ignoredTwist.operation == .tilt && ignoredTwist.delta == .zero && ignoredTwist.twist == 0 && ignoredTwist.zoom == 1,
            "Once tilt starts, twisting must not change rotation")
        let mixedTilt = input.update(points:pair(center:SIMD2(150,190),angle:0.9,span:160),time:2.04)
        precondition(mixedTilt.operation == .tilt && mixedTilt.delta.y == 20 && mixedTilt.twist == 0 && mixedTilt.zoom == 1)
        _ = input.update(points:[],time:2.05)
        _ = input.update(points:[SIMD2(100,170),SIMD2(200,170)],time:2.06)
        let twist = input.update(points:[SIMD2(150,120),SIMD2(150,220)],time:2.07)
        precondition(twist.operation == .twist && abs(twist.twist - .pi/2) < 1e-9 && twist.delta == .zero && twist.zoom == 1)
        let mixedTwist = input.update(points:pair(center:SIMD2(200,230),angle:1.9,span:160),time:2.08)
        precondition(mixedTwist.operation == .twist && mixedTwist.delta == .zero && mixedTwist.zoom == 1 && abs(mixedTwist.twist) > 0.1,
            "Once twist starts, sliding and pinching must be ignored")
        let single = input.update(points:[SIMD2(150,120)],time:2.09)
        precondition(single.modeChanged && single.delta == .zero && single.twist == 0)
        precondition(input.update(points:[],time:2.10).releaseVelocity == .zero, "Lifting a finger after orbiting must not fling")
        _ = input.update(points:[SIMD2(0,0),SIMD2(-100,1)],time:3)
        let wrapped = input.update(points:[SIMD2(0,0),SIMD2(-100,-1)],time:3.01)
        precondition(wrapped.operation == nil && wrapped.twist == 0, "Crossing +/- pi must not count as a full turn")
        let wrappedTwist = input.update(points:pair(center:SIMD2(-50,0),angle: -.pi+0.15),time:3.02)
        precondition(wrappedTwist.operation == .twist && abs(wrappedTwist.twist) < 0.2)

        input = NavigationTouchInput()
        _ = input.update(points:pair(center:SIMD2(150,200)),time:4)
        let wobble = input.update(points:pair(center:SIMD2(150,201),angle:0.005,span:101),time:4.01)
        precondition(wobble.operation == nil && wobble.delta == .zero && wobble.twist == 0 && wobble.zoom == 1)
        let pinch = input.update(points:pair(center:SIMD2(150,204),angle:0.02,span:120),time:4.02)
        precondition(pinch.operation == .zoom && pinch.delta == .zero && pinch.twist == 0 && abs(pinch.zoom-1.2) < 1e-9,
            "Dominant pinch must win over small tilt and twist")
        let mixedPinch = input.update(points:pair(center:SIMD2(150,260),angle:1.2,span:156),time:4.03)
        precondition(mixedPinch.operation == .zoom && mixedPinch.delta == .zero && mixedPinch.twist == 0 && abs(mixedPinch.zoom-1.3) < 1e-9)
        _ = input.update(points:[],time:4.04)
        _ = input.update(points:pair(center:SIMD2(150,200)),time:4.05)
        _ = input.update(points:pair(center:SIMD2(150,202)),time:4.06)
        _ = input.update(points:pair(center:SIMD2(150,204)),time:4.07)
        let accumulatedTilt = input.update(points:pair(center:SIMD2(150,207)),time:4.08)
        precondition(accumulatedTilt.operation == .tilt && accumulatedTilt.delta.y == 7,
            "Intent must accumulate from touch-down; the first accepted movement must not be lost")

        var directionCamera = CameraState(), directionNavigation = CameraNavigation()
        let directionInitial = directionCamera, directionTarget = directionCamera.eye+directionCamera.forward*100
        directionNavigation.begin(camera:directionCamera,focus:directionTarget,viewportHeight:800)
        directionNavigation.apply(tilt,viewportHeight:800,camera:&directionCamera)
        precondition(directionCamera.pitch > directionInitial.pitch && directionCamera.yaw == directionInitial.yaw,
            "Upward slide must reverse the previous tilt direction and leave yaw unchanged")
        directionCamera = directionInitial
        directionNavigation.begin(camera:directionCamera,focus:directionTarget,viewportHeight:800)
        directionNavigation.apply(twist,viewportHeight:800,camera:&directionCamera)
        precondition(directionCamera.yaw < directionInitial.yaw && directionCamera.pitch == directionInitial.pitch,
            "Clockwise twist must reverse the previous yaw direction and leave pitch unchanged")
        directionCamera = directionInitial
        directionNavigation.begin(camera:directionCamera,focus:directionTarget,viewportHeight:800)
        directionNavigation.apply(pinch,viewportHeight:800,camera:&directionCamera)
        precondition(directionCamera.yaw == directionInitial.yaw && directionCamera.pitch == directionInitial.pitch &&
            simd_distance(directionCamera.eye,directionTarget) < 100, "Pinch changes distance only")
        let floorTarget = CameraNavigation.fallbackFocus(camera:directionInitial,distance:350)
        directionCamera = directionInitial
        directionNavigation.begin(camera:directionCamera,focus:floorTarget,viewportHeight:800)
        directionNavigation.zoom(scale:1000,camera:&directionCamera)
        precondition(directionCamera.eye.y >= 2-1e-9 && directionCamera.pitch == directionInitial.pitch,
            "Ground limit during zoom must not introduce a tilt")

        var camera = CameraState(), navigation = CameraNavigation()
        let initial = camera, target = camera.eye+camera.forward*100
        navigation.begin(camera:camera,focus:target,viewportHeight:800)
        navigation.pan(SIMD2(40,20),camera:&camera)
        precondition(camera.eye.x < initial.eye.x && camera.eye.z < initial.eye.z && camera.eye.y == initial.eye.y)
        precondition(camera.yaw == initial.yaw && camera.pitch == initial.pitch, "Single finger changes position, not orientation")
        navigation.endPan(pointsPerSecond:SIMD2(400,200),camera:camera)
        let released = camera.eye, speed = simd_length(navigation.velocity)
        navigation.step(dt:0.1,camera:&camera)
        precondition(simd_distance(camera.eye,released) > 0.1 && simd_length(navigation.velocity) < speed)
        for _ in 0..<300 { navigation.step(dt:1/60,camera:&camera) }
        precondition(navigation.velocity == .zero)
        let stopped = camera.eye; navigation.step(dt:1,camera:&camera)
        precondition(camera.eye == stopped)

        var slowCamera = initial, fastCamera = initial
        var slow = CameraNavigation(), fast = CameraNavigation()
        slow.begin(camera:initial,focus:target,viewportHeight:800); fast = slow
        slow.endPan(pointsPerSecond:SIMD2(400,200),camera:slowCamera); fast.endPan(pointsPerSecond:SIMD2(400,200),camera:fastCamera)
        for _ in 0..<30 { slow.step(dt:1/30,camera:&slowCamera) }
        for _ in 0..<60 { fast.step(dt:1/60,camera:&fastCamera) }
        precondition(simd_distance(slowCamera.eye,fastCamera.eye) < 1e-9, "Inertia must be independent of frame rate")

        camera = initial; navigation.begin(camera:camera,focus:target,viewportHeight:800)
        let radius = simd_distance(camera.eye,target)
        navigation.orbit(azimuth:0.4,elevation:-0.2,camera:&camera)
        precondition(simd_distance(camera.eye,initial.eye) > 1 && simd_distance(navigation.focus,target) == 0)
        precondition(abs(simd_distance(camera.eye,target)-radius) < 1e-9)
        precondition(simd_distance(camera.eye+camera.forward*radius,target) < 1e-9, "Orbit target must remain on the center ray")
        let viewProjection = camera.projection(far:350)*camera.view
        let clip = simd_mul(viewProjection,SIMD4<Float>(SIMD3<Float>(target),1))
        precondition(abs(clip.x/clip.w) < 1e-6 && abs(clip.y/clip.w) < 1e-6)
        navigation.orbit(azimuth:0,elevation:100,camera:&camera)
        precondition(camera.eye.y >= 2-1e-9 && simd_distance(camera.eye+camera.forward*radius,target) < 1e-9)
        let shift = SIMD3<Double>(3000,0,-3000)
        navigation.rebase(by:shift); camera.eye -= shift
        precondition(simd_distance(camera.eye+camera.forward*radius,navigation.focus) < 1e-9)
        navigation.endOrbit(); precondition(navigation.velocity == .zero)
        navigation.stop(); precondition(!navigation.interacting && navigation.velocity == .zero)
        let fallback = CameraNavigation.fallbackFocus(camera:initial,distance:350)
        precondition(abs(fallback.y) < 1e-9 && simd_length(simd_cross(fallback-initial.eye,initial.forward)) < 1e-9)

        let origin = SIMD3<Float>(0,0,10), direction = SIMD3<Float>(0,0,-1)
        let hit = NavigationPicking.triangle(origin:origin,direction:direction,a:SIMD3(-2,-2,0),b:SIMD3(2,-2,0),c:SIMD3(0,2,0))!
        precondition(abs(hit.x-10) < 1e-6 && hit.y >= 0 && hit.z >= 0 && hit.y+hit.z <= 1)
        precondition(NavigationPicking.triangle(origin:origin,direction:-direction,a:SIMD3(-2,-2,0),b:SIMD3(2,-2,0),c:SIMD3(0,2,0)) == nil)
        precondition(NavigationPicking.sphere(origin:origin,direction:direction,center:.zero,radius:2))
        precondition(!NavigationPicking.sphere(origin:origin,direction:direction,center:SIMD3(20,0,0),radius:2))
        print("PASS: exclusive tilt/twist/pinch, reversed directions, intent threshold/lock/reset, touch transitions, angle wrap, pan/inertia/frame rate, fixed orbit center, altitude limit, rebase, fallback, ray picking")
    }
}
