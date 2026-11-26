import { useState, useEffect } from "react";
import { apiFetch } from "../api";
import { formatMinutes } from "../timer";
import TimeEntryForm from "./TimeEntryForm";
import Button from "./ui/Button";

export default function TimeEntryList({ taskId }) {
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	const [entryList, setEntryList] = useState([]);
	const [editingId, setEditingId] = useState(null);
	const [actionError, setActionError] = useState(null);

	function handleEntrySaved(saved) {
		// The filter makes this work for both create (nothing to remove) and edit
		// (removes the old version). Added at the end before sorting: sort is stable,
		// so on a day that already has timer sessions it goes after them, as in the
		// API's order. The new array also keeps sort from changing the state in place.
		const list = [
			...entryList.filter((e) => e.id !== saved.id),
			saved,
		].sort((a, b) => b.date.localeCompare(a.date));
		setEntryList(list);
		setEditingId(null);
	}

	async function handleDelete(entry) {
		if (!window.confirm("Delete this entry?")) {
			return;
		}
		try {
			await apiFetch(`/api/time-entries/${entry.id}/`, {
				method: "DELETE",
			});
			setEntryList(entryList.filter((e) => e.id !== entry.id));
			setActionError(null);
		} catch (err) {
			setActionError(err.data?.detail ?? err.message);
		}
	}

	useEffect(() => {
		// If the dialog switches to another task before this response arrives,
		// the old response must not overwrite the new task's entries.
		let ignore = false;
		async function loadEntries() {
			try {
				const data = await apiFetch(
					`/api/time-entries/?task=${taskId}`,
				);
				if (!ignore) {
					setEntryList(data);
				}
			} catch (err) {
				if (!ignore) {
					setError(err);
				}
			} finally {
				if (!ignore) {
					setLoading(false);
				}
			}
		}
		loadEntries();
		return () => {
			ignore = true;
		};
	}, [taskId]);

	if (loading) {
		return (
			<p className="text-sm text-slate-500 dark:text-slate-400">
				Loading...
			</p>
		);
	}
	if (error) {
		return (
			<p className="text-sm text-red-600 dark:text-red-400">
				{error.message}
			</p>
		);
	}

	return (
		<div className="flex flex-col gap-4 rounded-xl bg-white p-5 shadow-xs ring-1 ring-slate-900/10 dark:bg-slate-900 dark:ring-white/10">
			<h2 className="text-sm font-semibold text-slate-900 dark:text-slate-50">
				Time Entries
			</h2>
			{actionError && (
				<p className="text-sm text-red-600 dark:text-red-400">
					{actionError}
				</p>
			)}
			{entryList.length === 0 ? (
				<p className="text-sm text-slate-500 dark:text-slate-400">
					No time logged yet.
				</p>
			) : (
				<ul className="flex flex-col divide-y divide-slate-200 dark:divide-slate-800">
					{entryList.map((entry) =>
						entry.id === editingId ? (
							<li key={entry.id} className="py-4">
								<TimeEntryForm
									taskId={taskId}
									entry={entry}
									onSaved={handleEntrySaved}
									onCancel={() => setEditingId(null)}
								/>
							</li>
						) : (
							<li
								key={entry.id}
								className="flex items-center gap-2 py-2 text-sm text-slate-700 dark:text-slate-300"
							>
								{/* Shown as the API sends it: new Date("2026-11-26") reads it as
							    UTC midnight, which shows the previous day west of UTC. */}
								<span className="text-slate-500 dark:text-slate-400">
									{entry.date}
								</span>
								<span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
									{entry.source === "timer"
										? "Timer"
										: "Manual"}
								</span>
								<span className="ml-auto font-mono tabular-nums">
									{formatMinutes(entry.minutes)}
								</span>
								<Button
									variant="ghost"
									onClick={() => setEditingId(entry.id)}
								>
									Edit
								</Button>
								<Button
									variant="danger"
									onClick={() => handleDelete(entry)}
								>
									Delete
								</Button>
							</li>
						),
					)}
				</ul>
			)}
			<TimeEntryForm taskId={taskId} onSaved={handleEntrySaved} />
		</div>
	);
}
