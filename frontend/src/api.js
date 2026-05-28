import axios from "axios";

const isLocal =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";

const API_BASE_URL = isLocal
  ? "http://localhost:8000/api"
  : "https://esganalytics.onrender.com/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Token ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export function getStoredToken() {
  return localStorage.getItem("token");
}

export function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  setAuthToken(null);
}
