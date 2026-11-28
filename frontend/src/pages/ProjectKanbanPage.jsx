import { Link, useParams } from "react-router";
import { useState, useEffect, useEffectEvent } from "react";
import { apiFetch } from "../api";
import KanbanColumn from "../components/KanbanColumn";
import TaskForm from "../components/TaskForm";
import Dialog from "../components/ui/Dialog";
import { DragDropContext } from "@hello-pangea/dnd";
import moveTask from "../kanban";
import TimerConflictDialog from "../components/TimerConflictDialog";
import TimeEntryList from "../components/TimeEntryList";
import { formatMinutes } from "../timer";

export default function ProjectKanbanPage({ timer }) {
	const { projectId } = useParams();
	const [project, setProject] = useState(null);
	const [stages, setStages] = useState([]);
	const [tasks, setTasks] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	const [editingTask, setEditingTask] = useState(null);
	const [moveError, setMoveError] = useState(null);
	const [refreshError, setRefreshError] = useState(null);

	useEffect(() => {
		let ignore = false;
		async function loadProject() {
			try {
				const [projectFetched, projectStages, projectTasks] =
					await Promise.all([
						apiFetch(`/api/projects/${projectId}/`),
						apiFetch(`/api/stages/?project=${projectId}`),
						apiFetch(`/api/tasks/?project=${projectId}`),
					]);
				if (!ignore) {
					setProject(projectFetched);
					setStages(projectStages);
					setTasks(projectTasks);
				}
			} catch (err) {
				if (!ignore) {
					if (err.status === 404) {
						setError(new Error("Project not found."));
					} else {
						setError(err);
					}
				}
			} finally {
				if (!ignore) {
					setLoading(false);
				}
			}
		}
		loadProject();
		return () => {
			ignore = true;
		};
	}, [projectId]);

	function handleTaskCreated(task) {
		setTasks([...tasks, task]);
	}

	function handleTaskSaved(updated) {
		setTasks(tasks.map((t) => (t.id === updated.id ? updated : t)));
		setEditingTask(null);
	}

	function closeDialog() {
		setEditingTask(null);
	}

	async function handleDragEnd(result) {
		if (!result.destination) {
			return;
		}
		if (
			result.source.droppableId === result.destination.droppableId &&
			result.source.index === result.destination.index
		) {
			return;
		}
		const previousTasks = tasks;
		const taskId = Number(result.draggableId);
		const destStage = Number(result.destination.droppableId);
		const position = result.destination.index;
		setMoveError(null);
		setTasks(moveTask(previousTasks, taskId, destStage, position));
		try {
			await apiFetch(`/api/tasks/${taskId}/move/`, {
				method: "POST",
				body: {
					stage: destStage,
					position,
				},
			});
		} catch (err) {
			setTasks(previousTasks);
			console.error(err);
			setMoveError("Could not move the task. Try again.");
		}
	}

	function applyFreshTask(task) {
		// prevTasks, not tasks: a drag and drop may have changed the list while the
		// request was in flight, and this render's tasks would undo it.
		setTasks((prevTasks) =>
			prevTasks.map((t) => (t.id === task.id ? task : t)),
		);
		setRefreshError(null);
	}

	function showRefreshError(err) {
		console.error(err);
		setRefreshError("Couldn't refresh the task's total. Reload the page.");
	}

	// Re-fetches instead of adding the minutes here: the server owns the total
	// (rounding, open sessions), so the card shows exactly what the API sums.
	async function refreshTask(taskId) {
		try {
			applyFreshTask(await apiFetch(`/api/tasks/${taskId}/`));
		} catch (err) {
			showRefreshError(err);
		}
	}

	// An effect event: the effect reads the latest tasks through it without
	// depending on them, so it runs once per stop and not on every task change.
	const isOnThisPage = useEffectEvent((taskId) =>
		tasks.some((t) => t.id === taskId),
	);

	// Refreshes the stopped task's total, whichever place the stop came from (the
	// card, the conflict dialog or the forgotten session dialog in AppLayout).
	// Fetches here instead of calling refreshTask: the lint rule
	// react-hooks/set-state-in-effect only allows setState in a callback of the
	// effect (the .then), not in a function the effect calls directly.
	useEffect(() => {
		const taskId = timer.lastStopped?.task;
		// The timer is app-wide: a stop on another project's task has nothing to
		// refresh here.
		if (!taskId || !isOnThisPage(taskId)) {
			return;
		}
		let ignore = false;
		apiFetch(`/api/tasks/${taskId}/`).then(
			(task) => {
				if (!ignore) {
					applyFreshTask(task);
				}
			},
			(err) => {
				if (!ignore) {
					showRefreshError(err);
				}
			},
		);
		return () => {
			ignore = true;
		};
	}, [timer.lastStopped]);

	const pendingTask = tasks.find((t) => t.id === timer.pendingTaskId);
	const loggedMinutes = tasks.reduce(
		(sum, task) => sum + task.logged_minutes,
		0,
	);

	return (
		<div className="flex flex-col gap-4">
			<Link
				to="/"
				className="text-sm text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-50"
			>
				← Projects
			</Link>
			{loading ? (
				<p className="text-sm text-slate-500 dark:text-slate-400">
					Loading...
				</p>
			) : error ? (
				<p className="text-sm text-red-600 dark:text-red-400">
					{error.message}
				</p>
			) : (
				<>
					<div className="flex items-center gap-2">
						<h2 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
							{project.name}
						</h2>
						<span className="text-sm text-slate-500 dark:text-slate-400">
							<span>Logged </span>
							<span className="font-mono tabular-nums">
								{formatMinutes(loggedMinutes)}
							</span>
						</span>

						{project.archived_at && (
							<span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
								Archived
							</span>
						)}
					</div>

					<Dialog open={editingTask !== null} onClose={closeDialog}>
						{editingTask && (
							<div className="flex flex-col gap-4">
								<TaskForm
									key={editingTask.id}
									task={editingTask}
									onCancel={closeDialog}
									onSaved={handleTaskSaved}
								/>
								<TimeEntryList
									taskId={editingTask.id}
									onEntriesChanged={() =>
										refreshTask(editingTask.id)
									}
								/>
							</div>
						)}
					</Dialog>
					{moveError && (
						<p className="text-sm text-red-600 dark:text-red-400">
							{moveError}
						</p>
					)}
					{refreshError && (
						<p className="text-sm text-red-600 dark:text-red-400">
							{refreshError}
						</p>
					)}
					{timer.error && (
						<p className="text-sm text-red-600 dark:text-red-400">
							{timer.error}
						</p>
					)}

					<Dialog
						open={pendingTask !== undefined}
						onClose={timer.cancelStart}
					>
						{pendingTask && (
							<TimerConflictDialog
								activeTaskTitle={timer.entry.task_title}
								activeProjectName={timer.entry.project_name}
								pendingTaskTitle={pendingTask.title}
								onContinue={timer.cancelStart}
								onSwitch={timer.confirmStart}
							/>
						)}
					</Dialog>

					<DragDropContext onDragEnd={handleDragEnd}>
						<ul className="flex items-start gap-4 overflow-x-auto pb-2">
							{stages.map((stage) => (
								<KanbanColumn
									key={stage.id}
									stage={stage}
									tasks={tasks
										.filter(
											(task) => task.stage === stage.id,
										)
										.toSorted(
											(a, b) => a.sequence - b.sequence,
										)}
									onEditTask={setEditingTask}
									onTaskCreated={handleTaskCreated}
									readOnly={Boolean(project.archived_at)}
									timer={timer}
								/>
							))}
						</ul>
					</DragDropContext>
				</>
			)}
		</div>
	);
}
