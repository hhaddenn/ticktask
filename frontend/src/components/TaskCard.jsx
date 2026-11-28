import Button from "./ui/Button";
import TimerDisplay from "./TimerDisplay";
import { formatMinutes } from "../timer";

export default function TaskCard({
	task,
	onEdit,
	ref,
	isDragging,
	timer,
	readOnly,
	...props
}) {
	const dueDate = task.due_date ? new Date(task.due_date) : null;
	const entry = timer.entry?.task === task.id ? timer.entry : null;
	const running = entry?.state === "running";
	const formattedMinutes = formatMinutes(task.logged_minutes);
	return (
		<li
			className={`flex flex-col gap-1 rounded-xl bg-white p-3 text-sm ${isDragging ? "shadow-md" : "shadow-xs"} ${running ? "ring-2 ring-accent-600/50 dark:ring-accent-400/50" : "ring-1 ring-slate-900/10 dark:ring-white/10"} text-slate-800 focus-visible:outline-2 focus-visible:outline-accent-700 dark:bg-slate-800 dark:text-slate-100 dark:focus-visible:outline-accent-400`}
			ref={ref}
			{...props}
		>
			<span>{task.title}</span>
			{dueDate && (
				<span className="text-xs text-slate-500 dark:text-slate-400">
					{dueDate.toLocaleDateString(undefined, {
						timeZone: "UTC",
						day: "numeric",
						month: "short",
					})}
				</span>
			)}
			{task.logged_minutes > 0 && (
				<span className="text-xs text-slate-500 dark:text-slate-400">
					<span className="sr-only text-sm">Logged time: </span>
					<span className="font-mono tabular-nums">
						{formattedMinutes}
					</span>
				</span>
			)}

			<div
				className={`flex items-center gap-2 ${entry ? "justify-between" : "justify-end"}`}
			>
				{entry && (
					<TimerDisplay
						seconds={entry.elapsed_seconds}
						syncedAt={timer.syncedAt}
						running={running}
					/>
				)}
				{!readOnly &&
					(entry ? (
						running ? (
							<div className="flex gap-1">
								<Button
									variant="ghost"
									onClick={() => timer.pause()}
								>
									Pause
								</Button>
								<Button
									variant="ghost"
									onClick={() => timer.stop()}
								>
									Stop
								</Button>
							</div>
						) : (
							<div className="flex gap-1">
								<Button
									variant="ghost"
									onClick={() => timer.resume()}
								>
									Resume
								</Button>
								<Button
									variant="ghost"
									onClick={() => timer.stop()}
								>
									Stop
								</Button>
							</div>
						)
					) : (
						<Button
							variant="ghost"
							onClick={() => timer.start(task.id)}
						>
							Start
						</Button>
					))}
			</div>
			<Button variant="ghost" onClick={() => onEdit(task)}>
				Edit
			</Button>
		</li>
	);
}
