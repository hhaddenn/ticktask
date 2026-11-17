import TaskCard from "./TaskCard";

export default function KanbanColumn({ stage, tasks }) {
	return (
		<li className="flex w-72 shrink-0 flex-col gap-2 rounded-xl bg-slate-200/60 p-2 dark:bg-slate-900">
			<h3 className="flex items-center justify-between px-2 py-1 text-sm font-semibold text-slate-600 dark:text-slate-400">
				{stage.name}
				<span className="font-normal text-slate-500 dark:text-slate-400">
					{tasks.length}
				</span>
			</h3>
			{tasks.length ? (
				<ul className="flex flex-col gap-2">
					{tasks.map((task) => (
						<TaskCard key={task.id} task={task} />
					))}
				</ul>
			) : (
				<p className="px-2 py-3 text-sm text-slate-500 dark:text-slate-400">
					No tasks
				</p>
			)}
		</li>
	);
}
