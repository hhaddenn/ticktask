import { useState } from "react";
import { apiFetch } from "../api";
import Button from "./ui/Button";
import { Input, Textarea } from "./ui/Input";

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
			<div className="flex flex-col gap-1.5">
				<label
					htmlFor="name"
					className="text-sm font-medium text-slate-700 dark:text-slate-300"
				>
					Name
				</label>
				<Input
					name="name"
					id="name"
					value={name}
					onChange={(e) => setName(e.target.value)}
					required
				/>
				{errors.name?.[0] && (
					<p className="text-sm text-red-600 dark:text-red-400">
						{errors.name[0]}
					</p>
				)}
			</div>
			<div className="flex flex-col gap-1.5">
				<label
					htmlFor="description"
					className="text-sm font-medium text-slate-700 dark:text-slate-300"
				>
					Description
				</label>
				<Textarea
					name="description"
					id="description"
					value={description}
					onChange={(e) => setDescription(e.target.value)}
				/>
				{errors.description?.[0] && (
					<p className="text-sm text-red-600 dark:text-red-400">
						{errors.description[0]}
					</p>
				)}
			</div>
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
