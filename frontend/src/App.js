import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');
  const [priceData, setPriceData] = useState([]);
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: '2000-01-01',
    end: '2022-12-31'
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      // Check API health
      const healthRes = await fetch('http://localhost:5000/api/health');
      const healthData = await healthRes.json();
      
      if (healthData.status === 'healthy') {
        setApiStatus('connected');
        
        // Fetch all data
        const [pricesRes, eventsRes, metricsRes] = await Promise.all([
          fetch(`http://localhost:5000/api/prices?start_date=${dateRange.start}&end_date=${dateRange.end}`),
          fetch('http://localhost:5000/api/events'),
          fetch('http://localhost:5000/api/metrics')
        ]);
        
        const pricesData = await pricesRes.json();
        const eventsData = await eventsRes.json();
        const metricsData = await metricsRes.json();
        
        if (pricesData.success) setPriceData(pricesData.data);
        if (eventsData.success) setEvents(eventsData.data);
        if (metricsData.success) setMetrics(metricsData.data);
      } else {
        setApiStatus('error');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setApiStatus('error');
      
      // Set fallback data
      setMetrics({
        basic: {
          date_range: {
            start: '1987-05-20',
            end: '2022-11-14',
            total_days: 9011
          },
          price_statistics: {
            current: 96.42,
            average: 58.73,
            min: 9.10,
            max: 143.95
          }
        }
      });
      
      setEvents([
        {
          name: 'Gulf War',
          date: '1990-08-02',
          category: 'Geopolitical',
          impact_magnitude: 'Very High',
          price_before: 42.15,
          price_after: 38.72,
          price_change_pct: -8.1
        },
        {
          name: '2008 Financial Crisis',
          date: '2008-09-15',
          category: 'Economic',
          impact_magnitude: 'Very High',
          price_before: 96.88,
          price_after: 64.15,
          price_change_pct: -33.8
        },
        {
          name: 'COVID-19 Pandemic',
          date: '2020-03-11',
          category: 'Economic',
          impact_magnitude: 'Very High',
          price_before: 35.98,
          price_after: 41.12,
          price_change_pct: 14.3
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  const handleDateChange = (e) => {
    const { name, value } = e.target;
    setDateRange(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRefresh = () => {
    fetchData();
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading Brent Oil Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>Brent Oil Price Intelligence Dashboard</h1>
        <p>Analysis of geopolitical & economic impacts on oil markets (1987-2022)</p>
        <div className={`status ${apiStatus}`}>
          {apiStatus === 'connected' ? '✅ API Connected' : 
           apiStatus === 'error' ? '⚠️ Using Demo Data' : 
           '🔄 Connecting...'}
        </div>
      </header>

      {/* Controls */}
      <div className="controls">
        <div className="date-filters">
          <label>
            Start Date:
            <input
              type="date"
              name="start"
              value={dateRange.start}
              onChange={handleDateChange}
              min="1987-05-20"
              max="2022-11-14"
            />
          </label>
          <label>
            End Date:
            <input
              type="date"
              name="end"
              value={dateRange.end}
              onChange={handleDateChange}
              min="1987-05-20"
              max="2022-12-31"
            />
          </label>
          <button onClick={handleRefresh} className="refresh-btn">
            🔄 Refresh Data
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {metrics && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Current Price</h3>
            <div className="stat-value">
              ${metrics.basic?.price_statistics?.current?.toFixed(2) || '0.00'}
            </div>
            <div className="stat-label">USD per barrel</div>
          </div>
          
          <div className="stat-card">
            <h3>Average Price</h3>
            <div className="stat-value">
              ${metrics.basic?.price_statistics?.average?.toFixed(2) || '0.00'}
            </div>
            <div className="stat-label">Historical average</div>
          </div>
          
          <div className="stat-card">
            <h3>Data Points</h3>
            <div className="stat-value">
              {metrics.basic?.date_range?.total_days?.toLocaleString() || '0'}
            </div>
            <div className="stat-label">Total days</div>
          </div>
          
          <div className="stat-card">
            <h3>Events</h3>
            <div className="stat-value">
              {events.length}
            </div>
            <div className="stat-label">Major events</div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="main-content">
        {/* Price Chart */}
        <div className="chart-section">
          <h2>Price History</h2>
          <div className="chart-container">
            {priceData.length > 0 ? (
              <div className="price-chart">
                <div className="chart">
                  {/* Simple bar chart using divs */}
                  <div className="chart-bars">
                    {priceData.slice(-50).map((item, index) => (
                      <div
                        key={index}
                        className="chart-bar"
                        style={{
                          height: `${(item.price / 150) * 100}%`,
                          width: `${100 / 50}%`
                        }}
                        title={`${item.date}: $${item.price.toFixed(2)}`}
                      ></div>
                    ))}
                  </div>
                  <div className="chart-labels">
                    <span>{priceData[0]?.date}</span>
                    <span>{priceData[Math.floor(priceData.length/2)]?.date}</span>
                    <span>{priceData[priceData.length-1]?.date}</span>
                  </div>
                </div>
                <div className="chart-info">
                  <p>Showing {priceData.length} price points</p>
                  <p>Range: ${Math.min(...priceData.map(p => p.price)).toFixed(2)} - ${Math.max(...priceData.map(p => p.price)).toFixed(2)}</p>
                </div>
              </div>
            ) : (
              <p>No price data available</p>
            )}
          </div>
        </div>

        {/* Events List */}
        <div className="events-section">
          <h2>Major Events</h2>
          <div className="events-list">
            {events.map((event, index) => (
              <div key={index} className="event-card">
                <div className="event-header">
                  <h4>{event.name}</h4>
                  <span className={`event-category ${event.category.toLowerCase().replace(' ', '-')}`}>
                    {event.category}
                  </span>
                </div>
                <div className="event-details">
                  <p><strong>Date:</strong> {event.date}</p>
                  <p><strong>Impact:</strong> {event.impact_magnitude}</p>
                  <p><strong>Price Change:</strong> 
                    <span className={event.price_change_pct >= 0 ? 'positive' : 'negative'}>
                      {event.price_change_pct >= 0 ? '+' : ''}{event.price_change_pct}%
                    </span>
                  </p>
                  {event.description && <p>{event.description}</p>}
                </div>
                <div className="event-price">
                  <div className="price-before">
                    <span>Before: ${event.price_before?.toFixed(2)}</span>
                  </div>
                  <div className="price-arrow">→</div>
                  <div className="price-after">
                    <span>After: ${event.price_after?.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* API Links */}
      <div className="api-links">
        <h3>API Endpoints</h3>
        <div className="links-grid">
          <a href="http://localhost:5000/api/health" target="_blank" rel="noopener noreferrer">
            /api/health
          </a>
          <a href="http://localhost:5000/api/prices" target="_blank" rel="noopener noreferrer">
            /api/prices
          </a>
          <a href="http://localhost:5000/api/events" target="_blank" rel="noopener noreferrer">
            /api/events
          </a>
          <a href="http://localhost:5000/api/metrics" target="_blank" rel="noopener noreferrer">
            /api/metrics
          </a>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>Brent Oil Price Analysis Dashboard • Task 3</p>
        <p>Backend API: {apiStatus === 'connected' ? 'Running' : 'Offline'}</p>
      </footer>
    </div>
  );
}

export default App;