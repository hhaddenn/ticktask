// Label + field + error message (see docs/estilo.md, "Formulários").

export default function Field({ label, htmlFor, error, children }) {
	return (
		<div className="flex flex-col gap-1.5">
			<label
				htmlFor={htmlFor}
				className="text-sm font-medium text-slate-700 dark:text-slate-300"
			>
				{label}
			</label>
			{children}
			{error && (
				<p className="text-sm text-red-600 dark:text-red-400">
					{error}
				</p>
			)}
		</div>
	);
}
