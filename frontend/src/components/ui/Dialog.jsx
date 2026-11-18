import { useEffect, useRef } from "react";

export default function Dialog({ open, onClose, children }) {
	const dialogRef = useRef(null);

	useEffect(() => {
		if (open) {
			dialogRef.current.showModal();
		} else {
			dialogRef.current.close();
		}
	}, [open]);
	return (
		<dialog
			ref={dialogRef}
			onClose={onClose}
			className="m-auto w-full max-w-lg bg-transparent p-4 backdrop:bg-slate-950/40 dark:backdrop:bg-slate-950/80"
		>
			{children}
		</dialog>
	);
}
