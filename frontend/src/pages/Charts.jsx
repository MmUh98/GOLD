import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import TradingViewChart from "../components/TradingViewChart";

export default function Charts(){
  return (
    <>
      <Navbar/>
      <div className="grid" style={{padding:16,gap:16}}>
        <Sidebar/>
        <main className="card" style={{display:"grid", gap:16}}>
          <h3 style={{margin:0}}>Live Gold Price Chart</h3>
          <TradingViewChart symbol="OANDA:XAUUSD" interval="D"/>
        </main>
      </div>
    </>
  );
}
