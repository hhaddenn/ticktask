export function formatDuration(duration) {
	const total = Math.floor(duration);
	const hours = Math.floor(total / 3600);
	const minutes = Math.floor((total % 3600) / 60);
	const seconds = total % 60;
	return `${hours}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export function formatMinutes(minutes) {
	const total = Math.floor(minutes);
	const hours = Math.floor(total / 60);
	return `${hours}:${String(total % 60).padStart(2, "0")}`;
}
