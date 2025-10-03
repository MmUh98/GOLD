import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fetchSentimentSummary } from '../services/api';

const COLORS={bullish:'#16a34a', bearish:'#dc2626', neutral:'#475569'};

export default function SentimentSummary(){
  const [data,setData]=useState(null);
  useEffect(()=>{(async()=>{ const s=await fetchSentimentSummary(); setData(s); })();
    const id=setInterval(async()=>{ const s=await fetchSentimentSummary(); setData(s); },30000); return ()=>clearInterval(id);},[]);
  if(!data) return <div style={{textAlign:'center'}}>Loading...</div>;
  const pie=[{name:'Bullish', value:data.bullish_pct},{name:'Bearish', value:data.bearish_pct},{name:'Neutral', value:data.neutral_pct}];
  return <div style={{display:'flex',flexDirection:'column',alignItems:'center', width:'100%'}}>
    <h3 style={{marginTop:0}}>Sentiment Breakdown</h3>
    <div style={{width:'100%', height:260}}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={pie} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
            {pie.map((e,i)=><Cell key={i} fill={COLORS[e.name.toLowerCase()]||'#8884d8'} />)}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
    <div style={{fontSize:12,color:'#9ca3af'}}>Total items: {data.total}</div>
  </div>;
}
