import axios from "axios";

// Production backend on Render (swap to localhost when developing locally)
const API_BASE_URL = "https://esganalytics.onrender.com/api";
// const API_BASE_URL = "http://localhost:8000/api";

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
