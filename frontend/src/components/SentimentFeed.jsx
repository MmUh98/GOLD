import { useEffect, useState } from 'react';
import { fetchSentimentFeed } from '../services/api';

const colorFor = (l) => l==='bullish'? '#16a34a' : l==='bearish'? '#dc2626' : '#64748b';

export default function SentimentFeed(){
  const [items,setItems]=useState([]);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{(async()=>{ try{ const d=await fetchSentimentFeed(); setItems(d);}finally{setLoading(false);} })();
    const id=setInterval(async()=>{ const d=await fetchSentimentFeed(); setItems(d); },30000); return ()=>clearInterval(id);},[]);
  return <div className="card" style={{display:'flex',flexDirection:'column',height:400}}>
    <h3 style={{marginTop:0}}>Live Sentiment Feed</h3>
    {loading && <div>Loading...</div>}
    <div style={{overflowY:'auto', flex:1, display:'flex', flexDirection:'column', gap:8}}>
      {items.map(i=> <div key={i.id} style={{padding:8, background:'#0f172a', borderRadius:8}}>
        <div style={{fontSize:12, color:'#9ca3af'}}>{new Date(i.created_at).toLocaleTimeString()} · <span style={{color:colorFor(i.label)}}>{i.label||'—'}</span>{i.confidence?` (${(i.confidence*100).toFixed(0)}%)`:''}</div>
        <div style={{whiteSpace:'pre-wrap'}}>{i.text}</div>
      </div>)}
      {!items.length && !loading && <div style={{color:'#9ca3af'}}>No items classified yet.</div>}
    </div>
  </div>;
}
