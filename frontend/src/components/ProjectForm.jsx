import { useState } from "react";
import { apiFetch } from "../api";
import Button from "./ui/Button";
import { Input, Textarea } from "./ui/Input";
import Field from "./ui/Field";

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
		<form
			onSubmit={handleSubmit}
			className="flex flex-col gap-4 rounded-xl bg-white p-5 shadow-xs ring-1 ring-slate-900/10 dark:bg-slate-900 dark:ring-white/10"
		>
			<h2 className="text-sm font-semibold text-slate-900 dark:text-slate-50">
				{project ? "Edit Project" : "New Project"}
			</h2>
			{errors.detail && (
				<p className="text-sm text-red-600 dark:text-red-400">
					{errors.detail}
				</p>
			)}
			<Field label="Name" htmlFor="name" error={errors.name?.[0]}>
				<Input
					name="name"
					id="name"
					value={name}
					onChange={(e) => setName(e.target.value)}
					required
				/>
			</Field>
			<Field
				label="Description"
				htmlFor="description"
				error={errors.description?.[0]}
			>
				<Textarea
					name="description"
					id="description"
					value={description}
					onChange={(e) => setDescription(e.target.value)}
				/>
			</Field>
			<div className="flex gap-2">
				<Button type="submit" disabled={submitting}>
					{project ? "Save" : "Create"}
				</Button>
				{project && (
					<Button variant="secondary" onClick={onCancel}>
						Cancel
					</Button>
				)}
			</div>
		</form>
	);
}
