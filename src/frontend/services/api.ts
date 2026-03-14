const API = "http://localhost:5000";

export async function getVersions() {
    const res = await fetch(`${API}/version/`);
    return res.json();
}