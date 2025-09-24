import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import LivePrice from "../components/LivePrice";
import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard(){
  const [latest,setLatest]=useState(null); 
  const [pred,setPred]=useState(null);
  const [predMeta,setPredMeta]=useState({});
  
  useEffect(()=>{
    (async()=>{
      try {
        // Use price-history endpoint we added for recent cached values
        const hist=(await api.get("/price-history?limit=5")).data;
        if(hist && hist.length){
          setLatest(hist[hist.length-1].price);
        }
        // Get model prediction (may return 400 if not enough data yet)
        try {
          const p=(await api.get("/predict")).data; 
          setPred(p.predicted_price);
          setPredMeta({mode:p.mode, used:p.used, window:p.window});
        } catch (e) {
          // keep UI graceful
        }
      } catch (error) {
        console.error("Dashboard data fetch error:", error);
      }
    })()
  },[]);
  
  return (
    <>
      <Navbar/>
      <div className="grid" style={{padding:16,gap:16}}>
        <Sidebar/>
        <main className="card" style={{display:"grid",gap:16}}>
          <LivePrice />
          <div className="card">
            <h3>Historical Latest</h3>
            <div style={{fontSize:28}}>{typeof latest==='number'?latest.toFixed(2):"—"}</div>
          </div>
          <div className="card">
            <h3>Model Prediction</h3>
            <div style={{fontSize:28}}>{typeof pred==='number'?pred.toFixed(2):"—"}</div>
            {predMeta?.mode && (
              <div style={{color:'#9ca3af', fontSize:12, marginTop:4}}>
                Mode: {predMeta.mode}{predMeta.window?` · window ${predMeta.window}`:''}{predMeta.used?` · used ${predMeta.used}`:''}
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  );
}
