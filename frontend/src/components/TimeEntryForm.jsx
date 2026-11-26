import { useState } from "react";
import Button from "./ui/Button";
import Field from "./ui/Field";
import { Input } from "./ui/Input";
import { apiFetch } from "../api";

// en-CA formats as YYYY-MM-DD (what <input type="date"> expects) in local time.
// toISOString() would give the UTC day, which is still yesterday right after
// midnight in Lisbon during summer time.
function today() {
	return new Date().toLocaleDateString("en-CA");
}

// Without entry it creates a manual entry; with entry it edits that one.
export default function TimeEntryForm({ taskId, entry, onSaved, onCancel }) {
	const [date, setDate] = useState(entry?.date ?? today);
	const [minutes, setMinutes] = useState(entry ? String(entry.minutes) : "");
	const [description, setDescription] = useState(entry?.description ?? "");
	const [errors, setErrors] = useState({});
	const [submitting, setSubmitting] = useState(false);

	// A timer session's date comes from its start, and the API rejects changing it.
	// It's still sent on save: the API accepts the same date.
	const dateLocked = entry?.source === "timer";
	// Ids must be unique on the page: TaskForm (id="description") and the add form
	// are in the same dialog as the row being edited.
	const idPrefix = entry ? `entry${entry.id}` : "entry";

	async function handleSubmit(event) {
		event.preventDefault();
		try {
			setSubmitting(true);
			const saved = await apiFetch(
				entry ? `/api/time-entries/${entry.id}/` : "/api/time-entries/",
				{
					method: entry ? "PATCH" : "POST",
					body: {
						task: taskId,
						date,
						// Inputs always give a string, even with type="number".
						minutes: Number(minutes),
						description,
					},
				},
			);
			onSaved(saved);
			if (!entry) {
				// The date stays: logging several entries for the same day is the usual case.
				setMinutes("");
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

	// The task error has no field of its own (e.g. archived project), so it's
	// shown at the top with the general one.
	const generalError = errors.detail ?? errors.task?.[0];

	// No top border when editing: the form sits inside a list row, and the list's
	// divide-y already draws the line above it.
	return (
		<form
			onSubmit={handleSubmit}
			className={
				entry
					? "flex flex-col gap-4"
					: "flex flex-col gap-4 border-t border-slate-200 pt-4 dark:border-slate-800"
			}
		>
			{generalError && (
				<p className="text-sm text-red-600 dark:text-red-400">
					{generalError}
				</p>
			)}
			<div className="grid grid-cols-2 gap-4">
				<Field
					label="Date"
					htmlFor={`${idPrefix}Date`}
					error={errors.date?.[0]}
				>
					<Input
						name="date"
						type="date"
						id={`${idPrefix}Date`}
						value={date}
						onChange={(e) => setDate(e.target.value)}
						disabled={dateLocked}
						required
					/>
				</Field>
				<Field
					label="Minutes"
					htmlFor={`${idPrefix}Minutes`}
					error={errors.minutes?.[0]}
				>
					<Input
						name="minutes"
						type="number"
						id={`${idPrefix}Minutes`}
						min="1"
						value={minutes}
						onChange={(e) => setMinutes(e.target.value)}
						required
					/>
				</Field>
			</div>
			<Field
				label="Description"
				htmlFor={`${idPrefix}Description`}
				error={errors.description?.[0]}
			>
				<Input
					name="description"
					id={`${idPrefix}Description`}
					value={description}
					onChange={(e) => setDescription(e.target.value)}
				/>
			</Field>
			<div className="flex gap-2">
				<Button type="submit" disabled={submitting}>
					{entry ? "Save" : "Add"}
				</Button>
				{entry && (
					<Button variant="secondary" onClick={onCancel}>
						Cancel
					</Button>
				)}
			</div>
		</form>
	);
}
