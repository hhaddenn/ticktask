import { apiFetch } from "../api";
import ProjectForm from "../components/ProjectForm";
import ProjectList from "../components/ProjectList";
import { useEffect, useState } from "react";

export default function ProjectsPage() {
	const [error, setError] = useState(null);
	const [loading, setLoading] = useState(true);
	const [projects, setProjects] = useState(null);
	const [editingProject, setEditingProject] = useState(null);
	const [showArchived, setShowArchived] = useState(false);

	useEffect(() => {
		let ignore = false;
		async function loadProjects() {
			try {
				const projectList = await apiFetch(
					showArchived
						? "/api/projects/?archived=true"
						: "/api/projects/",
				);
				if (!ignore) {
					setProjects(projectList);
				}
			} catch (error) {
				if (!ignore) {
					setError(error);
				}
			} finally {
				if (!ignore) {
					setLoading(false);
				}
			}
		}
		loadProjects();
		return () => {
			ignore = true;
		};
	}, [showArchived]);

	function handleCreated(project) {
		setProjects([...projects, project]);
	}

	function handleUpdated(updated) {
		setProjects(projects.map((p) => (p.id === updated.id ? updated : p)));
		setEditingProject(null);
	}

	async function handleToggleArchive(project) {
		const action = project.archived_at ? "unarchive" : "archive";
		try {
			await apiFetch(`/api/projects/${project.id}/${action}/`, {
				method: "POST",
			});
			setProjects(projects.filter((p) => p.id !== project.id));
			if (editingProject?.id === project.id) {
				setEditingProject(null);
			}
		} catch (err) {
			console.error(err);
		}
	}

	return loading ? (
		<p className="slate-500 dark:slate-400 text-sm">Loading...</p>
	) : error ? (
		<p className="text-sm text-red-600 dark:text-red-400">
			{error.message}
		</p>
	) : (
		<div className="flex flex-col gap-6">
			{editingProject ? (
				<ProjectForm
					key={editingProject.id}
					project={editingProject}
					onSaved={handleUpdated}
					onCancel={() => setEditingProject(null)}
				/>
			) : (
				!showArchived && <ProjectForm onSaved={handleCreated} />
			)}
			<div className="flex items-center justify-between">
				<h2 className="text-base font-semibold text-slate-900 dark:text-slate-50">
					Projects
				</h2>
				<label
					htmlFor="showArchived"
					className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400"
				>
					<input
						type="checkbox"
						checked={showArchived}
						onChange={(e) => setShowArchived(e.target.checked)}
						name="showArchived"
						id="showArchived"
						className="size-4 accent-accent-700 dark:accent-accent-500"
					/>
					Show Archived
				</label>
			</div>
			<ProjectList
				projects={projects}
				onEdit={setEditingProject}
				onToggleArchive={handleToggleArchive}
			/>
		</div>
	);
}
