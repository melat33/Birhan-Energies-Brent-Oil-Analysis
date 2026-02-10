import React, { useState } from 'react';
import { format } from 'date-fns';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

const EventTimeline = ({ events, onEventSelect, selectedEvent }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const eventsPerPage = 5;

  const sortedEvents = [...events].sort((a, b) => 
    new Date(b.date) - new Date(a.date)
  );

  const totalPages = Math.ceil(sortedEvents.length / eventsPerPage);
  const currentEvents = sortedEvents.slice(
    currentPage * eventsPerPage,
    (currentPage + 1) * eventsPerPage
  );

  const getCategoryColor = (category) => {
    switch(category) {
      case 'Geopolitical': return 'bg-red-500';
      case 'Economic': return 'bg-green-500';
      case 'OPEC Decision': return 'bg-purple-500';
      case 'Conflict': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  const getImpactColor = (impact) => {
    switch(impact) {
      case 'Very High': return 'text-red-400';
      case 'High': return 'text-orange-400';
      case 'Medium': return 'text-yellow-400';
      case 'Low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const handlePrevious = () => {
    setCurrentPage(prev => Math.max(prev - 1, 0));
  };

  const handleNext = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages - 1));
  };

  return (
    <div className="bg-gray-800/30 rounded-xl p-4 border border-gray-700">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-lg font-semibold">Event Timeline</h3>
          <p className="text-gray-400 text-sm">Chronological view of key events</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrevious}
            disabled={currentPage === 0}
            className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeftIcon className="h-4 w-4" />
          </button>
          <span className="text-sm text-gray-400">
            {currentPage + 1} / {totalPages}
          </span>
          <button
            onClick={handleNext}
            disabled={currentPage === totalPages - 1}
            className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRightIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {currentEvents.map((event, index) => (
          <div
            key={index}
            onClick={() => onEventSelect(event)}
            className={`p-4 rounded-lg border cursor-pointer transition-all duration-300 hover:scale-[1.02] ${
              selectedEvent?.id === event.id
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-3 h-3 rounded-full ${getCategoryColor(event.category)}`}></div>
                  <h4 className="font-semibold">{event.event_name}</h4>
                  <span className="text-xs px-2 py-1 bg-gray-700 rounded-full">
                    {event.category}
                  </span>
                  <span className={`text-xs font-medium ${getImpactColor(event.impact_magnitude)}`}>
                    {event.impact_magnitude} Impact
                  </span>
                </div>
                
                <p className="text-gray-400 text-sm mb-3">{event.description}</p>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                  <div className="bg-gray-900/50 rounded p-2">
                    <p className="text-gray-400">Date</p>
                    <p>{format(new Date(event.date), 'MMM dd, yyyy')}</p>
                  </div>
                  <div className="bg-gray-900/50 rounded p-2">
                    <p className="text-gray-400">Price Change</p>
                    <p className={event.price_change_pct >= 0 ? 'text-green-400' : 'text-red-400'}>
                      {event.price_change_pct >= 0 ? '+' : ''}{event.price_change_pct}%
                    </p>
                  </div>
                  <div className="bg-gray-900/50 rounded p-2">
                    <p className="text-gray-400">Before</p>
                    <p>${event.before_price}</p>
                  </div>
                  <div className="bg-gray-900/50 rounded p-2">
                    <p className="text-gray-400">After</p>
                    <p>${event.after_price}</p>
                  </div>
                </div>
              </div>
              
              <button className="ml-4 px-3 py-1 text-sm bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition">
                Analyze
              </button>
            </div>
            
            {event.volatility_at_event > 30 && (
              <div className="mt-3 p-2 bg-red-900/20 border border-red-800 rounded">
                <p className="text-red-400 text-sm">
                  ⚡ High volatility period: {event.volatility_at_event}%
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EventTimeline;