import { useState } from "react";
import { apiFetch } from "../api";

export default function ProjectForm({ onSaved, project, onCancel }) {
	const [name, setName] = useState(project?.name ?? "");
	const [description, setDescription] = useState(project?.description ?? "");
	const [errors, setErrors] = useState({});
	const [submitting, setSubmitting] = useState(false);

	async function handleSubmit(event) {
		event.preventDefault();
		try {
			setSubmitting(true);
			const newProject = await apiFetch(
				project ? `/api/projects/${project.id}/` : "/api/projects/",
				{
					method: project ? "PATCH" : "POST",
					body: { name, description },
				},
			);
			onSaved(newProject);
			if (!project) {
				setName("");
				setDescription("");
			}
			setErrors({});
		} catch (err) {
			if (err.status === 400) {
				setErrors(err.data);
			} else {
				setErrors({ detail: err.data?.detail ?? err.message });
			}
		} finally {
			setSubmitting(false);
		}
	}

	return (
		<form onSubmit={handleSubmit}>
			{errors.detail && <p>{errors.detail}</p>}
			<label htmlFor="name">Name</label>
			<input
				type="text"
				name="name"
				id="name"
				value={name}
				onChange={(e) => setName(e.target.value)}
				required
			/>
			{errors.name?.[0] && <p>{errors.name[0]}</p>}
			<label htmlFor="description">Description</label>
			<textarea
				name="description"
				id="description"
				value={description}
				onChange={(e) => setDescription(e.target.value)}
			></textarea>
			{errors.description?.[0] && <p>{errors.description[0]}</p>}
			<button type="submit" disabled={submitting}>
				{project ? "Save" : "Create"}
			</button>
			{project && (
				<button type="button" onClick={onCancel}>
					Cancel
				</button>
			)}
		</form>
	);
}
