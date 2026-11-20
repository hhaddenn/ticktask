import { Route, Routes } from "react-router";
import ProjectsPage from "./pages/ProjectsPage";
import ProjectKanbanPage from "./pages/ProjectKanbanPage";
import { useEffect, useState } from "react";
import { apiFetch } from "./api";
import LoginPage from "./pages/LoginPage";
import Button from "./components/ui/Button";

function App() {
	const [user, setUser] = useState(null);
	// Starts true so the "no session" screen doesn't flash on every reload
	// while we still wait for /api/auth/me/.
	const [checkingSession, setCheckingSession] = useState(true);
	const [apiError, setApiError] = useState(null);

	useEffect(() => {
		let ignore = false;
		async function loadUser() {
			try {
				const me = await apiFetch("/api/auth/me/");
				if (!ignore) {
					setUser(me);
				}
			} catch (error) {
				// 403 just means "not logged in" (user stays null), so it isn't an error.
				// Anything else (500, network down) means the API itself is failing.
				if (!ignore && error.status !== 403) {
					setApiError(error);
				}
			} finally {
				if (!ignore) {
					setCheckingSession(false);
				}
			}
		}
		loadUser();
		return () => {
			ignore = true;
		};
	}, []);

	async function handleLogout() {
		try {
			await apiFetch("/api/auth/logout/", { method: "POST" });
			// Only after the server confirms: the sessionid cookie is HttpOnly, so
			// only the server can end the session. Clearing the user on failure
			// would show "logged out" while the session is still alive.
			setUser(null);
		} catch {
			alert("Could not log out, try again.");
		}
	}

	// Order matters: user is also null while checking and when the API fails,
	// so the more specific cases must be handled before "no session".
	if (checkingSession) {
		return <p>Loading...</p>;
	}
	if (apiError !== null) {
		return <p>An error occurred, try again later</p>;
	}
	if (user === null) {
		return <LoginPage onLogin={setUser} />;
	}

	return (
		<div className="min-h-screen bg-slate-100 text-slate-700 dark:bg-slate-950 dark:text-slate-300">
			<header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
				<div className="mx-auto flex max-w-7xl items-center gap-2.5 px-4 py-3.5">
					<span className="size-3 rounded-full bg-accent-600 dark:bg-accent-400"></span>
					<h1 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
						Ticktask
					</h1>
					<div className="ml-auto flex items-center gap-3">
						<span className="text-sm">{user.username}</span>
						<Button variant="ghost" onClick={handleLogout}>
							Log out
						</Button>
					</div>
				</div>
			</header>
			<main className="mx-auto max-w-7xl px-4 py-6">
				<Routes>
					<Route path="/" element={<ProjectsPage />}></Route>
					<Route
						path="/projects/:projectId"
						element={<ProjectKanbanPage />}
					></Route>
				</Routes>
			</main>
		</div>
	);
}

export default App;
