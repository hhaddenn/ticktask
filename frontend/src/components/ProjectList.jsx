import Button from "./ui/Button";

export default function ProjectList({ projects, onEdit, onToggleArchive }) {
	return projects.length === 0 ? (
		<p className="text-sm text-slate-500 dark:text-slate-400">
			No projects available.
		</p>
	) : (
		<ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{projects.map((project) => (
				<li
					key={project.id}
					className="flex flex-col gap-2 rounded-xl bg-white p-5 shadow-xs ring-1 ring-slate-900/10 transition hover:shadow-md dark:bg-slate-900 dark:ring-white/10"
				>
					<h2 className="font-semibold text-slate-900 dark:text-slate-50">
						{project.name}
					</h2>
					{project.description && (
						<p className="text-sm text-slate-500 dark:text-slate-400">
							{project.description}
						</p>
					)}
					<div className="mt-auto flex gap-1 pt-2">
						<Button variant="ghost" onClick={() => onEdit(project)}>
							Edit
						</Button>
						<Button
							variant="danger"
							onClick={() => onToggleArchive(project)}
						>
							{project.archived_at ? "Unarchive" : "Archive"}
						</Button>
					</div>
				</li>
			))}
		</ul>
	);
}
