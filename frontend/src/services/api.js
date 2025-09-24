import axios from "axios";
const api = axios.create({ baseURL: process.env.REACT_APP_API_BASE || "http://localhost:5001/api" });
api.interceptors.request.use(cfg=>{ const t=localStorage.getItem("token"); if(t) cfg.headers.Authorization=`Bearer ${t}`; return cfg; });
export default api;
