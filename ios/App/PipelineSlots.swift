import Foundation

// Limit expensive preparation separately from the two network requests.
// Waiting tasks hold only bounded raw responses and remain cancellable.
@MainActor
final class PipelineSlots {
    let limit: Int
    private(set) var active = 0
    private var waiters: [(UUID, CheckedContinuation<Void,Error>)] = []

    init(limit: Int) { precondition(limit > 0); self.limit = limit }

    func withSlot<T>(operation: () async throws -> T) async throws -> T {
        try await acquire()
        defer { release() }
        try Task.checkCancellation()
        return try await operation()
    }

    private func acquire() async throws {
        try Task.checkCancellation()
        let id = UUID()
        try await withTaskCancellationHandler(operation: {
            try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void,Error>) in
                if Task.isCancelled { continuation.resume(throwing:CancellationError()) }
                else if active < limit { active += 1; continuation.resume() }
                else { waiters.append((id,continuation)) }
            }
        }, onCancel: {
            Task { @MainActor in self.cancel(id) }
        })
    }

    private func cancel(_ id: UUID) {
        guard let index = waiters.firstIndex(where:{$0.0 == id}) else { return }
        waiters.remove(at:index).1.resume(throwing:CancellationError())
    }

    private func release() {
        if waiters.isEmpty { active -= 1 }
        else { waiters.removeFirst().1.resume() }
    }
}
