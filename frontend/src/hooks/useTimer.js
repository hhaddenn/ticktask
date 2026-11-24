import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function useTimer() {
	const [entry, setEntry] = useState(null);
	// Anchor for the live counter: when the server's elapsed_seconds arrived. The
	// display adds the local time passed since then, instead of counting on its
	// own, so the server stays the source of truth (timer.md rule 5).
	// performance.now() and not Date.now(): it never jumps if the PC clock is set.
	const [syncedAt, setSyncedAt] = useState(null);
	const [error, setError] = useState(null);
	const [pendingTaskId, setPendingTaskId] = useState(null);

	function applyResponse(data) {
		// Stop returns the closed session; for the UI that means "no timer".
		if (data === null || data.state === "stopped") {
			setEntry(null);
		} else {
			setEntry(data);
		}
		setSyncedAt(performance.now());
		setError(null);
		// The warning was asked about the previous server state: any new state makes
		// it stale. If the conflict still exists, the next start shows it again.
		setPendingTaskId(null);
	}

	useEffect(() => {
		// Drops a response that arrives after unmount (StrictMode mounts twice in dev).
		let ignore = false;
		async function loadOpenEntry() {
			try {
				const data = await apiFetch("/api/timer/");
				if (!ignore) {
					applyResponse(data);
				}
			} catch (err) {
				if (!ignore) {
					setError(
						err.data?.detail ??
							"Could not load open entry. Try again.",
					);
				}
			}
		}
		loadOpenEntry();
		return () => {
			ignore = true;
		};
	}, []);

	async function post(action, body) {
		try {
			const data = await apiFetch(`/api/timer/${action}/`, {
				method: "POST",
				body,
			});
			applyResponse(data);
			return true;
		} catch (err) {
			setError(
				err.data?.detail ?? "Could not update the timer. Try again.",
			);
			return false;
		}
	}

	async function start(taskId) {
		// The server would reject this with 409 anyway, but checking here first lets
		// the user choose what to do (timer.md rule 2) instead of only seeing an error.
		// The 409 is still the real guard, for when this state is out of date.
		if (entry && entry.task !== taskId) {
			setPendingTaskId(taskId);
			return;
		}
		try {
			const data = await apiFetch("/api/timer/start/", {
				method: "POST",
				body: { task: taskId },
			});
			applyResponse(data);
		} catch (err) {
			if (err.status === 409) {
				// A 409 means this tab's state is out of date (e.g. another tab started a
				// timer): reload the open session from the server and decide from that,
				// not from `entry`, which is still the old state in this render.
				try {
					const result = await apiFetch("/api/timer/");
					applyResponse(result);
					// After applyResponse, because it clears pendingTaskId.
					if (result === null) {
						setError(
							"The timer changed in another tab. Try again.",
						);
					} else if (result.task !== taskId) {
						setPendingTaskId(taskId);
					}
				} catch (getErr) {
					setError(
						getErr.data?.detail ??
							"Could not update the timer. Try again.",
					);
				}
			} else {
				setError(
					err.data?.detail ??
						"Could not update the timer. Try again.",
				);
			}
		}
	}

	async function pause() {
		await post("pause");
	}

	async function resume() {
		await post("resume");
	}
	async function stop() {
		await post("stop");
	}

	function cancelStart() {
		setPendingTaskId(null);
	}

	async function confirmStart() {
		// Calls post() directly, not stop() and start(): this render's `entry` is
		// still the old session after the stop, so start() would see the conflict
		// again and only reopen the warning. The id is kept before the stop because
		// its response clears pendingTaskId.
		const taskId = pendingTaskId;
		const stopped = await post("stop");
		if (stopped) {
			await post("start", { task: taskId });
		}
	}

	return {
		entry,
		syncedAt,
		error,
		start,
		pause,
		resume,
		stop,
		pendingTaskId,
		cancelStart,
		confirmStart,
	};
}
