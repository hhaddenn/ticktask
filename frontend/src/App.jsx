import { Route, Routes } from "react-router";
import ProjectsPage from "./pages/ProjectsPage";
import ProjectKanbanPage from "./pages/ProjectKanbanPage";

function App() {
	return (
		<div className="min-h-screen bg-slate-100 text-slate-700 dark:bg-slate-950 dark:text-slate-300">
			<header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
				<div className="mx-auto flex max-w-7xl items-center gap-2.5 px-4 py-3.5">
					<span className="size-3 rounded-full bg-accent-600 dark:bg-accent-400"></span>
					<h1 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
						Ticktask
					</h1>
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
