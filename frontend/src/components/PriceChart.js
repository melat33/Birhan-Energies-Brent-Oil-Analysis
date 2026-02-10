import React, { useMemo } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
  Area
} from 'recharts';
import { format } from 'date-fns';

const PriceChart = ({ data, events, selectedEvent, changePoints, isLoading }) => {
  const chartData = useMemo(() => {
    return data.map(item => ({
      ...item,
      date: format(new Date(item.Date), 'yyyy-MM-dd'),
      formattedDate: format(new Date(item.Date), 'MMM yyyy'),
    }));
  }, [data]);

  const eventMarkers = useMemo(() => {
    return events.map(event => ({
      ...event,
      x: new Date(event.date).getTime(),
    }));
  }, [events]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900/95 backdrop-blur-sm border border-gray-700 rounded-lg p-4 shadow-2xl">
          <p className="text-gray-300 mb-2">{label}</p>
          <div className="space-y-1">
            <p className="text-blue-300">
              <span className="text-gray-400">Price: </span>
              ${payload[0].value.toFixed(2)}
            </p>
            {payload[1] && (
              <p className="text-purple-300">
                <span className="text-gray-400">Volatility: </span>
                {payload[1].value.toFixed(2)}%
              </p>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="bg-gray-800/30 rounded-xl p-6 border border-gray-700 h-[400px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading price data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/30 rounded-xl p-4 border border-gray-700">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-lg font-semibold">Historical Price & Volatility</h3>
          <p className="text-gray-400 text-sm">Brent Oil Price (USD/barrel) with 30-day volatility</p>
        </div>
        <div className="flex gap-2">
          <span className="flex items-center gap-1 text-sm">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            Price
          </span>
          <span className="flex items-center gap-1 text-sm">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            Volatility
          </span>
        </div>
      </div>

      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="formattedDate"
              stroke="#9CA3AF"
              fontSize={12}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis 
              yAxisId="left"
              stroke="#60A5FA"
              fontSize={12}
              tickFormatter={(value) => `$${value}`}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              stroke="#A855F7"
              fontSize={12}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Price Line */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="Price"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={false}
              name="Price (USD)"
              activeDot={{ r: 6, fill: '#3B82F6' }}
            />
            
            {/* Volatility Area */}
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="Volatility"
              stroke="#A855F7"
              fill="#A855F7"
              fillOpacity={0.1}
              strokeWidth={1}
              name="Volatility (%)"
            />
            
            {/* Selected Event Highlight */}
            {selectedEvent && (
              <ReferenceLine
                x={selectedEvent.date}
                stroke="#F59E0B"
                strokeWidth={2}
                strokeDasharray="5 5"
                label={{
                  value: selectedEvent.event_name,
                  position: 'top',
                  fill: '#F59E0B',
                  fontSize: 12,
                  fontWeight: 'bold'
                }}
              />
            )}
            
            {/* Change Points */}
            {changePoints.map((cp, index) => (
              <ReferenceLine
                key={index}
                x={cp.date}
                stroke="#EF4444"
                strokeWidth={1}
                strokeDasharray="3 3"
                label={{
                  value: 'CP',
                  position: 'insideTopRight',
                  fill: '#EF4444',
                  fontSize: 10
                }}
              />
            ))}
            
            {/* Event Markers */}
            {eventMarkers.map((event, index) => (
              <ReferenceLine
                key={index}
                x={event.date}
                stroke={event.category === 'Geopolitical' ? '#DC2626' : 
                       event.category === 'Economic' ? '#10B981' : 
                       event.category === 'OPEC Decision' ? '#8B5CF6' : '#F59E0B'}
                strokeWidth={1}
              />
            ))}
            
            <Brush 
              dataKey="formattedDate" 
              height={30}
              stroke="#4B5563"
              travellerWidth={10}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
        <div className="bg-gray-800/50 rounded p-2">
          <p className="text-gray-400">Current</p>
          <p className="text-xl font-bold">
            ${chartData[chartData.length - 1]?.Price?.toFixed(2) || '0'}
          </p>
        </div>
        <div className="bg-gray-800/50 rounded p-2">
          <p className="text-gray-400">Average</p>
          <p className="text-xl font-bold">
            ${(chartData.reduce((sum, d) => sum + d.Price, 0) / chartData.length).toFixed(2) || '0'}
          </p>
        </div>
        <div className="bg-gray-800/50 rounded p-2">
          <p className="text-gray-400">Max</p>
          <p className="text-xl font-bold">
            ${Math.max(...chartData.map(d => d.Price)).toFixed(2) || '0'}
          </p>
        </div>
        <div className="bg-gray-800/50 rounded p-2">
          <p className="text-gray-400">Min</p>
          <p className="text-xl font-bold">
            ${Math.min(...chartData.map(d => d.Price)).toFixed(2) || '0'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PriceChart;