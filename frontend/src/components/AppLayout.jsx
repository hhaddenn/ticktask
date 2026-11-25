import { Routes, Route } from "react-router";
import ProjectsPage from "../pages/ProjectsPage";
import Button from "./ui/Button";
import ProjectKanbanPage from "../pages/ProjectKanbanPage";
import useTimer from "../hooks/useTimer";
import Dialog from "./ui/Dialog";
import ForgottenSessionDialog from "./ForgottenSessionDialog";

export default function AppLayout({ user, onLogout }) {
	// Lives here and not in a page: this layout only exists after login, so
	// GET /api/timer/ never runs without a session, and every page (and the
	// forgotten-session warning) shares the same timer.
	const timer = useTimer();
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
						<Button variant="ghost" onClick={onLogout}>
							Log out
						</Button>
					</div>
				</div>
			</header>
			{/* Here and not in a page, so the warning shows on whichever page the app opens (timer.md rule 10). */}
			<Dialog open={timer.isForgotten} onClose={timer.dismissForgotten}>
				{timer.isForgotten && (
					<ForgottenSessionDialog
						entry={timer.entry}
						error={timer.error}
						onStop={timer.stop}
						onStopAndRestart={timer.stopAndRestart}
						onDismiss={timer.dismissForgotten}
					/>
				)}
			</Dialog>
			<main className="mx-auto max-w-7xl px-4 py-6">
				<Routes>
					<Route path="/" element={<ProjectsPage />}></Route>
					<Route
						path="/projects/:projectId"
						element={<ProjectKanbanPage timer={timer} />}
					></Route>
				</Routes>
			</main>
		</div>
	);
}
