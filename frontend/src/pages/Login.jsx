import { useState } from "react";
import api from "../services/api";
import { useNavigate, Link } from "react-router-dom";
export default function Login(){
  const nav = useNavigate(); const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [err,setErr]=useState("");
  const onSubmit=async(e)=>{e.preventDefault();setErr("");try{const {data}=await api.post("/auth/login",{email,password});localStorage.setItem("token",data.token);nav("/dashboard");}catch(e){setErr("Invalid credentials");}};
  return (<main style={{display:"grid",placeItems:"center",minHeight:"100vh"}}>
    <form className="card" onSubmit={onSubmit} style={{width:360}}><h2>Sign in</h2>
    {err && <div style={{color:'#f87171'}}>{err}</div>}
    <input className="input" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/>
    <input className="input" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)}/>
    <button className="btn" type="submit">Login</button>
    <p style={{marginTop:8}}>No account? <Link to="/signup">Sign up</Link></p></form></main>);
}
