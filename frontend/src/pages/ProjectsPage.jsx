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
		<p>Loading...</p>
	) : error ? (
		<p>{error.message}</p>
	) : (
		<>
			<label htmlFor="showArchived">Show Archived</label>
			<input
				type="checkbox"
				checked={showArchived}
				onChange={(e) => setShowArchived(e.target.checked)}
				name="showArchived"
				id="showArchived"
			/>
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
			<ProjectList
				projects={projects}
				onEdit={setEditingProject}
				onToggleArchive={handleToggleArchive}
			/>
		</>
	);
}
