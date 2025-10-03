import { useEffect, useState } from 'react';
import { RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts';
import { fetchSentimentSummary } from '../services/api';

export default function SentimentGauge(){
  const [val,setVal]=useState(0);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{(async()=>{
    try{ const s=await fetchSentimentSummary(); setVal(Number(s.bullish_pct||0)); }finally{setLoading(false);} })();
    const id=setInterval(async()=>{ const s=await fetchSentimentSummary(); setVal(Number(s.bullish_pct||0)); },30000);
    return ()=>clearInterval(id);
  },[]);
  const data=[{name:'Bullish', value:val, fill:'#16a34a'}];
  return <div className="card" style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
    <h3 style={{marginTop:0}}>Bullish Gauge</h3>
    {loading? 'Loading...' : <RadialBarChart width={250} height={250} cx={125} cy={125} innerRadius={60} outerRadius={120} barSize={18} data={data} startAngle={180} endAngle={0}>
      <PolarAngleAxis type="number" domain={[0,100]} angleAxisId={0} tick={false} />
      <RadialBar background clockWise dataKey="value" cornerRadius={10} />
      <text x={125} y={135} textAnchor="middle" fontSize={28} fill="#f9fafb">{val.toFixed(1)}%</text>
    </RadialBarChart>}
  </div>;
}
