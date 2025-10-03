import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import LivePrice from "../components/LivePrice";
import GoldPriceWidget from "../components/GoldPriceWidget";
import GoldMiniChart from "../components/GoldMiniChart";
import TickerTapeWidget from "../components/TickerTapeWidget";
import SentimentGauge from "../components/SentimentGauge";
import SentimentSummary from "../components/SentimentSummary";
import SentimentFeed from "../components/SentimentFeed";
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
          <div style={{display:'grid', gap:16, gridTemplateColumns:'1fr 380px'}}>
            {/* Left Column: Market & Price / Prediction */}
            <div style={{display:'grid', gap:16}}>
              <div>
                <h3 style={{marginTop:0}}>Market Ticker</h3>
                <TickerTapeWidget />
              </div>
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
              <div>
                <h3 style={{marginTop:0}}>Gold Widgets</h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16 }}>
                <GoldPriceWidget />
                <GoldMiniChart />
              </div>
            </div>
            {/* Right Column: Sentiment */}
            <div style={{display:'flex', flexDirection:'column', gap:16}}>
              <div style={{display:'grid', gap:16, gridTemplateColumns:'1fr'}}>
                <div className="card" style={{padding:12}}>
                  <SentimentGauge />
                </div>
                <div className="card" style={{padding:12}}>
                  <SentimentSummary />
                </div>
              </div>
              <div className="card" style={{flex:1, minHeight:320, display:'flex', flexDirection:'column'}}>
                <h3 style={{marginTop:0}}>Sentiment Feed</h3>
                <div style={{flex:1, overflowY:'auto'}}>
                  <SentimentFeed />
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
