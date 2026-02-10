import React, { useState, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Line, Bar } from 'react-chartjs-2';
import PriceChart from '../components/PriceChart';
import EventTimeline from '../components/EventTimeline';
import MetricsPanel from '../components/MetricsPanel';
import Filters from '../components/Filters';
import { 
  usePrices, 
  useEvents, 
  useChangePoints,
  useMetrics 
} from '../hooks/useApiData';
import { 
  CalendarIcon,
  ArrowTrendingUpIcon,
  BoltIcon,
  ChartBarIcon,
  ArrowsRightLeftIcon
} from '@heroicons/react/24/outline';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
);

const Dashboard = ({ apiStatus, metrics, isLoading }) => {
  const [dateRange, setDateRange] = useState({
    start: '2000-01-01',
    end: '2022-12-31'
  });
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [chartType, setChartType] = useState('line');
  const [showVolatility, setShowVolatility] = useState(true);
  const [eventCategory, setEventCategory] = useState('All');
  const [impactFilter, setImpactFilter] = useState('Medium');

  // React Query hooks for data fetching
  const { 
    data: priceData, 
    isLoading: pricesLoading,
    error: pricesError 
  } = usePrices(dateRange);

  const {
    data: eventsData,
    isLoading: eventsLoading,
    error: eventsError
  } = useEvents({ category: eventCategory, minImpact: impactFilter });

  const {
    data: changePointsData,
    isLoading: cpLoading,
    error: cpError
  } = useChangePoints();

  const {
    data: detailedMetrics,
    isLoading: metricsLoading
  } = useMetrics();

  // Process chart data
  const chartData = useMemo(() => {
    if (!priceData?.data) return null;

    const prices = priceData.data.map(d => ({
      x: new Date(d.date),
      y: d.price,
      volatility: d.volatility,
      returns: d.returns
    }));

    const labels = priceData.data.map(d => d.date);
    
    return {
      labels,
      datasets: [
        {
          label: 'Brent Oil Price (USD)',
          data: prices.map(p => ({ x: p.x, y: p.y })),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.1,
          yAxisID: 'y',
        },
        ...(showVolatility ? [{
          label: '30-Day Volatility',
          data: prices.map(p => ({ x: p.x, y: p.volatility * 100 })),
          borderColor: 'rgb(139, 92, 246)',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          borderWidth: 1,
          borderDash: [5, 5],
          fill: false,
          yAxisID: 'y1',
        }] : []),
      ]
    };
  }, [priceData, showVolatility]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#9CA3AF',
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: '#D1D5DB',
        bodyColor: '#9CA3AF',
        borderColor: '#374151',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            if (label.includes('Price')) {
              return `${label}: $${value.toFixed(2)}`;
            } else if (label.includes('Volatility')) {
              return `${label}: ${value.toFixed(2)}%`;
            }
            return `${label}: ${value}`;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'month',
          displayFormats: {
            month: 'MMM yyyy'
          }
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)'
        },
        ticks: {
          color: '#9CA3AF',
          maxRotation: 45,
          minRotation: 45
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        grid: {
          color: 'rgba(55, 65, 81, 0.3)'
        },
        ticks: {
          color: '#9CA3AF',
          callback: (value) => `$${value}`
        },
        title: {
          display: true,
          text: 'Price (USD)',
          color: '#9CA3AF'
        }
      },
      y1: {
        type: 'linear',
        display: showVolatility,
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: '#9CA3AF',
          callback: (value) => `${value}%`
        },
        title: {
          display: true,
          text: 'Volatility (%)',
          color: '#9CA3AF'
        }
      }
    }
  };

  // Handle event selection
  const handleEventSelect = (event) => {
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

  // Handle date range change
  const handleDateRangeChange = (newRange) => {
    setDateRange(newRange);
  };

  // Handle filters change
  const handleFiltersChange = (filters) => {
    if (filters.category) setEventCategory(filters.category);
    if (filters.impact) setImpactFilter(filters.impact);
    if (filters.chartType) setChartType(filters.chartType);
    if (filters.showVolatility !== undefined) setShowVolatility(filters.showVolatility);
  };

  // Calculate performance metrics
  const performanceMetrics = useMemo(() => {
    if (!priceData?.data) return null;
    
    const prices = priceData.data.map(d => d.price);
    const returns = priceData.data.map(d => d.returns);
    
    const totalReturn = ((prices[prices.length - 1] - prices[0]) / prices[0]) * 100;
    const positiveDays = returns.filter(r => r > 0).length;
    const negativeDays = returns.filter(r => r < 0).length;
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    
    return {
      totalReturn: totalReturn.toFixed(1),
      positiveDays,
      negativeDays,
      winRate: ((positiveDays / returns.length) * 100).toFixed(1),
      maxPrice: maxPrice.toFixed(2),
      minPrice: minPrice.toFixed(2),
      currentPrice: prices[prices.length - 1].toFixed(2)
    };
  }, [priceData]);

  // Loading state
  if (pricesLoading || eventsLoading || metricsLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner-container">
          <div className="spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (pricesError || eventsError) {
    return (
      <div className="dashboard-error">
        <div className="error-container">
          <h3>Unable to load data</h3>
          <p>Please check your connection and try again.</p>
          <button onClick={() => window.location.reload()} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Quick Stats Bar */}
      <div className="quick-stats-bar">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-item">
              <CalendarIcon className="stat-icon" />
              <div>
                <div className="stat-value">{priceData?.metadata?.count || 0}</div>
                <div className="stat-label">Data Points</div>
              </div>
            </div>
            <div className="stat-item">
              <ArrowTrendingUpIcon className="stat-icon" />
              <div>
                <div className="stat-value">{performanceMetrics?.totalReturn || '0'}%</div>
                <div className="stat-label">Total Return</div>
              </div>
            </div>
            <div className="stat-item">
              <BoltIcon className="stat-icon" />
              <div>
                <div className="stat-value">{eventsData?.count || 0}</div>
                <div className="stat-label">Events</div>
              </div>
            </div>
            <div className="stat-item">
              <ArrowsRightLeftIcon className="stat-icon" />
              <div>
                <div className="stat-value">{changePointsData?.count || 0}</div>
                <div className="stat-label">Change Points</div>
              </div>
            </div>
            <div className="stat-item">
              <ChartBarIcon className="stat-icon" />
              <div>
                <div className="stat-value">{performanceMetrics?.winRate || '0'}%</div>
                <div className="stat-label">Win Rate</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Dashboard Grid */}
      <div className="container">
        <div className="dashboard-grid">
          {/* Left Column - Main Chart & Filters */}
          <div className="main-chart-section">
            {/* Filters */}
            <Filters
              dateRange={dateRange}
              onDateRangeChange={handleDateRangeChange}
              eventCategory={eventCategory}
              impactFilter={impactFilter}
              chartType={chartType}
              showVolatility={showVolatility}
              onFiltersChange={handleFiltersChange}
            />
            
            {/* Main Chart */}
            <div className="chart-container">
              <div className="chart-header">
                <h3>Brent Oil Price Analysis</h3>
                <div className="chart-controls">
                  <button
                    className={`chart-type-btn ${chartType === 'line' ? 'active' : ''}`}
                    onClick={() => setChartType('line')}
                  >
                    Line
                  </button>
                  <button
                    className={`chart-type-btn ${chartType === 'bar' ? 'active' : ''}`}
                    onClick={() => setChartType('bar')}
                  >
                    Bar
                  </button>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={showVolatility}
                      onChange={(e) => setShowVolatility(e.target.checked)}
                    />
                    <span className="toggle-slider"></span>
                    <span className="toggle-label">Show Volatility</span>
                  </label>
                </div>
              </div>
              
              <div className="chart-wrapper">
                {chartData && chartType === 'line' && (
                  <Line data={chartData} options={chartOptions} />
                )}
                {chartData && chartType === 'bar' && (
                  <Bar data={chartData} options={chartOptions} />
                )}
              </div>
              
              <div className="chart-footer">
                <div className="price-indicators">
                  <div className="price-indicator">
                    <span className="indicator-label">Current:</span>
                    <span className="indicator-value">${performanceMetrics?.currentPrice || '0'}</span>
                  </div>
                  <div className="price-indicator">
                    <span className="indicator-label">High:</span>
                    <span className="indicator-value">${performanceMetrics?.maxPrice || '0'}</span>
                  </div>
                  <div className="price-indicator">
                    <span className="indicator-label">Low:</span>
                    <span className="indicator-value">${performanceMetrics?.minPrice || '0'}</span>
                  </div>
                  <div className="price-indicator">
                    <span className="indicator-label">Avg Daily Return:</span>
                    <span className={`indicator-value ${(priceData?.data?.[0]?.returns || 0) >= 0 ? 'positive' : 'negative'}`}>
                      {(priceData?.data?.[0]?.returns || 0).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Event Timeline */}
            <div className="timeline-section">
              <EventTimeline
                events={eventsData?.data || []}
                selectedEvent={selectedEvent}
                onEventSelect={handleEventSelect}
              />
            </div>
          </div>
          
          {/* Right Column - Metrics & Details */}
          <div className="sidebar-section">
            {/* Metrics Panel */}
            <MetricsPanel
              metrics={detailedMetrics?.data}
              performance={performanceMetrics}
              changePoints={changePointsData?.data}
              isLoading={metricsLoading}
            />
            
            {/* Selected Event Details */}
            {selectedEvent && (
              <div className="event-details-card">
                <div className="card-header">
                  <h4>Event Analysis</h4>
                  <button 
                    className="close-btn"
                    onClick={() => setSelectedEvent(null)}
                  >
                    ✕
                  </button>
                </div>
                <div className="event-content">
                  <h5>{selectedEvent.name}</h5>
                  <div className="event-meta">
                    <span className="event-date">{selectedEvent.date}</span>
                    <span className={`event-category ${selectedEvent.category.toLowerCase().replace(/\s+/g, '-')}`}>
                      {selectedEvent.category}
                    </span>
                    <span className={`event-impact impact-${selectedEvent.impact_magnitude.toLowerCase().replace(/\s+/g, '-')}`}>
                      {selectedEvent.impact_magnitude} Impact
                    </span>
                  </div>
                  <p className="event-description">{selectedEvent.description}</p>
                  <div className="event-stats">
                    <div className="stat">
                      <div className="stat-value">${selectedEvent.price_before || '0'}</div>
                      <div className="stat-label">Price Before</div>
                    </div>
                    <div className="stat">
                      <div className="stat-value">${selectedEvent.price_after || '0'}</div>
                      <div className="stat-label">Price After</div>
                    </div>
                    <div className="stat">
                      <div className={`stat-value ${(selectedEvent.price_change_pct || 0) >= 0 ? 'positive' : 'negative'}`}>
                        {selectedEvent.price_change_pct || '0'}%
                      </div>
                      <div className="stat-label">Change</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Market Regime */}
            <div className="market-regime-card">
              <h4>Market Regime</h4>
              <div className="regime-indicator">
                <div className="regime-dot"></div>
                <div className="regime-text">
                  <div className="regime-title">Current: Neutral</div>
                  <div className="regime-subtitle">Low volatility, stable prices</div>
                </div>
              </div>
              <div className="regime-stats">
                <div className="regime-stat">
                  <div className="stat-value">60%</div>
                  <div className="stat-label">Bullish Days</div>
                </div>
                <div className="regime-stat">
                  <div className="stat-value">25%</div>
                  <div className="stat-label">Bearish Days</div>
                </div>
                <div className="regime-stat">
                  <div className="stat-value">15%</div>
                  <div className="stat-label">Neutral Days</div>
                </div>
              </div>
            </div>
            
            {/* Export Options */}
            <div className="export-card">
              <h4>Export Data</h4>
              <p>Download analysis data for further processing</p>
              <div className="export-options">
                <a 
                  href="http://localhost:5000/api/export/prices?format=csv" 
                  className="export-btn"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  📊 Price Data (CSV)
                </a>
                <a 
                  href="http://localhost:5000/api/export/events?format=json" 
                  className="export-btn"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  📅 Events Data (JSON)
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;