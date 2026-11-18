import Button from "./ui/Button";

export default function TaskCard({ task, onEdit, ref, isDragging, ...props }) {
	const dueDate = task.due_date ? new Date(task.due_date) : null;
	return (
		<li
			className={`flex flex-col gap-1 rounded-xl bg-white p-3 text-sm ${isDragging ? "shadow-md" : "shadow-xs"} text-slate-800 ring-1 ring-slate-900/10 focus-visible:outline-2 focus-visible:outline-accent-700 dark:bg-slate-800 dark:text-slate-100 dark:ring-white/10 dark:focus-visible:outline-accent-400`}
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
			<Button variant="ghost" onClick={() => onEdit(task)}>
				Edit
			</Button>
		</li>
	);
}
