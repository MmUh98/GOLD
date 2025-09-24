import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import { Line } from "react-chartjs-2";
import { useEffect, useMemo, useRef, useState } from "react";
import api from "../services/api";
import { Chart as ChartJS, LineElement, LinearScale, PointElement, TimeScale, Tooltip, Legend, CategoryScale } from "chart.js";
import "chartjs-adapter-date-fns";
import zoomPlugin from "chartjs-plugin-zoom";
import annotationPlugin from "chartjs-plugin-annotation";
ChartJS.register(LineElement, LinearScale, PointElement, TimeScale, Tooltip, Legend, CategoryScale, zoomPlugin, annotationPlugin);
export default function PriceChart(){
  const [rows,setRows]=useState([]);
  const [meta,setMeta]=useState({});
  const [rangeSel,setRangeSel]=useState("1d");
  const [intervalSel,setIntervalSel]=useState("");
  const [err,setErr]=useState("");
  const chartRef = useRef(null);
  useEffect(()=>{(async()=>{
    try{
      const res = await api.get(`/chart-series`, { params: { range: rangeSel, interval: intervalSel || undefined } });
      const pts = res.data?.points||[]; setRows(pts); setMeta(res.data?.meta||{}); setErr("");
    }catch(e){
      const msg=e?.response?.data?.error||e?.message||"Failed to load chart series"; setErr(msg);
      // Fallback to cached DB history so we still show something
      try{
        const hist=await api.get('/price-history?limit=600');
        const pts=(hist.data||[]).map(d=>({timestamp:d.timestamp, price:d.price}));
        setRows(pts); setMeta({});
      }catch{ /* ignore */ }
    }
  })()},[rangeSel, intervalSel]);
  // live refresh every 30s
  useEffect(()=>{
    const id=setInterval(async()=>{
      try{const res=await api.get(`/chart-series`, { params: { range: rangeSel, interval: intervalSel || undefined } });
        setRows(res.data?.points||[]); setMeta(res.data?.meta||{}); setErr("");
      }catch(e){
        const msg=e?.response?.data?.error||e?.message; setErr(msg||"Chart refresh failed");
      }
    },30000);
    return()=>clearInterval(id);
  },[rangeSel, intervalSel]);
  const data=useMemo(()=>({
    labels:rows.map(r=>new Date(r.timestamp)),
    datasets:[{
      label:"Gold Price",
      data:rows.map(r=>r.price),
      borderColor:"#0ea5e9",
      backgroundColor:"rgba(14,165,233,0.2)",
      pointRadius:0,
      tension:0.2,
    }]
  }),[rows]);
  const options=useMemo(()=>({
    responsive:true,
    maintainAspectRatio:true,
    aspectRatio: 2.2,
    interaction:{mode:"index",intersect:false},
    scales:{
      x:{type:"time", time:{tooltipFormat:"PPp"}, ticks:{maxRotation:0, autoSkip:true}},
      y:{beginAtZero:false}
    },
    plugins:{
      legend:{display:false},
      zoom:{
        pan:{enabled:true, mode:"x"},
        zoom:{wheel:{enabled:true}, pinch:{enabled:true}, mode:"x"}
      },
      annotation: {
        annotations: {
          prevClose: meta?.previousClose ? {
            type: 'line',
            yMin: meta.previousClose, yMax: meta.previousClose,
            borderColor: '#999', borderDash: [6,4], borderWidth: 1,
            label: { enabled: true, content: 'Prev Close', position: 'start', backgroundColor: 'rgba(0,0,0,0.6)'}
          } : undefined,
          last: rows?.length ? {
            type: 'line',
            yMin: rows[rows.length-1].price, yMax: rows[rows.length-1].price,
            borderColor: '#22c55e', borderDash: [4,4], borderWidth: 1,
            label: { enabled: true, content: 'Last', position: 'start', backgroundColor: 'rgba(0,0,0,0.6)'}
          } : undefined
        }
      }
    }
  }),[rows, meta]);
  return (<>
    <Navbar/>
    <div className="grid" style={{padding:16,gap:16}}><Sidebar/>
      <main className="card">
        <div style={{display:"flex", alignItems:"center", justifyContent:"space-between", gap:12}}>
          <h3 style={{margin:0}}>Price Chart</h3>
          <div style={{display:"flex", gap:8}}>
            {["1d","5d","1mo","6mo","1y"].map(r=> (
              <button key={r} onClick={()=>setRangeSel(r)}
                style={{padding:"6px 10px", border:"1px solid #ddd", borderRadius:6, background:r===rangeSel?"#eef":"white", cursor:"pointer"}}>{r.toUpperCase()}</button>
            ))}
          </div>
          <button
            onClick={()=>{try{chartRef.current && chartRef.current.resetZoom && chartRef.current.resetZoom();}catch(e){}}}
            className="btn"
            style={{padding:"6px 10px", border:"1px solid #ddd", borderRadius:6, background:"white", cursor:"pointer"}}
            title="Reset zoom"
          >Reset Zoom</button>
        </div>
        {err && (
          <div style={{padding:8, marginTop:8, color:'#f87171', fontSize:12, border:'1px solid #3b0f0f', background:'#1b0b0b', borderRadius:6}}>
            {String(err)}
          </div>
        )}
        {rows.length===0 ? (
          <div style={{padding:16, color:"#666"}}>No data yet. Try waiting a moment or backfilling prices.</div>
        ) : (
          <div style={{width:"100%", maxWidth:900, height:400, margin:"8px auto 0"}}>
            <Line ref={chartRef} data={data} options={options}/>
          </div>
        )}
      </main>
    </div></>);
}
