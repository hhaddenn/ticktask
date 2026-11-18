import { useState } from "react";
import { apiFetch } from "../api";
import Button from "./ui/Button";
import { Input } from "./ui/Input";

export default function QuickAddTask({ projectId, stageId, onCreated }) {
	const [adding, setAdding] = useState(false);
	const [title, setTitle] = useState("");
	const [errors, setErrors] = useState({});
	const [submitting, setSubmitting] = useState(false);

	function close() {
		setAdding(false);
		setTitle("");
		setErrors({});
	}

	async function handleSubmit(event) {
		event.preventDefault();
		try {
			setSubmitting(true);
			const newTask = await apiFetch("/api/tasks/", {
				method: "POST",
				body: { project: projectId, stage: stageId, title },
			});
			onCreated(newTask);
			setTitle("");
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

	const errorMessage = errors.title?.[0] ?? errors.detail;

	return adding ? (
		<form onSubmit={handleSubmit} className="flex flex-col gap-1">
			<Input
				autoFocus
				value={title}
				onChange={(e) => setTitle(e.target.value)}
				onKeyDown={(e) => e.key === "Escape" && close()}
				readOnly={submitting}
				aria-label="Task title"
				placeholder="Task title"
				onBlur={(e) => e.target.value === "" && close()}
			/>
			{errorMessage && (
				<p className="text-sm text-red-600 dark:text-red-400">
					{errorMessage}
				</p>
			)}
		</form>
	) : (
		<Button variant="ghost" onClick={() => setAdding(true)}>
			+ Add task
		</Button>
	);
}
