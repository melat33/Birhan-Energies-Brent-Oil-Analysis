import React, { useState, useEffect } from 'react';
import PriceChart from './PriceChart';
import EventTimeline from './EventTimeline';
import VolatilityChart from './VolatilityChart';
import ImpactMetrics from './ImpactMetrics';
import EventSelector from './EventSelector';
import DateRangeFilter from './DateRangeFilter';
import { 
  fetchHistoricalPrices, 
  fetchEvents, 
  fetchVolatilityMetrics,
  fetchChangePoints 
} from '../utils/api';
import { ArrowsRightLeftIcon, FilterIcon, CalendarDaysIcon } from '@heroicons/react/24/outline';

const Dashboard = () => {
  const [priceData, setPriceData] = useState([]);
  const [events, setEvents] = useState([]);
  const [volatilityData, setVolatilityData] = useState([]);
  const [changePoints, setChangePoints] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [dateRange, setDateRange] = useState({
    start: '2000-01-01',
    end: '2022-12-31'
  });
  const [eventCategory, setEventCategory] = useState('All');
  const [isLoading, setIsLoading] = useState({
    prices: true,
    events: true,
    volatility: true,
    changePoints: true
  });

  const loadData = async () => {
    try {
      setIsLoading(prev => ({ ...prev, prices: true }));
      const prices = await fetchHistoricalPrices(dateRange);
      setPriceData(prices.data);

      setIsLoading(prev => ({ ...prev, events: true }));
      const eventsData = await fetchEvents(eventCategory);
      setEvents(eventsData.data);

      setIsLoading(prev => ({ ...prev, volatility: true }));
      const volData = await fetchVolatilityMetrics();
      setVolatilityData(volData.data);

      setIsLoading(prev => ({ ...prev, changePoints: true }));
      const cpData = await fetchChangePoints();
      setChangePoints(cpData.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setIsLoading({
        prices: false,
        events: false,
        volatility: false,
        changePoints: false
      });
    }
  };

  useEffect(() => {
    loadData();
  }, [dateRange, eventCategory]);

  const handleEventSelect = (event) => {
    setSelectedEvent(event);
  };

  const handleDateRangeChange = (newRange) => {
    setDateRange(newRange);
  };

  const handleCategoryChange = (category) => {
    setEventCategory(category);
  };

  return (
    <div className="space-y-6">
      {/* Controls Section */}
      <div className="bg-gray-800/30 rounded-xl p-4 border border-gray-700">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div>
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <FilterIcon className="h-5 w-5" />
              Dashboard Controls
            </h2>
            <p className="text-gray-400 text-sm">
              Filter and explore Brent oil price data
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 w-full lg:w-auto">
            <DateRangeFilter 
              onDateRangeChange={handleDateRangeChange}
              currentRange={dateRange}
            />
            
            <div className="flex items-center gap-2">
              <CalendarDaysIcon className="h-5 w-5 text-gray-400" />
              <select
                value={eventCategory}
                onChange={(e) => handleCategoryChange(e.target.value)}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="All">All Event Categories</option>
                <option value="Geopolitical">Geopolitical</option>
                <option value="Economic">Economic</option>
                <option value="OPEC Decision">OPEC Decisions</option>
                <option value="Conflict">Conflicts</option>
              </select>
            </div>
            
            <button
              onClick={loadData}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg hover:opacity-90 transition flex items-center gap-2 justify-center"
            >
              <ArrowsRightLeftIcon className="h-4 w-4" />
              Refresh Data
            </button>
          </div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Chart */}
        <div className="lg:col-span-2 space-y-6">
          <PriceChart 
            data={priceData} 
            events={events}
            selectedEvent={selectedEvent}
            changePoints={changePoints}
            isLoading={isLoading.prices}
          />
          
          <VolatilityChart 
            data={volatilityData}
            isLoading={isLoading.volatility}
          />
        </div>

        {/* Right Column - Events & Metrics */}
        <div className="space-y-6">
          <EventSelector 
            events={events}
            onEventSelect={handleEventSelect}
            selectedEvent={selectedEvent}
            isLoading={isLoading.events}
          />
          
          <ImpactMetrics 
            events={events}
            changePoints={changePoints}
            isLoading={isLoading.changePoints}
          />
        </div>
      </div>

      {/* Bottom Row - Timeline */}
      <div>
        <EventTimeline 
          events={events}
          onEventSelect={handleEventSelect}
          selectedEvent={selectedEvent}
        />
      </div>

      {/* Loading Overlay */}
      {Object.values(isLoading).some(loading => loading) && (
        <div className="fixed inset-0 bg-gray-900/80 flex items-center justify-center z-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-300">Loading dashboard data...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;