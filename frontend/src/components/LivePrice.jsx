import { useState, useEffect } from 'react';
import api from '../services/api';

export default function LivePrice() {
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchLivePrice = async () => {
    try {
      setLoading(true);
  // baseURL already includes /api, so don't repeat it
  const response = await api.get('/live-price');
      setPriceData(response.data);
      setError('');
    } catch (err) {
      const serverMsg = err?.response?.data?.message || err?.response?.data?.error || err?.message;
      setError(serverMsg ? `Failed to fetch live price: ${serverMsg}` : 'Failed to fetch live price');
      // Use warn to avoid CRA dev overlay while still logging for diagnostics
      console.warn('Live price fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch immediately
    fetchLivePrice();
    
    // Then fetch every 10 seconds
    const interval = setInterval(fetchLivePrice, 10000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading && !priceData) {
    return (
      <div className="card">
        <h3>Live Gold Price</h3>
        <p>Loading...</p>
      </div>
    );
  }

  if (error && !priceData) {
    return (
      <div className="card">
        <h3>Live Gold Price</h3>
        <p style={{ color: '#f87171' }}>{error}</p>
        <button className="btn" onClick={fetchLivePrice}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>Live Gold Price</h3>
      {priceData && (
        <div>
          <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
            ${priceData.price?.toFixed(2)}
          </div>
          
          {priceData.predicted && (
            <div style={{ fontSize: '16px', color: '#10b981', marginBottom: '8px' }}>
              Predicted: ${priceData.predicted.toFixed(2)}
            </div>
          )}
          
          <div style={{ fontSize: '12px', color: '#9ca3af' }}>
            Last updated: {new Date(priceData.timestamp).toLocaleTimeString()}
          </div>
          
          <div style={{ marginTop: '12px' }}>
            <button 
              className="btn" 
              onClick={fetchLivePrice}
              disabled={loading}
              style={{ fontSize: '12px', padding: '4px 8px' }}
            >
              {loading ? 'Updating...' : 'Refresh'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}