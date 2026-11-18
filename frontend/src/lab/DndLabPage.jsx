import { useState } from "react";
import TaskCard from "../components/TaskCard";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

const stages = [
	{ id: 1, name: "To do" },
	{ id: 2, name: "Doing" },
	{ id: 3, name: "Done" },
];
const initialTasks = [
	{ id: 1, title: "Task A", stage: 1, sequence: 0 },
	{ id: 2, title: "Task B", stage: 1, sequence: 1 },
	{ id: 3, title: "Task C", stage: 1, sequence: 2 },
	{ id: 4, title: "Task D", stage: 2, sequence: 0 },
	{ id: 5, title: "Task E", stage: 2, sequence: 1 },
	{ id: 6, title: "Task F", stage: 2, sequence: 2 },
	{ id: 7, title: "Task G", stage: 2, sequence: 3 },
];

export default function DndLabPage() {
	const [tasks, setTasks] = useState(initialTasks);

	function handleDragEnd(result) {
		if (!result.destination) {
			return;
		}
		if (
			result.source.droppableId === result.destination.droppableId &&
			result.source.index === result.destination.index
		) {
			return;
		}
		const taskId = Number(result.draggableId);
		const destStage = Number(result.destination.droppableId);
		const sourceStage = Number(result.source.droppableId);
		const movedTask = tasks.find((task) => task.id === taskId);
		const destStageTasks = tasks
			.filter((task) => task.stage === destStage && task.id !== taskId)
			.toSorted((a, b) => a.sequence - b.sequence);
		const newDestTasks = destStageTasks
			.toSpliced(result.destination.index, 0, {
				...movedTask,
				stage: destStage,
			})
			.map((t, i) => ({ ...t, sequence: i }));
		const newSourceTasks =
			sourceStage === destStage
				? []
				: tasks
						.filter(
							(task) =>
								task.stage === sourceStage &&
								task.id !== taskId,
						)
						.toSorted((a, b) => a.sequence - b.sequence)
						.map((t, i) => ({ ...t, sequence: i }));
		const updatedTasks = new Map(
			[...newDestTasks, ...newSourceTasks].map((t) => [t.id, t]),
		);
		setTasks(tasks.map((t) => updatedTasks.get(t.id) ?? t));
		console.log("move", taskId, {
			stage: destStage,
			position: result.destination.index,
		});
	}

	return (
		<div className="flex flex-col gap-4">
			<h2 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
				Drag and drop lab
			</h2>
			<DragDropContext onDragEnd={handleDragEnd}>
				<ul className="flex items-start gap-4 overflow-x-auto pb-2">
					{stages.map((stage) => {
						const stageTasks = tasks
							.filter((task) => task.stage === stage.id)
							.toSorted((a, b) => a.sequence - b.sequence);
						return (
							<li
								className="flex w-72 shrink-0 flex-col gap-2 rounded-xl bg-slate-200/60 p-2 dark:bg-slate-900"
								key={stage.id}
							>
								<h3 className="flex items-center justify-between px-2 py-1 text-sm font-semibold text-slate-600 dark:text-slate-400">
									{stage.name}
									<span className="font-normal text-slate-500 dark:text-slate-400">
										{stageTasks.length}
									</span>
								</h3>
								<Droppable droppableId={String(stage.id)}>
									{(provided, snapshot) => (
										<ul
											className={`flex min-h-16 flex-col gap-2 rounded-lg ${snapshot.isDraggingOver ? "bg-accent-600/10 dark:bg-accent-400/10" : ""}`}
											ref={provided.innerRef}
											{...provided.droppableProps}
										>
											{stageTasks.map((task, i) => (
												<Draggable
													key={task.id}
													draggableId={String(
														task.id,
													)}
													index={i}
												>
													{(provided, snapshot) => (
														<TaskCard
															ref={
																provided.innerRef
															}
															{...provided.draggableProps}
															{...provided.dragHandleProps}
															task={task}
															onEdit={(t) =>
																console.log(
																	"edit",
																	t.id,
																)
															}
															isDragging={
																snapshot.isDragging
															}
														/>
													)}
												</Draggable>
											))}
											{provided.placeholder}
										</ul>
									)}
								</Droppable>
							</li>
						);
					})}
				</ul>
			</DragDropContext>
		</div>
	);
}
