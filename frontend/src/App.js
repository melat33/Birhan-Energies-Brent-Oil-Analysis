import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');
  const [metrics, setMetrics] = useState(null);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const healthRes = await fetch('http://localhost:5000/api/health');
        const healthData = await healthRes.json();
        
        if (healthData.status === 'healthy') {
          setApiStatus('connected');
          
          const metricsRes = await fetch('http://localhost:5000/api/summary-metrics');
          const metricsData = await metricsRes.json();
          
          const eventsRes = await fetch('http://localhost:5000/api/events');
          const eventsData = await eventsRes.json();
          
          if (metricsData.success) setMetrics(metricsData.metrics);
          if (eventsData.success) setEvents(eventsData.data);
        } else {
          setApiStatus('error');
        }
      } catch (error) {
        console.error('Error:', error);
        setApiStatus('error');
        
        setMetrics({
          total_days: 9011,
          date_range: { start: '1987-05-20', end: '2022-11-14' },
          price_stats: {
            current: 96.42,
            average: 58.73,
            max: 143.95,
            min: 9.10
          },
          event_stats: {
            total_events: 17,
            events_by_category: { Geopolitical: 5, Economic: 6, 'OPEC Decision': 4, Conflict: 2 }
          }
        });
        
        setEvents([
          { event_name: 'Gulf War', date: '1990-08-02', category: 'Geopolitical', impact_magnitude: 'Very High', price_at_event: 42.15 },
          { event_name: '2008 Financial Crisis', date: '2008-09-15', category: 'Economic', impact_magnitude: 'Very High', price_at_event: 96.88 },
          { event_name: 'COVID-19 Pandemic', date: '2020-03-11', category: 'Economic', impact_magnitude: 'Very High', price_at_event: 35.98 },
          { event_name: 'Russia-Ukraine War', date: '2022-02-24', category: 'Geopolitical', impact_magnitude: 'Very High', price_at_event: 105.79 }
        ]);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="dashboard">
      <header className="header">
        <h1>Brent Oil Price Intelligence Dashboard</h1>
        <p>Interactive analysis of geopolitical & economic impacts on oil markets (1987-2022)</p>
        <div className={'status-badge status-' + apiStatus}>
          {apiStatus === 'connected' ? '✅ Backend API Connected' : 
           apiStatus === 'error' ? '⚠️ Using Demo Data' : 
           '🔄 Connecting...'}
        </div>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Current Price</h3>
          <div className="stat-value">${metrics?.price_stats?.current?.toFixed(2) || '0.00'}</div>
          <div className="stat-label">USD per barrel</div>
        </div>

        <div className="stat-card">
          <h3>Data Range</h3>
          <div className="stat-value">
            {metrics?.date_range?.start?.split('-')[0] || '1987'} - {metrics?.date_range?.end?.split('-')[0] || '2022'}
          </div>
          <div className="stat-label">{metrics?.total_days?.toLocaleString() || '9,011'} days</div>
        </div>

        <div className="stat-card">
          <h3>Total Events</h3>
          <div className="stat-value">{metrics?.event_stats?.total_events || '17'}</div>
          <div className="stat-label">Geopolitical events</div>
        </div>

        <div className="stat-card">
          <h3>Price Range</h3>
          <div className="stat-value">
            ${metrics?.price_stats?.min?.toFixed(2) || '9.10'} - ${metrics?.price_stats?.max?.toFixed(2) || '143.95'}
          </div>
          <div className="stat-label">Historical Min - Max</div>
        </div>
      </div>

      <div className="main-content">
        <div className="content-card">
          <h2 className="card-title">API Test Endpoints</h2>
          <a href="http://localhost:5000/api/health" target="_blank" rel="noopener noreferrer" className="api-link">
            <strong>GET /api/health</strong> - Health Check
          </a>
          <a href="http://localhost:5000/api/summary-metrics" target="_blank" rel="noopener noreferrer" className="api-link">
            <strong>GET /api/summary-metrics</strong> - Summary Data
          </a>
          <a href="http://localhost:5000/api/events" target="_blank" rel="noopener noreferrer" className="api-link">
            <strong>GET /api/events</strong> - Events Data
          </a>
          <a href="http://localhost:5000/api/historical-prices" target="_blank" rel="noopener noreferrer" className="api-link">
            <strong>GET /api/historical-prices</strong> - Price History
          </a>
        </div>

        <div className="content-card">
          <h2 className="card-title">Key Events</h2>
          <div className="events-list">
            {events.map((event, index) => (
              <div key={index} className="event-item">
                <div className="event-name">{event.event_name}</div>
                <div className="event-details">
                  <div><strong>Date:</strong> {event.date}</div>
                  <div><strong>Price:</strong> ${event.price_at_event?.toFixed(2)}</div>
                  <div>
                    <strong>Category:</strong>
                    <span className={'event-category category-' + event.category.toLowerCase().replace(/ /g, '-')}>
                      {event.category}
                    </span>
                  </div>
                  <div><strong>Impact:</strong> {event.impact_magnitude}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <footer className="footer">
        <p>Brent Oil Price Analysis Dashboard • Task 3: Interactive Dashboard</p>
        <div style={{ marginTop: '1rem' }}>
          <button onClick={() => window.location.reload()} className="button">
            🔄 Refresh Dashboard
          </button>
          <button onClick={() => window.open('http://localhost:5000', '_blank')} className="button button-secondary">
            🌐 Open Backend
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;