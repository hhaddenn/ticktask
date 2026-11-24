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

	function applyResponse(data) {
		// Stop returns the closed session; for the UI that means "no timer".
		if (data === null || data.state === "stopped") {
			setEntry(null);
		} else {
			setEntry(data);
		}
		setSyncedAt(performance.now());
		setError(null);
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
		} catch (err) {
			setError(
				err.data?.detail ?? "Could not update the timer. Try again.",
			);
		}
	}

	async function start(taskId) {
		await post("start", { task: taskId });
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

	return { entry, syncedAt, error, start, pause, resume, stop };
}
