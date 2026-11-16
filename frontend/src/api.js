function getCookie(name) {
	const cookies = document.cookie.split("; ");
	const cookie = cookies.find((p) => p.startsWith(name + "="));
	if (cookie !== undefined) {
		const cookieValue = cookie.slice(name.length + 1);
		return decodeURIComponent(cookieValue);
	}
	return null;
}

export async function apiFetch(path, { method = "GET", body } = {}) {
	const headers = {};

	if (method !== "GET") {
		headers["Content-Type"] = "application/json";
		headers["X-CSRFToken"] = getCookie("csrftoken");
	}

	const response = await fetch(path, {
		method,
		headers,
		body: body ? JSON.stringify(body) : undefined,
	});

	if (!response.ok) {
		const data = await response.json().catch(() => null);
		const error = new Error(`Request failed: ${response.status}`);
		error.status = response.status;
		error.data = data;
		throw error;
	}

	if (response.status === 204) {
		return null;
	}

	return response.json();
}
