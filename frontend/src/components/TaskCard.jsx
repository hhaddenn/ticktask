export default function TaskCard({ task, onEdit }) {
	const dueDate = task.due_date ? new Date(task.due_date) : null;
	return (
		<li className="flex flex-col gap-1 rounded-xl bg-white p-3 text-sm text-slate-800 shadow-xs ring-1 ring-slate-900/10 dark:bg-slate-800 dark:text-slate-100 dark:ring-white/10">
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
			<button
				onClick={() => onEdit(task)}
				className="focus-visible: w-full text-left"
			>
				Edit
			</button>
		</li>
	);
}
