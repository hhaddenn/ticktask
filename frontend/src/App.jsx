import { useEffect, useState } from "react";
import { apiFetch } from "./api";
import LoginPage from "./pages/LoginPage";
import AppLayout from "./components/AppLayout";

function App() {
	const [user, setUser] = useState(null);
	// Starts true so the "no session" screen doesn't flash on every reload
	// while we still wait for /api/auth/me/.
	const [checkingSession, setCheckingSession] = useState(true);
	const [apiError, setApiError] = useState(null);

	useEffect(() => {
		let ignore = false;
		async function loadUser() {
			try {
				const me = await apiFetch("/api/auth/me/");
				if (!ignore) {
					setUser(me);
				}
			} catch (error) {
				// 403 just means "not logged in" (user stays null), so it isn't an error.
				// Anything else (500, network down) means the API itself is failing.
				if (!ignore && error.status !== 403) {
					setApiError(error);
				}
			} finally {
				if (!ignore) {
					setCheckingSession(false);
				}
			}
		}
		loadUser();
		return () => {
			ignore = true;
		};
	}, []);

	async function handleLogout() {
		try {
			await apiFetch("/api/auth/logout/", { method: "POST" });
			// Only after the server confirms: the sessionid cookie is HttpOnly, so
			// only the server can end the session. Clearing the user on failure
			// would show "logged out" while the session is still alive.
			setUser(null);
		} catch {
			alert("Could not log out, try again.");
		}
	}

	// Order matters: user is also null while checking and when the API fails,
	// so the more specific cases must be handled before "no session".
	if (checkingSession) {
		return <p>Loading...</p>;
	}
	if (apiError !== null) {
		return <p>An error occurred, try again later</p>;
	}
	if (user === null) {
		return <LoginPage onLogin={setUser} />;
	}

	return <AppLayout user={user} onLogout={handleLogout} />;
}

export default App;
