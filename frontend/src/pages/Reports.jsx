import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import { useEffect, useState } from "react";
import api from "../services/api";
export default function Reports(){
  const [range,setRange]=useState("daily"); const [data,setData]=useState(null);
  useEffect(()=>{(async()=>setData((await api.get(`/reports?range=${range}`)).data))()},[range]);
  return (<><Navbar/><div className="grid" style={{padding:16,gap:16}}><Sidebar/>
    <main className="card"><div style={{display:"flex",gap:12,alignItems:"center"}}><h3>Reports</h3>
      <select className="input" value={range} onChange={e=>setRange(e.target.value)}><option value="daily">Daily</option><option value="weekly">Weekly</option><option value="monthly">Monthly</option></select></div>
      {data && (<ul><li>Count: {data.count}</li><li>Avg: {data.avg?.toFixed?.(2)}</li><li>Min: {data.min?.toFixed?.(2)}</li><li>Max: {data.max?.toFixed?.(2)}</li><li>Volatility: {data.volatility_pct?.toFixed?.(2)}%</li></ul>)}
    </main></div></>);
}
