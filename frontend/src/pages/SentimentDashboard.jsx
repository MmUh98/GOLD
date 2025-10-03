import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import SentimentGauge from '../components/SentimentGauge';
import SentimentSummary from '../components/SentimentSummary';
import SentimentFeed from '../components/SentimentFeed';

export default function SentimentDashboard() {
  return (
    <>
      <Navbar />
      <div className="grid" style={{ padding: 16, gap: 16 }}>
        <Sidebar />
        <main className="card" style={{ display: 'grid', gap: 16 }}>
          <h2 style={{ margin: 0 }}>Sentiment Dashboard</h2>
          <div style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))' }}>
            <SentimentGauge />
            <SentimentSummary />
          </div>
          <SentimentFeed />
        </main>
      </div>
    </>
  );
}
