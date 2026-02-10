import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');
  const [priceData, setPriceData] = useState([]);
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [highlightEvents, setHighlightEvents] = useState(true);
  
  // Date range state
  const [dateRange, setDateRange] = useState({
    start: '2000-01-01',
    end: '2022-12-31'
  });
  
  // Event filtering state
  const [eventFilters, setEventFilters] = useState({
    category: 'All',
    impactLevel: 'Medium'
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      // Check API health
      const healthRes = await fetch('http://localhost:5000/api/health');
      const healthData = await healthRes.json();
      
      if (healthData.status === 'healthy') {
        setApiStatus('connected');
        
        // Build query parameters
        const priceParams = new URLSearchParams({
          start_date: dateRange.start,
          end_date: dateRange.end,
          limit: '1000'
        });
        
        const eventParams = new URLSearchParams();
        if (eventFilters.category !== 'All') {
          eventParams.append('category', eventFilters.category);
        }
        eventParams.append('min_impact', eventFilters.impactLevel);
        
        // Fetch all data
        const [pricesRes, eventsRes, metricsRes] = await Promise.all([
          fetch(`http://localhost:5000/api/prices?${priceParams}`),
          fetch(`http://localhost:5000/api/events?${eventParams}`),
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
      loadFallbackData();
    } finally {
      setLoading(false);
    }
  };

  const loadFallbackData = () => {
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
        id: '1',
        name: 'Gulf War',
        date: '1990-08-02',
        category: 'Geopolitical',
        impact_magnitude: 'Very High',
        description: 'Iraq invades Kuwait leading to supply disruptions',
        price_before: 42.15,
        price_after: 38.72,
        price_change_pct: -8.1
      },
      {
        id: '2',
        name: '2008 Financial Crisis',
        date: '2008-09-15',
        category: 'Economic',
        impact_magnitude: 'Very High',
        description: 'Global financial crisis causing massive demand destruction',
        price_before: 96.88,
        price_after: 64.15,
        price_change_pct: -33.8
      },
      {
        id: '3',
        name: 'COVID-19 Pandemic',
        date: '2020-03-11',
        category: 'Economic',
        impact_magnitude: 'Very High',
        description: 'Global pandemic causing unprecedented demand drop',
        price_before: 35.98,
        price_after: 41.12,
        price_change_pct: 14.3
      }
    ]);
  };

  useEffect(() => {
    fetchData();
  }, [dateRange, eventFilters]);

  const handleDateChange = (e) => {
    const { name, value } = e.target;
    setDateRange(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setEventFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleEventClick = (event) => {
    setSelectedEvent(event);
    
    // Zoom to event date range
    if (event && event.date) {
      const eventDate = new Date(event.date);
      const startDate = new Date(eventDate);
      startDate.setMonth(startDate.getMonth() - 3);
      const endDate = new Date(eventDate);
      endDate.setMonth(endDate.getMonth() + 3);
      
      setDateRange({
        start: startDate.toISOString().split('T')[0],
        end: endDate.toISOString().split('T')[0]
      });
    }
  };

  const handleResetFilters = () => {
    setDateRange({
      start: '2000-01-01',
      end: '2022-12-31'
    });
    setEventFilters({
      category: 'All',
      impactLevel: 'Medium'
    });
    setSelectedEvent(null);
  };

  const handleExportData = () => {
    // Export price data as CSV
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Date,Price,Returns,Volatility\n"
      + priceData.map(item => 
          `${item.date},${item.price},${item.returns},${item.volatility}`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `brent_prices_${dateRange.start}_${dateRange.end}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
        <div className="header-content">
          <h1>Brent Oil Price Intelligence Dashboard</h1>
          <p className="subtitle">Interactive analysis of geopolitical & economic impacts on oil markets (1987-2022)</p>
          <div className={`status-badge ${apiStatus}`}>
            {apiStatus === 'connected' ? '✅ API Connected' : 
             apiStatus === 'error' ? '⚠️ Using Demo Data' : 
             '🔄 Connecting...'}
          </div>
        </div>
        {metrics && (
          <div className="header-stats">
            <div className="stat-item">
              <span className="stat-label">Current Price</span>
              <span className="stat-value">${metrics.basic?.price_statistics?.current?.toFixed(2)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Date Range</span>
              <span className="stat-value">{metrics.basic?.date_range?.start?.split('-')[0]} - {metrics.basic?.date_range?.end?.split('-')[0]}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Events</span>
              <span className="stat-value">{events.length}</span>
            </div>
          </div>
        )}
      </header>

      {/* Main Controls Section */}
      <section className="controls-section">
        <div className="section-header">
          <h2>📊 Dashboard Controls</h2>
          <p>Filter and explore Brent oil price data</p>
        </div>
        
        <div className="controls-grid">
          {/* Date Range Controls */}
          <div className="control-group">
            <h3>📅 Date Range Filter</h3>
            <div className="date-controls">
              <div className="input-group">
                <label htmlFor="start-date">Start Date</label>
                <input
                  type="date"
                  id="start-date"
                  name="start"
                  value={dateRange.start}
                  onChange={handleDateChange}
                  min="1987-05-20"
                  max="2022-11-14"
                  className="date-input"
                />
              </div>
              <div className="input-group">
                <label htmlFor="end-date">End Date</label>
                <input
                  type="date"
                  id="end-date"
                  name="end"
                  value={dateRange.end}
                  onChange={handleDateChange}
                  min="1987-05-20"
                  max="2022-12-31"
                  className="date-input"
                />
              </div>
              <div className="quick-dates">
                <button 
                  onClick={() => setDateRange({ start: '2000-01-01', end: '2022-12-31' })}
                  className="quick-btn"
                >
                  Full Range
                </button>
                <button 
                  onClick={() => setDateRange({ start: '2010-01-01', end: '2020-12-31' })}
                  className="quick-btn"
                >
                  2010s
                </button>
              </div>
            </div>
          </div>

          {/* Event Filter Controls */}
          <div className="control-group">
            <h3>⚡ Event Filters</h3>
            <div className="filter-controls">
              <div className="input-group">
                <label htmlFor="event-category">Category</label>
                <select
                  id="event-category"
                  name="category"
                  value={eventFilters.category}
                  onChange={handleFilterChange}
                  className="filter-select"
                >
                  <option value="All">All Categories</option>
                  <option value="Geopolitical">Geopolitical</option>
                  <option value="Economic">Economic</option>
                  <option value="OPEC Decision">OPEC Decisions</option>
                </select>
              </div>
              
              <div className="input-group">
                <label htmlFor="impact-level">Minimum Impact</label>
                <select
                  id="impact-level"
                  name="impactLevel"
                  value={eventFilters.impactLevel}
                  onChange={handleFilterChange}
                  className="filter-select"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Very High">Very High</option>
                </select>
              </div>
              
              <div className="toggle-group">
                <label className="toggle-label">
                  <input
                    type="checkbox"
                    checked={highlightEvents}
                    onChange={(e) => setHighlightEvents(e.target.checked)}
                    className="toggle-input"
                  />
                  <span className="toggle-slider"></span>
                  <span>Highlight Events</span>
                </label>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="control-group">
            <h3>🛠️ Actions</h3>
            <div className="action-buttons">
              <button onClick={handleResetFilters} className="action-btn secondary">
                🔄 Reset Filters
              </button>
              <button onClick={fetchData} className="action-btn">
                📡 Refresh Data
              </button>
              <button onClick={handleExportData} className="action-btn success">
                📥 Export CSV
              </button>
              {selectedEvent && (
                <button 
                  onClick={() => setSelectedEvent(null)}
                  className="action-btn warning"
                >
                  ✕ Clear Selection
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Selected Event Info */}
        {selectedEvent && (
          <div className="selected-event-info">
            <div className="event-header">
              <h3>Selected Event: {selectedEvent.name}</h3>
              <button 
                onClick={() => setSelectedEvent(null)}
                className="close-btn"
              >
                ✕
              </button>
            </div>
            <div className="event-details-grid">
              <div className="event-detail">
                <span className="detail-label">Date:</span>
                <span className="detail-value">{selectedEvent.date}</span>
              </div>
              <div className="event-detail">
                <span className="detail-label">Category:</span>
                <span className={`detail-value category-${selectedEvent.category.toLowerCase().replace(' ', '-')}`}>
                  {selectedEvent.category}
                </span>
              </div>
              <div className="event-detail">
                <span className="detail-label">Impact:</span>
                <span className={`detail-value impact-${selectedEvent.impact_magnitude.toLowerCase().replace(' ', '-')}`}>
                  {selectedEvent.impact_magnitude}
                </span>
              </div>
              <div className="event-detail">
                <span className="detail-label">Price Change:</span>
                <span className={`detail-value ${selectedEvent.price_change_pct >= 0 ? 'positive' : 'negative'}`}>
                  {selectedEvent.price_change_pct >= 0 ? '+' : ''}{selectedEvent.price_change_pct}%
                </span>
              </div>
            </div>
            {selectedEvent.description && (
              <p className="event-description">{selectedEvent.description}</p>
            )}
          </div>
        )}
      </section>

      {/* Main Dashboard Content */}
      <main className="dashboard-content">
        {/* Price Chart Section */}
        <section className="chart-section">
          <div className="section-header">
            <h2>📈 Historical Price Analysis</h2>
            <p>Brent Oil Price (USD/barrel) with events highlighted</p>
          </div>
          
          <div className="chart-container">
            {priceData.length > 0 ? (
              <div className="price-visualization">
                {/* Simple bar chart */}
                <div className="chart-wrapper">
                  <div className="chart-bars-container">
                    {priceData.map((item, index) => {
                      // Check if this date has an event
                      const eventOnDate = events.find(event => event.date === item.date);
                      const isSelected = selectedEvent && selectedEvent.date === item.date;
                      
                      return (
                        <div
                          key={index}
                          className={`chart-bar ${eventOnDate ? 'has-event' : ''} ${isSelected ? 'selected' : ''}`}
                          style={{
                            height: `${(item.price / 150) * 80}%`,
                            width: `${Math.max(2, 100 / priceData.length)}%`
                          }}
                          onClick={() => eventOnDate && handleEventClick(eventOnDate)}
                          title={`${item.date}: $${item.price.toFixed(2)}${eventOnDate ? `\nEvent: ${eventOnDate.name}` : ''}`}
                        >
                          {eventOnDate && highlightEvents && (
                            <div className="event-marker"></div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                  <div className="chart-axis">
                    <div className="y-axis">
                      <span>$150</span>
                      <span>$100</span>
                      <span>$50</span>
                      <span>$0</span>
                    </div>
                    <div className="x-axis">
                      <span>{priceData[0]?.date}</span>
                      <span>{priceData[Math.floor(priceData.length/2)]?.date}</span>
                      <span>{priceData[priceData.length-1]?.date}</span>
                    </div>
                  </div>
                </div>
                
                {/* Chart Statistics */}
                <div className="chart-stats">
                  <div className="stat-card">
                    <div className="stat-title">Current Price</div>
                    <div className="stat-value">${priceData[priceData.length-1]?.price.toFixed(2)}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-title">Average Price</div>
                    <div className="stat-value">
                      ${(priceData.reduce((sum, item) => sum + item.price, 0) / priceData.length).toFixed(2)}
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-title">Maximum Price</div>
                    <div className="stat-value">
                      ${Math.max(...priceData.map(p => p.price)).toFixed(2)}
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-title">Minimum Price</div>
                    <div className="stat-value">
                      ${Math.min(...priceData.map(p => p.price)).toFixed(2)}
                    </div>
                  </div>
                </div>
                
                {/* Event Legend */}
                <div className="chart-legend">
                  <div className="legend-item">
                    <div className="legend-color normal-bar"></div>
                    <span>Normal Price</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color event-bar"></div>
                    <span>Event Day</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color selected-bar"></div>
                    <span>Selected Event</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-data">
                <p>No price data available for the selected date range.</p>
                <button onClick={() => setDateRange({ start: '2000-01-01', end: '2022-12-31' })}>
                  Reset to Default Range
                </button>
              </div>
            )}
          </div>
        </section>

        {/* Events List Section */}
        <section className="events-section">
          <div className="section-header">
            <h2>📅 Major Events Timeline</h2>
            <p>Click on events to highlight them on the chart</p>
          </div>
          
          <div className="events-container">
            <div className="events-filter-info">
              <span>Showing {events.length} events</span>
              <span>Filtered by: {eventFilters.category} | Min Impact: {eventFilters.impactLevel}</span>
            </div>
            
            <div className="events-list">
              {events.map((event) => (
                <div
                  key={event.id}
                  className={`event-card ${selectedEvent?.id === event.id ? 'selected' : ''}`}
                  onClick={() => handleEventClick(event)}
                >
                  <div className="event-card-header">
                    <h4>{event.name}</h4>
                    <div className="event-tags">
                      <span className={`event-tag category-${event.category.toLowerCase().replace(' ', '-')}`}>
                        {event.category}
                      </span>
                      <span className={`event-tag impact-${event.impact_magnitude.toLowerCase().replace(' ', '-')}`}>
                        {event.impact_magnitude}
                      </span>
                    </div>
                  </div>
                  
                  <div className="event-card-body">
                    <div className="event-date">{event.date}</div>
                    
                    <div className="event-price-change">
                      <div className="price-before">
                        <span className="price-label">Before:</span>
                        <span className="price-value">${event.price_before?.toFixed(2)}</span>
                      </div>
                      <div className="price-arrow">
                        <span className={`arrow ${event.price_change_pct >= 0 ? 'up' : 'down'}`}>
                          {event.price_change_pct >= 0 ? '↗' : '↘'}
                        </span>
                      </div>
                      <div className="price-after">
                        <span className="price-label">After:</span>
                        <span className="price-value">${event.price_after?.toFixed(2)}</span>
                      </div>
                      <div className="price-change">
                        <span className={`change-value ${event.price_change_pct >= 0 ? 'positive' : 'negative'}`}>
                          {event.price_change_pct >= 0 ? '+' : ''}{event.price_change_pct}%
                        </span>
                      </div>
                    </div>
                    
                    {event.description && (
                      <p className="event-description">{event.description}</p>
                    )}
                  </div>
                  
                  <div className="event-card-footer">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEventClick(event);
                      }}
                      className="view-event-btn"
                    >
                      {selectedEvent?.id === event.id ? '✓ Selected' : 'View on Chart'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* API Endpoints Section */}
      <section className="api-section">
        <div className="section-header">
          <h2>🔗 API Endpoints</h2>
          <p>Backend API endpoints for data access</p>
        </div>
        
        <div className="endpoints-grid">
          <a href="http://localhost:5000/api/health" target="_blank" rel="noopener noreferrer" className="endpoint-card">
            <div className="endpoint-method">GET</div>
            <div className="endpoint-path">/api/health</div>
            <div className="endpoint-desc">Health check and API status</div>
          </a>
          
          <a href={`http://localhost:5000/api/prices?start_date=${dateRange.start}&end_date=${dateRange.end}`} 
             target="_blank" rel="noopener noreferrer" className="endpoint-card">
            <div className="endpoint-method">GET</div>
            <div className="endpoint-path">/api/prices</div>
            <div className="endpoint-desc">Historical price data with filtering</div>
          </a>
          
          <a href="http://localhost:5000/api/events" target="_blank" rel="noopener noreferrer" className="endpoint-card">
            <div className="endpoint-method">GET</div>
            <div className="endpoint-path">/api/events</div>
            <div className="endpoint-desc">Geopolitical events with impact analysis</div>
          </a>
          
          <a href="http://localhost:5000/api/metrics" target="_blank" rel="noopener noreferrer" className="endpoint-card">
            <div className="endpoint-method">GET</div>
            <div className="endpoint-path">/api/metrics</div>
            <div className="endpoint-desc">Comprehensive dashboard metrics</div>
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-info">
            <h3>Brent Oil Price Analysis Dashboard</h3>
            <p>Task 3: Interactive Dashboard Development</p>
            <p>Data Range: 1987-05-20 to 2022-11-14</p>
          </div>
          
          <div className="footer-status">
            <div className={`status-indicator ${apiStatus}`}>
              API Status: {apiStatus === 'connected' ? 'Connected' : 'Demo Mode'}
            </div>
            <div className="data-stats">
              <span>📊 {priceData.length} price points</span>
              <span>⚡ {events.length} events</span>
              <span>🕐 {dateRange.start} to {dateRange.end}</span>
            </div>
          </div>
          
          <div className="footer-actions">
            <button onClick={fetchData} className="footer-btn">
              🔄 Refresh
            </button>
            <button onClick={handleResetFilters} className="footer-btn secondary">
              🗑️ Clear Filters
            </button>
            <a href="http://localhost:5000" target="_blank" rel="noopener noreferrer" className="footer-btn">
              🌐 Backend API
            </a>
          </div>
        </div>
        
        <div className="footer-copyright">
          <p>© 2024 Birhan Energies Brent Oil Analysis • Task 3 • Interactive Dashboard</p>
        </div>
      </footer>
    </div>
  );
}

export default App;