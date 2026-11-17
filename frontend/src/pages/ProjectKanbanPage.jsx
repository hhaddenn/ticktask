import { Link, useParams } from "react-router";
import { useState, useEffect } from "react";
import { apiFetch } from "../api";
import KanbanColumn from "../components/KanbanColumn";

export default function ProjectKanbanPage() {
	const { projectId } = useParams();
	const [project, setProject] = useState(null);
	const [stages, setStages] = useState([]);
	const [tasks, setTasks] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

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
						{project.archived_at && (
							<span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
								Archived
							</span>
						)}
					</div>

					<ul className="flex items-start gap-4 overflow-x-auto pb-2">
						{stages.map((stage) => (
							<KanbanColumn
								key={stage.id}
								stage={stage}
								tasks={tasks.filter(
									(task) => task.stage === stage.id,
								)}
							/>
						))}
					</ul>
				</>
			)}
		</div>
	);
}
