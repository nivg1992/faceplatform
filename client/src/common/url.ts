export function getBaseURL() {
    return window.location.host === "localhost:5173" ? "http://localhost:5000/api" : "/api"
}