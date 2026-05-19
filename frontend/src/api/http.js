import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "/api";

const http = axios.create({
  baseURL,
  timeout: 30000,
});

export default http;
