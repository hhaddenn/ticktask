import { useState } from "react";
import { apiFetch } from "../api";
import Field from "../components/ui/Field";
import { Input } from "../components/ui/Input";
import Button from "../components/ui/Button";

export default function LoginPage({ onLogin }) {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [submitting, setSubmitting] = useState(false);
	const [error, setError] = useState(null);

	async function handleSubmit(event) {
		event.preventDefault();
		try {
			setSubmitting(true);
			setError(null);
			const user = await apiFetch("/api/auth/login/", {
				method: "POST",
				body: { username, password },
			});
			// The login endpoint already returns the user, so there's no need to
			// call /api/auth/me/ again.
			onLogin(user);
		} catch (error) {
			// Only a 400 means wrong credentials, and its detail is written for the
			// user. Anything else (CSRF 403, 500, network) is not their fault.
			if (error.status === 400) {
				setError(error.data?.detail ?? "Wrong username or password.");
			} else {
				setError("An error occurred, try again later");
			}
		} finally {
			setSubmitting(false);
		}
	}
	return (
		// Rendered by App before its own layout, so it brings its own page background.
		<div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-slate-100 px-4 text-slate-700 dark:bg-slate-950 dark:text-slate-300">
			<div className="flex items-center gap-2.5">
				<span className="size-3 rounded-full bg-accent-600 dark:bg-accent-400"></span>
				<h1 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
					Ticktask
				</h1>
			</div>
			<div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
				<form onSubmit={handleSubmit} className="flex flex-col gap-4">
					{/* One message for the pair, not per field: it must not reveal
					    which of the two is wrong. */}
					{error && (
						<p className="text-sm text-red-600 dark:text-red-400">
							{error}
						</p>
					)}
					<Field label="Username" htmlFor="username">
						<Input
							name="username"
							id="username"
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							required
							autoComplete="username"
						/>
					</Field>
					<Field label="Password" htmlFor="password">
						<Input
							name="password"
							id="password"
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							required
							autoComplete="current-password"
						/>
					</Field>
					<Button type="submit" disabled={submitting}>
						Log in
					</Button>
				</form>
			</div>
		</div>
	);
}
