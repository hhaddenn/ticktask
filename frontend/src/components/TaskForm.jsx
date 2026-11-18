import { useState } from "react";
import Button from "./ui/Button";
import Field from "./ui/Field";
import { Input, Textarea } from "./ui/Input";
import { apiFetch } from "../api";

export default function TaskForm({ task, onSaved, onCancel }) {
	const [title, setTitle] = useState(task?.title ?? "");
	const [description, setDescription] = useState(task?.description ?? "");
	const [startDate, setStartDate] = useState(task?.start_date ?? "");
	const [dueDate, setDueDate] = useState(task?.due_date ?? "");

	const [errors, setErrors] = useState({});
	const [submitting, setSubmitting] = useState(false);

	async function handleSubmit(event) {
		event.preventDefault();
		try {
			setSubmitting(true);
			const newTask = await apiFetch(
				task ? `/api/tasks/${task.id}/` : "/api/tasks/",
				{
					method: task ? "PATCH" : "POST",
					body: {
						title,
						description,
						start_date: startDate || null,
						due_date: dueDate || null,
					},
				},
			);
			onSaved(newTask);
			if (!task) {
				setTitle("");
				setDescription("");
				setStartDate("");
				setDueDate("");
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
				{task ? "Edit Task" : "New Task"}
			</h2>
			{errors.detail && (
				<p className="text-sm text-red-600 dark:text-red-400">
					{errors.detail}
				</p>
			)}
			<Field label="Title" htmlFor="title" error={errors.title?.[0]}>
				<Input
					name="title"
					id="title"
					value={title}
					onChange={(e) => setTitle(e.target.value)}
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

			<div className="grid grid-cols-2 gap-4">
				<Field
					label="Start Date"
					htmlFor="startDate"
					error={errors.start_date?.[0]}
				>
					<Input
						name="startDate"
						type="date"
						id="startDate"
						value={startDate}
						onChange={(e) => setStartDate(e.target.value)}
					/>
				</Field>
				<Field
					label="Due Date"
					htmlFor="dueDate"
					error={errors.due_date?.[0]}
				>
					<Input
						name="dueDate"
						type="date"
						id="dueDate"
						value={dueDate}
						onChange={(e) => setDueDate(e.target.value)}
					/>
				</Field>
			</div>

			<div className="flex gap-2">
				<Button type="submit" disabled={submitting}>
					{task ? "Save" : "Create"}
				</Button>
				{task && (
					<Button variant="secondary" onClick={onCancel}>
						Cancel
					</Button>
				)}
			</div>
		</form>
	);
}
