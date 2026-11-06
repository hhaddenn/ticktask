import { useEffect, useState } from "react";

function App() {
	const [data, setData] = useState(null);
	const [error, setError] = useState(null);

	useEffect(() => {
		fetch("/api/health/")
			.then((response) => {
				if (!response.ok) {
					throw new Error(`Error, ${response.status}`);
				}
				return response.json();
			})
			.then((json) => {
				setData(json);
			})
			.catch((err) => {
				setError(err);
			});
	}, []);

	let statusText;
	if (error) {
		statusText = `API indisponível: ${error}`;
	} else if (data === null) {
		statusText = "A ligar à API…";
	} else {
		statusText = `API: ${data.status}`;
	}

	return (
		<>
			<h1>Ticktask</h1>
			<p>{statusText}</p>
		</>
	);
}

export default App;
