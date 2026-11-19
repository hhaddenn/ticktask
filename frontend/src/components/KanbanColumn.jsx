import TaskCard from "./TaskCard";
import QuickAddTask from "./QuickAddTask";
import { Droppable, Draggable } from "@hello-pangea/dnd";

export default function KanbanColumn({
	stage,
	tasks,
	onEditTask,
	onTaskCreated,
	readOnly,
}) {
	return (
		<li className="flex w-72 shrink-0 flex-col gap-2 rounded-xl bg-slate-200/60 p-2 dark:bg-slate-900">
			<h3 className="flex items-center justify-between px-2 py-1 text-sm font-semibold text-slate-600 dark:text-slate-400">
				{stage.name}
				<span className="font-normal text-slate-500 dark:text-slate-400">
					{tasks.length}
				</span>
			</h3>
			<Droppable droppableId={String(stage.id)}>
				{(provided, snapshot) => (
					<ul
						className={`flex min-h-16 flex-col gap-2 rounded-lg ${snapshot.isDraggingOver ? "bg-accent-600/10 dark:bg-accent-400/10" : ""}`}
						ref={provided.innerRef}
						{...provided.droppableProps}
					>
						{tasks.map((task, i) => (
							<Draggable
								key={task.id}
								draggableId={String(task.id)}
								index={i}
								isDragDisabled={readOnly}
							>
								{(provided, snapshot) => (
									<TaskCard
										task={task}
										onEdit={onEditTask}
										isDragging={snapshot.isDragging}
										ref={provided.innerRef}
										{...provided.draggableProps}
										{...provided.dragHandleProps}
									/>
								)}
							</Draggable>
						))}
						{tasks.length === 0 && !snapshot.isDraggingOver && (
							<li className="px-2 py-3 text-sm text-slate-500 dark:text-slate-400">
								No tasks.
							</li>
						)}
						{provided.placeholder}
					</ul>
				)}
			</Droppable>
			<QuickAddTask
				projectId={stage.project}
				stageId={stage.id}
				onCreated={onTaskCreated}
			/>
		</li>
	);
}
