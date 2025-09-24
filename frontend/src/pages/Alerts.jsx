import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import { useEffect, useState } from "react";
import api from "../services/api";
import { requestFCMToken, listenForeground } from "../firebase";
export default function Alerts(){
  const [alerts,setAlerts]=useState([]);
  const [form,setForm]=useState({type:"percentage",direction:"up",threshold_value:2,push_enabled:true});
  const [notif,setNotif]=useState("");
  const refresh=async()=>setAlerts((await api.get("/alerts")).data);
  useEffect(()=>{refresh(); listenForeground(setNotif);},[]);
  const add=async()=>{
    const token=await requestFCMToken(); if(token){await api.post("/auth/token/fcm",{token});}
    await api.post("/alerts",{...form,fcm_token:token}); setForm({...form}); refresh();
  };
  const del=async(id)=>{await api.delete(`/alerts/${id}`); refresh();};
  return (<>
    <Navbar/><div className="grid" style={{padding:16,gap:16}}><Sidebar/>
    <main className="card"><h3>Alerts</h3>{notif && <div className="card">{notif}</div>}
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(200px,1fr))",gap:12}}>
        <select className="input" value={form.type} onChange={e=>setForm({...form,type:e.target.value})}><option value="percentage">Percentage</option><option value="absolute">Absolute</option></select>
        <select className="input" value={form.direction} onChange={e=>setForm({...form,direction:e.target.value})}><option value="up">Up</option><option value="down">Down</option></select>
        <input className="input" type="number" value={form.threshold_value} onChange={e=>setForm({...form,threshold_value:e.target.value})}/>
        <button className="btn" onClick={add}>Create</button>
      </div>
      <table className="table" style={{marginTop:16}}><thead><tr><th>Type</th><th>Dir</th><th>Threshold</th><th>Active</th><th>Push</th><th/></tr></thead>
      <tbody>{alerts.map(a=>(<tr key={a.id}><td>{a.type}</td><td>{a.direction}</td><td>{a.threshold_value}</td><td>{a.active?'Yes':'No'}</td><td>{a.push_enabled?'Yes':'No'}</td><td><button className="btn" onClick={()=>del(a.id)}>Delete</button></td></tr>))}</tbody></table>
    </main></div></>);
}
