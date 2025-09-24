import { Link, useLocation } from "react-router-dom";
export default function Sidebar(){
  const { pathname } = useLocation();
  const Item=({to,label})=>(<Link to={to} style={{padding:'10px 12px',borderRadius:10,background:pathname===to?'#1f2937':'transparent',color:'#fff'}}>{label}</Link>);
  return (<aside className="sidebar">
    <Item to="/dashboard" label="Dashboard"/><Item to="/chart" label="Charts"/><Item to="/alerts" label="Alerts"/><Item to="/reports" label="Reports"/><Item to="/settings" label="Settings"/>
  </aside>);
}
