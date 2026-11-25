import { useState } from "react";
import Button from "./ui/Button";
import Field from "./ui/Field";
import { Input } from "./ui/Input";

export default function ForgottenSessionDialog({
	entry,
	error,
	onStop,
	onStopAndRestart,
	onDismiss,
}) {
	const [endedAt, setEndedAt] = useState("");
	// Only a running session needs the time: a paused one is closed now and the
	// total is already right, because pauses don't count (timer.md rule 3).
	const isRunning = entry.state === "running";
	// Stopping a running session "now" would log the whole night as work.
	const missingTime = isRunning && endedAt === "";

	function endedAtIso() {
		if (!isRunning) {
			return undefined;
		}
		// datetime-local gives "2026-11-24T18:30" with no time zone. new Date()
		// reads it as the PC's local time and toISOString() sends it as UTC, so
		// the server knows which instant it is.
		return new Date(endedAt).toISOString();
	}

	return (
		<div className="flex flex-col gap-4 rounded-xl bg-white p-5 shadow-xs ring-1 ring-slate-900/10 dark:bg-slate-900 dark:ring-white/10">
			<p className="text-sm text-slate-700 dark:text-slate-300">
				You have a session open since {entry.date}: {entry.task_title} (
				{entry.project_name})
			</p>
			{isRunning ? (
				<Field
					label="When did you stop working?"
					htmlFor="forgotten-ended-at"
					error={error}
				>
					<Input
						id="forgotten-ended-at"
						type="datetime-local"
						value={endedAt}
						onChange={(e) => setEndedAt(e.target.value)}
					/>
				</Field>
			) : (
				error && (
					<p className="text-sm text-red-600 dark:text-red-400">
						{error}
					</p>
				)
			)}
			<div className="flex flex-wrap justify-end gap-2">
				<Button
					onClick={() => onStop(endedAtIso())}
					disabled={missingTime}
				>
					Close session
				</Button>
				<Button
					variant="secondary"
					onClick={() => onStopAndRestart(endedAtIso())}
					disabled={missingTime}
				>
					Close and start new now
				</Button>
				<Button variant="ghost" onClick={onDismiss}>
					Ignore
				</Button>
			</div>
		</div>
	);
}
