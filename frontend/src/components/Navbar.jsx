import { Link } from "react-router-dom";
export default function Navbar(){
  return (<nav className="nav">
    <Link to="/dashboard" style={{fontWeight:700,color:"#d4af37"}}>GoldPredict</Link>
    <div style={{marginLeft:"auto",display:"flex",gap:12}}>
      <Link to="/chart">Chart</Link>
      <Link to="/sentiment">Sentiment</Link>
      <Link to="/alerts">Alerts</Link>
      <Link to="/reports">Reports</Link>
      <Link to="/settings">Settings</Link>
    </div></nav>);
}
