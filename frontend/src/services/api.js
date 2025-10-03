import axios from "axios";
const api = axios.create({ baseURL: process.env.REACT_APP_API_BASE || "http://localhost:5001/api" });
api.interceptors.request.use(cfg=>{ const t=localStorage.getItem("token"); if(t) cfg.headers.Authorization=`Bearer ${t}`; return cfg; });
export default api;

// Sentiment helpers
export async function fetchSentimentSummary(){
	const {data}=await api.get("/sentiment/summary");
	return data;
}
export async function fetchSentimentFeed(){
	const {data}=await api.get("/sentiment/feed");
	return data;
}
