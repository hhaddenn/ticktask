import { useEffect, useState } from "react";
import { formatDuration } from "../timer";

export default function TimerDisplay({ seconds, syncedAt, running }) {
	const [now, setNow] = useState(() => performance.now());

	useEffect(() => {
		if (!running) return;
		const id = setInterval(() => setNow(performance.now()), 1000);
		return () => clearInterval(id);
	}, [running]);

	// Derived from the server's anchor on every tick, never counted with +1:
	// setInterval drifts and is slowed down in background tabs, so a late tick
	// must not add up. Math.max: after a resume, syncedAt is newer than the last
	// tick's `now` until the next tick, which would briefly show less time.
	const value = running
		? seconds + Math.max(0, now - syncedAt) / 1000
		: seconds;

	return (
		<time
			className={`font-mono tabular-nums ${running ? "font-medium text-accent-700 dark:text-accent-400" : "text-slate-500 dark:text-slate-400"}`}
		>
			{formatDuration(value)}
		</time>
	);
}
