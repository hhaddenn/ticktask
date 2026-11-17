// Classes shared by every variant (see docs/estilo.md, "Botões").
const base =
	"rounded-full text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50";

const variants = {
	primary:
		"bg-accent-700 px-4 py-2 text-white hover:bg-accent-800 focus-visible:outline-accent-700 dark:bg-accent-500 dark:text-slate-950 dark:hover:bg-accent-400",
	secondary:
		"bg-slate-100 px-4 py-2 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700",
	ghost: "px-3 py-1 text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-50",
	danger: "px-3 py-1 text-slate-500 hover:bg-red-50 hover:text-red-700 dark:text-slate-400 dark:hover:bg-red-950/60 dark:hover:text-red-400",
};

export default function Button({
	variant = "primary",
	type = "button",
	children,
	...props
}) {
	return (
		<button
			type={type}
			className={`${base} ${variants[variant]}`}
			{...props}
		>
			{children}
		</button>
	);
}
