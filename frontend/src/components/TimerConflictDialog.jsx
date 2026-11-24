import Button from "./ui/Button";

export default function TimerConflictDialog({
	activeTaskTitle,
	activeProjectName,
	pendingTaskTitle,
	onContinue,
	onSwitch,
}) {
	return (
		<div className="flex flex-col gap-4 rounded-xl bg-white p-5 shadow-xs ring-1 ring-slate-900/10 dark:bg-slate-900 dark:ring-white/10">
			<p className="text-sm text-slate-700 dark:text-slate-300">
				The timer is running in {activeTaskTitle} ({activeProjectName})
			</p>
			<div className="flex justify-end gap-2">
				<Button onClick={onSwitch}>
					Stop {activeTaskTitle} and start {pendingTaskTitle}
				</Button>
				<Button onClick={onContinue} variant="secondary">
					Continue {activeTaskTitle}
				</Button>
			</div>
		</div>
	);
}
