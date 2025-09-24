import { useState } from "react";
import api from "../services/api";
import { useNavigate, Link } from "react-router-dom";
export default function Signup(){
  const nav = useNavigate(); const [name,setName]=useState(""); const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [err,setErr]=useState("");
  const onSubmit=async(e)=>{e.preventDefault();setErr("");try{const {data}=await api.post("/auth/signup",{name,email,password});localStorage.setItem("token",data.token);nav("/dashboard");}catch(e){setErr("Failed to sign up");}};
  return (<main style={{display:"grid",placeItems:"center",minHeight:"100vh"}}>
    <form className="card" onSubmit={onSubmit} style={{width:380}}><h2>Create account</h2>
    {err && <div style={{color:'#f87171'}}>{err}</div>}
    <input className="input" placeholder="Name" value={name} onChange={e=>setName(e.target.value)}/>
    <input className="input" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/>
    <input className="input" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)}/>
    <button className="btn" type="submit">Sign up</button>
    <p style={{marginTop:8}}>Have an account? <Link to="/login">Sign in</Link></p></form></main>);
}
