function moveTask(tasks, taskId, stageId, position) {
	const movedTask = tasks.find((task) => task.id === taskId);
	const destStageTasks = tasks
		.filter((task) => task.stage === stageId && task.id !== taskId)
		.toSorted((a, b) => a.sequence - b.sequence);
	const newDestTasks = destStageTasks
		.toSpliced(position, 0, {
			...movedTask,
			stage: stageId,
		})
		.map((t, i) => ({ ...t, sequence: i }));
	const newSourceTasks =
		movedTask.stage === stageId
			? []
			: tasks
					.filter(
						(task) =>
							task.stage === movedTask.stage &&
							task.id !== taskId,
					)
					.toSorted((a, b) => a.sequence - b.sequence)
					.map((t, i) => ({ ...t, sequence: i }));
	const updatedTasks = new Map(
		[...newDestTasks, ...newSourceTasks].map((t) => [t.id, t]),
	);
	return tasks.map((t) => updatedTasks.get(t.id) ?? t);
}

export default moveTask;
