import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import { useEffect, useState } from "react";
import api from "../services/api";
import { requestFCMToken } from "../firebase";
export default function Settings(){
  const [me,setMe]=useState(null);
  useEffect(()=>{(async()=>setMe((await api.get("/auth/me")).data))()},[]);
  const save=async()=>{let payload={theme:me.theme,language:me.language}; const token=await requestFCMToken(); if(token) payload.fcm_token=token; await api.put("/settings", payload); alert("Saved");};
  if(!me) return null;
  return (<><Navbar/><div className="grid" style={{padding:16,gap:16}}><Sidebar/>
    <main className="card"><h3>Settings</h3>
      <label>Theme</label><select className="input" value={me.theme} onChange={e=>setMe({...me,theme:e.target.value})}><option>light</option><option>dark</option></select>
      <label>Language</label><select className="input" value={me.language} onChange={e=>setMe({...me,language:e.target.value})}><option value="en">English</option></select>
      <button className="btn" onClick={save} style={{marginTop:12}}>Save</button>
    </main></div></>);
}
