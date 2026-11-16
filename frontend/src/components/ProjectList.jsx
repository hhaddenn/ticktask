export default function ProjectList({ projects, onEdit, onToggleArchive }) {
	return projects.length === 0 ? (
		<p>No projects available.</p>
	) : (
		<ul>
			{projects.map((project) => (
				<li key={project.id}>
					<h2>{project.name}</h2>
					<p>{project.description}</p>
					<button onClick={() => onEdit(project)}>Edit</button>
					<button onClick={() => onToggleArchive(project)}>
						{project.archived_at ? "Unarchive" : "Archive"}
					</button>
				</li>
			))}
		</ul>
	);
}
