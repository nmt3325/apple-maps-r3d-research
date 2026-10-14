import Foundation

@main struct PipelineChecks {
    @MainActor static func main() async throws {
        let slots = PipelineSlots(limit:2)
        var releases: [CheckedContinuation<Void,Never>] = []
        var started = 0
        func job() -> Task<Void,Error> {
            Task { @MainActor in
                try await slots.withSlot {
                    started += 1
                    await withCheckedContinuation { releases.append($0) }
                }
            }
        }
        let first = job(), second = job()
        while started < 2 { await Task.yield() }
        let cancelled = job()
        await Task.yield()
        cancelled.cancel()
        do { try await cancelled.value; preconditionFailure("Cancelled waiter ran") }
        catch is CancellationError { }
        precondition(started == 2 && slots.active == 2)
        let next = job()
        releases.removeFirst().resume()
        while started < 3 { await Task.yield() }
        precondition(slots.active == 2, "Released slot must transfer to the next waiter")
        for release in releases { release.resume() }
        try await first.value; try await second.value; try await next.value
        precondition(slots.active == 0)
        do {
            try await slots.withSlot { throw CancellationError() }
        } catch is CancellationError { }
        precondition(slots.active == 0, "Errors must release a slot")
        print("PASS: preparation limit, cancelled waiters, FIFO transfer, and release after errors")
    }
}
