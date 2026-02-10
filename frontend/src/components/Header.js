import React from 'react';
import { 
  ChartBarIcon, 
  BoltIcon, 
  CalendarIcon,
  CurrencyDollarIcon 
} from '@heroicons/react/24/outline';

const Header = ({ metrics }) => {
  const statCards = [
    {
      title: 'Current Price',
      value: `$${metrics?.price_stats?.current || '0'}`,
      icon: CurrencyDollarIcon,
      color: 'bg-gradient-to-r from-green-500 to-emerald-600',
      change: '+2.3%'
    },
    {
      title: 'Total Events',
      value: metrics?.event_stats?.total_events || '0',
      icon: BoltIcon,
      color: 'bg-gradient-to-r from-blue-500 to-cyan-600',
      subtitle: `${metrics?.event_stats?.high_impact_events || '0'} high impact`
    },
    {
      title: 'Change Points',
      value: metrics?.change_points?.detected || '0',
      icon: ChartBarIcon,
      color: 'bg-gradient-to-r from-purple-500 to-pink-600',
      subtitle: 'Statistical breaks detected'
    },
    {
      title: 'Data Range',
      value: `${metrics?.date_range?.start?.split('-')[0] || '1987'} - ${metrics?.date_range?.end?.split('-')[0] || '2022'}`,
      icon: CalendarIcon,
      color: 'bg-gradient-to-r from-orange-500 to-red-600',
      subtitle: `${metrics?.total_days?.toLocaleString() || '0'} days`
    }
  ];

  return (
    <header className="sticky top-0 z-50 bg-gray-900/95 backdrop-blur-lg border-b border-gray-800">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col md:flex-row justify-between items-center mb-6">
          <div className="mb-4 md:mb-0">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Brent Oil Price Intelligence
            </h1>
            <p className="text-gray-400 mt-1">
              Interactive analysis of geopolitical & economic impacts on oil markets
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="px-3 py-1 bg-gray-800 rounded-full text-sm">
              Beta v1.0
            </span>
            <button className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg hover:opacity-90 transition">
              Export Report
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                className="bg-gray-800/50 rounded-xl p-4 border border-gray-700 hover:border-gray-600 transition-all duration-300"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                    {stat.subtitle && (
                      <p className="text-gray-500 text-sm mt-1">{stat.subtitle}</p>
                    )}
                    {stat.change && (
                      <span className="text-green-400 text-sm mt-1">{stat.change}</span>
                    )}
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </header>
  );
};

export default Header;