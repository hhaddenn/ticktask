// Shared by Input and Textarea (see docs/estilo.md, "Formulários").
const fieldClasses =
	"rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-accent-400 focus:bg-white focus:ring-2 focus:ring-accent-600/15 focus:outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50 dark:placeholder:text-slate-500 dark:focus:border-accent-500 dark:focus:bg-slate-950";

export function Input({ type = "text", ...props }) {
	return <input type={type} className={fieldClasses} {...props} />;
}

export function Textarea({ rows = 3, ...props }) {
	return <textarea rows={rows} className={fieldClasses} {...props} />;
}
