import Foundation
import simd

@main struct NavigationChecks {
    static func main() {
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
        precondition(tilt.delta.y == -30 && tilt.twist == 0 && tilt.zoom == 1)
        let twist = input.update(points:[SIMD2(150,120),SIMD2(150,220)],time:2.03)
        precondition(abs(twist.twist - .pi/2) < 1e-9 && abs(twist.delta.y) < 1e-9 && twist.zoom == 1)
        let single = input.update(points:[SIMD2(150,120)],time:2.04)
        precondition(single.modeChanged && single.delta == .zero && single.twist == 0)
        precondition(input.update(points:[],time:2.05).releaseVelocity == .zero, "Lifting a finger after orbiting must not fling")
        _ = input.update(points:[SIMD2(0,0),SIMD2(-100,1)],time:3)
        let wrapped = input.update(points:[SIMD2(0,0),SIMD2(-100,-1)],time:3.01)
        precondition(abs(wrapped.twist) < 0.03, "Crossing +/- pi must not jump by a full turn")

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
        print("PASS: touch transitions, tilt/twist, angle wrap, horizontal pan, inertia/decay/frame rate, fixed orbit center, altitude limit, rebase, fallback, ray picking")
    }
}
