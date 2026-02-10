from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure cache
cache_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

class DataManager:
    """Enhanced data management with caching"""
    
    def __init__(self):
        self.price_data = None
        self.events_data = None
        self.change_points = None
        self.impacts = None
        self.load_all_data()
    
    def load_price_data(self):
        """Load and preprocess price data"""
        try:
            price_path = DATA_DIR / 'raw' / 'BrentOilPrices.csv'
            if not price_path.exists():
                logger.error(f"Price file not found: {price_path}")
                return None
            
            df = pd.read_csv(price_path)
            
            # Handle different date formats
            date_formats = ['%d-%b-%y', '%Y-%m-%d', '%m/%d/%Y']
            for fmt in date_formats:
                try:
                    df['Date'] = pd.to_datetime(df['Date'], format=fmt)
                    break
                except:
                    continue
            else:
                df['Date'] = pd.to_datetime(df['Date'])
            
            # Sort and clean
            df = df.sort_values('Date').reset_index(drop=True)
            
            # Calculate metrics
            df['Returns'] = df['Price'].pct_change() * 100
            df['Log_Returns'] = np.log(df['Price']).diff()
            
            # Multiple volatility windows
            for window in [7, 30, 90]:
                df[f'Volatility_{window}d'] = df['Returns'].rolling(window).std() * np.sqrt(252)
            
            # Moving averages
            df['MA_7'] = df['Price'].rolling(7).mean()
            df['MA_30'] = df['Price'].rolling(30).mean()
            df['MA_90'] = df['Price'].rolling(90).mean()
            
            logger.info(f"✅ Price data loaded: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error loading price data: {e}")
            return None
    
    def load_events_data(self):
        """Load events data"""
        try:
            events_path = DATA_DIR / 'raw' / 'events_1987_2022.csv'
            if events_path.exists():
                df = pd.read_csv(events_path)
            else:
                # Sample events based on your Task 2
                df = pd.DataFrame([
                    {
                        'Event_Name': 'Gulf War',
                        'Start_Date': '1990-08-02',
                        'Category': 'Geopolitical',
                        'Impact_Magnitude': 'Very High',
                        'Description': 'Iraq invades Kuwait, leading to Gulf War and oil supply disruptions',
                        'Duration_Days': 210
                    },
                    {
                        'Event_Name': '2008 Financial Crisis',
                        'Start_Date': '2008-09-15',
                        'Category': 'Economic',
                        'Impact_Magnitude': 'Very High',
                        'Description': 'Global financial crisis causing massive demand destruction',
                        'Duration_Days': 180
                    },
                    {
                        'Event_Name': 'OPEC Price War 2014',
                        'Start_Date': '2014-11-27',
                        'Category': 'OPEC Decision',
                        'Impact_Magnitude': 'High',
                        'Description': 'OPEC maintains production despite oversupply, triggering price collapse',
                        'Duration_Days': 365
                    },
                    {
                        'Event_Name': 'COVID-19 Pandemic',
                        'Start_Date': '2020-03-11',
                        'Category': 'Economic',
                        'Impact_Magnitude': 'Very High',
                        'Description': 'Global pandemic causing unprecedented demand drop',
                        'Duration_Days': 180
                    },
                    {
                        'Event_Name': 'Russia-Ukraine War',
                        'Start_Date': '2022-02-24',
                        'Category': 'Geopolitical',
                        'Impact_Magnitude': 'Very High',
                        'Description': 'Russian invasion of Ukraine triggering sanctions and supply concerns',
                        'Duration_Days': 90
                    }
                ])
            
            df['Start_Date'] = pd.to_datetime(df['Start_Date'])
            df['End_Date'] = df['Start_Date'] + pd.to_timedelta(df.get('Duration_Days', 30), unit='d')
            
            logger.info(f"✅ Events data loaded: {len(df)} events")
            return df
            
        except Exception as e:
            logger.error(f"Error loading events data: {e}")
            return None
    
    def load_all_data(self):
        """Load all datasets"""
        self.price_data = self.load_price_data()
        self.events_data = self.load_events_data()
        
        # Load processed data
        try:
            cp_path = DATA_DIR / 'processed' / 'change_points.csv'
            if cp_path.exists():
                self.change_points = pd.read_csv(cp_path)
                if 'date' in self.change_points.columns:
                    self.change_points['date'] = pd.to_datetime(self.change_points['date'])
        except:
            self.change_points = pd.DataFrame()
        
        try:
            impacts_path = DATA_DIR / 'processed' / 'event_impacts.csv'
            if impacts_path.exists():
                self.impacts = pd.read_csv(impacts_path)
        except:
            self.impacts = pd.DataFrame()
        
        logger.info("✅ All data loaded successfully")
    
    def get_filtered_data(self, start_date=None, end_date=None):
        """Get filtered price data"""
        df = self.price_data.copy()
        
        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df['Date'] >= start_date]
        
        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df['Date'] <= end_date]
        
        return df
    
    def calculate_metrics(self, df=None):
        """Calculate comprehensive metrics"""
        if df is None:
            df = self.price_data
        
        return {
            'price': {
                'current': float(df['Price'].iloc[-1]),
                'average': float(df['Price'].mean()),
                'max': float(df['Price'].max()),
                'min': float(df['Price'].min()),
                'std': float(df['Price'].std()),
                'q1': float(df['Price'].quantile(0.25)),
                'median': float(df['Price'].quantile(0.5)),
                'q3': float(df['Price'].quantile(0.75))
            },
            'returns': {
                'average_daily': float(df['Returns'].mean()),
                'volatility_30d': float(df['Volatility_30d'].iloc[-1]) if 'Volatility_30d' in df.columns else 0,
                'sharpe_ratio': float(df['Returns'].mean() / df['Returns'].std() * np.sqrt(252)) if df['Returns'].std() > 0 else 0
            },
            'periods': {
                'bull_market': len(df[df['Returns'] > 0]),
                'bear_market': len(df[df['Returns'] < 0])
            }
        }

# Initialize data manager
data_manager = DataManager()

# API Response wrapper
def api_response(success=True, data=None, message="", error=None, code=200):
    return jsonify({
        'success': success,
        'data': data,
        'message': message,
        'error': error,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), code

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return api_response(False, None, "Resource not found", str(error), 404)

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return api_response(False, None, "Internal server error", "Contact administrator", 500)

@app.errorhandler(400)
def bad_request(error):
    return api_response(False, None, "Bad request", str(error), 400)

# Health endpoint
@app.route('/api/health', methods=['GET'])
@cache.cached(timeout=60)
def health_check():
    """Comprehensive health check"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Brent Oil API',
        'version': '1.0.0',
        'data_loaded': data_manager.price_data is not None,
        'records_count': len(data_manager.price_data) if data_manager.price_data else 0,
        'events_count': len(data_manager.events_data) if data_manager.events_data else 0,
        'uptime': '0 days'  # Would implement with startup time
    }
    return api_response(True, health_status, "API is operational")

# Historical prices with filtering
@app.route('/api/prices', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_prices():
    """Get historical prices with advanced filtering"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 1000))
        resample = request.args.get('resample')  # daily, weekly, monthly
        
        # Get filtered data
        df = data_manager.get_filtered_data(start_date, end_date)
        
        # Resample if requested
        if resample == 'weekly':
            df = df.resample('W', on='Date').agg({
                'Price': 'mean',
                'Returns': 'mean',
                'Volatility_30d': 'mean'
            }).reset_index()
        elif resample == 'monthly':
            df = df.resample('M', on='Date').agg({
                'Price': 'mean',
                'Returns': 'mean',
                'Volatility_30d': 'mean'
            }).reset_index()
        
        # Limit results
        df = df.tail(limit)
        
        # Convert to JSON format
        data = []
        for _, row in df.iterrows():
            data.append({
                'date': row['Date'].strftime('%Y-%m-%d'),
                'price': float(row['Price']),
                'returns': float(row['Returns']) if pd.notna(row['Returns']) else 0,
                'volatility': float(row.get('Volatility_30d', 0)) if pd.notna(row.get('Volatility_30d', 0)) else 0,
                'ma_7': float(row.get('MA_7', 0)) if pd.notna(row.get('MA_7', 0)) else None,
                'ma_30': float(row.get('MA_30', 0)) if pd.notna(row.get('MA_30', 0)) else None,
                'ma_90': float(row.get('MA_90', 0)) if pd.notna(row.get('MA_90', 0)) else None
            })
        
        # Calculate additional metrics
        metrics = data_manager.calculate_metrics(df)
        
        return api_response(True, {
            'data': data,
            'metadata': {
                'count': len(data),
                'start_date': df['Date'].min().strftime('%Y-%m-%d'),
                'end_date': df['Date'].max().strftime('%Y-%m-%d'),
                'resample': resample or 'daily',
                'limit': limit
            },
            'metrics': metrics
        }, f"Retrieved {len(data)} price records")
        
    except Exception as e:
        logger.error(f"Error in get_prices: {e}")
        return api_response(False, None, "Failed to retrieve prices", str(e), 500)

# Enhanced events endpoint
@app.route('/api/events', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def get_events():
    """Get events with impact analysis"""
    try:
        category = request.args.get('category')
        min_impact = request.args.get('min_impact', 'Medium')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        df = data_manager.events_data.copy()
        
        # Apply filters
        if category and category != 'All':
            df = df[df['Category'] == category]
        
        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df['Start_Date'] >= start_date]
        
        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df['Start_Date'] <= end_date]
        
        # Impact magnitude filter
        impact_order = {'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}
        min_level = impact_order.get(min_impact, 1)
        df['impact_level'] = df['Impact_Magnitude'].map(impact_order)
        df = df[df['impact_level'] >= min_level]
        
        # Enrich with price data
        events_list = []
        for idx, event in df.iterrows():
            event_date = event['Start_Date']
            
            # Find price data around event
            price_window = data_manager.price_data[
                (data_manager.price_data['Date'] >= event_date - pd.Timedelta(days=30)) &
                (data_manager.price_data['Date'] <= event_date + pd.Timedelta(days=30))
            ]
            
            if len(price_window) > 0:
                price_before = price_window[price_window['Date'] < event_date]['Price'].mean()
                price_after = price_window[price_window['Date'] > event_date]['Price'].mean()
                price_change = ((price_after - price_before) / price_before * 100) if price_before > 0 else 0
                volatility = price_window['Volatility_30d'].mean()
            else:
                price_before = price_after = price_change = volatility = 0
            
            events_list.append({
                'id': f"event_{idx}",
                'name': event['Event_Name'],
                'date': event_date.strftime('%Y-%m-%d'),
                'category': event['Category'],
                'impact_magnitude': event['Impact_Magnitude'],
                'description': event.get('Description', ''),
                'duration_days': event.get('Duration_Days', 30),
                'price_before': round(price_before, 2),
                'price_after': round(price_after, 2),
                'price_change_pct': round(price_change, 1),
                'volatility': round(volatility, 2),
                'severity': impact_order.get(event['Impact_Magnitude'], 1)
            })
        
        # Sort by date
        events_list.sort(key=lambda x: x['date'], reverse=True)
        
        return api_response(True, {
            'data': events_list,
            'count': len(events_list),
            'categories': df['Category'].unique().tolist(),
            'impact_levels': list(impact_order.keys())
        }, f"Retrieved {len(events_list)} events")
        
    except Exception as e:
        logger.error(f"Error in get_events: {e}")
        return api_response(False, None, "Failed to retrieve events", str(e), 500)

# Change points endpoint
@app.route('/api/change-points', methods=['GET'])
@cache.cached(timeout=600)
def get_change_points():
    """Get statistical change points"""
    try:
        if data_manager.change_points is None or data_manager.change_points.empty:
            # Generate from significant price movements
            price_data = data_manager.price_data.copy()
            price_data['Price_Change'] = price_data['Price'].pct_change().abs()
            
            # Find significant changes (>15%)
            significant_changes = price_data[price_data['Price_Change'] > 0.15]
            
            change_points = []
            for _, row in significant_changes.iterrows():
                change_points.append({
                    'date': row['Date'].strftime('%Y-%m-%d'),
                    'price': float(row['Price']),
                    'price_change_pct': float(row['Price_Change'] * 100),
                    'type': 'price_shock',
                    'confidence': 'high' if row['Price_Change'] > 0.25 else 'medium'
                })
        else:
            change_points = []
            for _, cp in data_manager.change_points.iterrows():
                change_points.append({
                    'date': cp['date'].strftime('%Y-%m-%d'),
                    'type': cp.get('type', 'detected'),
                    'confidence': cp.get('confidence', 'medium')
                })
        
        return api_response(True, {
            'data': change_points,
            'count': len(change_points),
            'analysis': {
                'total_points': len(change_points),
                'avg_interval_days': 'N/A',
                'most_common_year': max(set([cp['date'][:4] for cp in change_points])) if change_points else 'N/A'
            }
        }, f"Retrieved {len(change_points)} change points")
        
    except Exception as e:
        logger.error(f"Error in get_change_points: {e}")
        return api_response(False, None, "Failed to retrieve change points", str(e), 500)

# Comprehensive metrics endpoint
@app.route('/api/metrics', methods=['GET'])
@cache.cached(timeout=300)
def get_comprehensive_metrics():
    """Get comprehensive dashboard metrics"""
    try:
        price_df = data_manager.price_data
        
        # Basic metrics
        basic_metrics = {
            'data_range': {
                'start': price_df['Date'].min().strftime('%Y-%m-%d'),
                'end': price_df['Date'].max().strftime('%Y-%m-%d'),
                'total_days': len(price_df),
                'total_years': round(len(price_df) / 365, 1)
            },
            'price_statistics': {
                'current': float(price_df['Price'].iloc[-1]),
                'average': float(price_df['Price'].mean()),
                'median': float(price_df['Price'].median()),
                'max': float(price_df['Price'].max()),
                'min': float(price_df['Price'].min()),
                'std': float(price_df['Price'].std()),
                'range': float(price_df['Price'].max() - price_df['Price'].min())
            },
            'returns_statistics': {
                'avg_daily_return': float(price_df['Returns'].mean()),
                'avg_daily_volatility': float(price_df['Returns'].std()),
                'sharpe_ratio': float(price_df['Returns'].mean() / price_df['Returns'].std() * np.sqrt(252)) if price_df['Returns'].std() > 0 else 0,
                'positive_days': int((price_df['Returns'] > 0).sum()),
                'negative_days': int((price_df['Returns'] < 0).sum()),
                'max_gain': float(price_df['Returns'].max()),
                'max_loss': float(price_df['Returns'].min())
            }
        }
        
        # Event metrics
        event_metrics = {
            'total_events': len(data_manager.events_data),
            'events_by_category': data_manager.events_data['Category'].value_counts().to_dict(),
            'events_by_impact': data_manager.events_data['Impact_Magnitude'].value_counts().to_dict(),
            'avg_event_impact': 'N/A',
            'most_impactful_year': 'N/A'
        }
        
        # Market regime metrics
        price_df['Regime'] = 'Neutral'
        price_df.loc[price_df['Returns'] > price_df['Returns'].quantile(0.75), 'Regime'] = 'Bullish'
        price_df.loc[price_df['Returns'] < price_df['Returns'].quantile(0.25), 'Regime'] = 'Bearish'
        
        regime_metrics = price_df['Regime'].value_counts().to_dict()
        
        # Correlation analysis
        correlations = {
            'price_volatility_corr': float(price_df['Price'].corr(price_df['Volatility_30d'])),
            'price_volume_corr': 'N/A'  # Would need volume data
        }
        
        return api_response(True, {
            'basic': basic_metrics,
            'events': event_metrics,
            'regimes': regime_metrics,
            'correlations': correlations,
            'last_updated': datetime.now().isoformat()
        }, "Comprehensive metrics retrieved")
        
    except Exception as e:
        logger.error(f"Error in get_comprehensive_metrics: {e}")
        return api_response(False, None, "Failed to retrieve metrics", str(e), 500)

# Time series analysis endpoint
@app.route('/api/analysis/seasonality', methods=['GET'])
@cache.cached(timeout=3600)
def get_seasonality():
    """Analyze seasonal patterns"""
    try:
        df = data_manager.price_data.copy()
        df['Month'] = df['Date'].dt.month
        df['Year'] = df['Date'].dt.year
        
        # Monthly averages
        monthly_avg = df.groupby('Month').agg({
            'Price': 'mean',
            'Returns': 'mean',
            'Volatility_30d': 'mean'
        }).reset_index()
        
        # Yearly performance
        yearly_perf = df.groupby('Year').agg({
            'Price': ['first', 'last', 'max', 'min']
        }).reset_index()
        
        yearly_perf.columns = ['Year', 'Price_Start', 'Price_End', 'Price_Max', 'Price_Min']
        yearly_perf['Yearly_Return'] = ((yearly_perf['Price_End'] - yearly_perf['Price_Start']) / yearly_perf['Price_Start'] * 100)
        
        return api_response(True, {
            'monthly_averages': monthly_avg.to_dict('records'),
            'yearly_performance': yearly_perf.to_dict('records'),
            'seasonal_patterns': {
                'best_month': int(monthly_avg.loc[monthly_avg['Price'].idxmax(), 'Month']),
                'worst_month': int(monthly_avg.loc[monthly_avg['Price'].idxmin(), 'Month']),
                'avg_yearly_return': float(yearly_perf['Yearly_Return'].mean())
            }
        }, "Seasonality analysis completed")
        
    except Exception as e:
        logger.error(f"Error in get_seasonality: {e}")
        return api_response(False, None, "Failed to analyze seasonality", str(e), 500)

# Event impact analysis endpoint
@app.route('/api/analysis/event-impact/<event_name>', methods=['GET'])
def get_event_impact(event_name):
    """Analyze specific event impact"""
    try:
        # Find event
        event = data_manager.events_data[
            data_manager.events_data['Event_Name'].str.contains(event_name, case=False, na=False)
        ]
        
        if event.empty:
            return api_response(False, None, "Event not found", "", 404)
        
        event = event.iloc[0]
        event_date = event['Start_Date']
        
        # Get price data around event
        window_days = 60
        price_data = data_manager.price_data.copy()
        
        pre_event = price_data[
            (price_data['Date'] >= event_date - pd.Timedelta(days=window_days)) &
            (price_data['Date'] < event_date)
        ]
        
        post_event = price_data[
            (price_data['Date'] > event_date) &
            (price_data['Date'] <= event_date + pd.Timedelta(days=window_days))
        ]
        
        # Calculate impacts
        pre_avg = pre_event['Price'].mean() if len(pre_event) > 0 else 0
        post_avg = post_event['Price'].mean() if len(post_event) > 0 else 0
        price_change = ((post_avg - pre_avg) / pre_avg * 100) if pre_avg > 0 else 0
        
        pre_vol = pre_event['Volatility_30d'].mean() if len(pre_event) > 0 else 0
        post_vol = post_event['Volatility_30d'].mean() if len(post_event) > 0 else 0
        vol_change = post_vol - pre_vol
        
        # Event timeline data
        timeline_data = []
        combined = pd.concat([pre_event, post_event])
        
        for _, row in combined.iterrows():
            timeline_data.append({
                'date': row['Date'].strftime('%Y-%m-%d'),
                'price': float(row['Price']),
                'period': 'pre' if row['Date'] < event_date else 'post'
            })
        
        return api_response(True, {
            'event_info': {
                'name': event['Event_Name'],
                'date': event_date.strftime('%Y-%m-%d'),
                'category': event['Category'],
                'impact_magnitude': event['Impact_Magnitude'],
                'description': event.get('Description', '')
            },
            'impact_analysis': {
                'price_before': round(pre_avg, 2),
                'price_after': round(post_avg, 2),
                'price_change_pct': round(price_change, 1),
                'volatility_before': round(pre_vol, 4),
                'volatility_after': round(post_vol, 4),
                'volatility_change': round(vol_change, 4),
                'recovery_time_days': 'N/A',
                'max_drawdown': round(min(post_event['Price'].min() - pre_event['Price'].max(), 0), 2) if len(pre_event) > 0 and len(post_event) > 0 else 0
            },
            'timeline_data': timeline_data,
            'window_days': window_days
        }, f"Impact analysis for {event['Event_Name']}")
        
    except Exception as e:
        logger.error(f"Error in get_event_impact: {e}")
        return api_response(False, None, "Failed to analyze event impact", str(e), 500)

# Export data endpoint
@app.route('/api/export/<dataset>', methods=['GET'])
def export_data(dataset):
    """Export data in various formats"""
    try:
        format_type = request.args.get('format', 'json')
        
        if dataset == 'prices':
            df = data_manager.price_data
            filename = f'brent_prices_{datetime.now().strftime("%Y%m%d")}'
        elif dataset == 'events':
            df = data_manager.events_data
            filename = f'brent_events_{datetime.now().strftime("%Y%m%d")}'
        else:
            return api_response(False, None, "Invalid dataset", "", 400)
        
        if format_type == 'csv':
            csv_data = df.to_csv(index=False)
            return csv_data, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename={filename}.csv'
            }
        elif format_type == 'json':
            json_data = df.to_json(orient='records', date_format='iso')
            return json_data, 200, {
                'Content-Type': 'application/json',
                'Content-Disposition': f'attachment; filename={filename}.json'
            }
        else:
            return api_response(False, None, "Unsupported format", "", 400)
            
    except Exception as e:
        logger.error(f"Error in export_data: {e}")
        return api_response(False, None, "Failed to export data", str(e), 500)

# Dashboard configuration
@app.route('/api/config', methods=['GET'])
def get_config():
    """Get dashboard configuration"""
    config = {
        'dashboard': {
            'title': 'Brent Oil Price Intelligence Dashboard',
            'version': '1.0.0',
            'description': 'Interactive analysis of geopolitical & economic impacts on oil markets',
            'time_range': {
                'min': '1987-05-20',
                'max': '2022-11-14',
                'default_start': '2000-01-01',
                'default_end': '2022-12-31'
            }
        },
        'features': {
            'real_time_updates': False,
            'export_capabilities': True,
            'event_analysis': True,
            'change_point_detection': True,
            'seasonality_analysis': True
        },
        'charts': {
            'default_chart_type': 'line',
            'available_types': ['line', 'area', 'bar', 'scatter'],
            'color_schemes': ['blue', 'green', 'purple', 'orange'],
            'animation_enabled': True
        }
    }
    return api_response(True, config, "Dashboard configuration")

if __name__ == '__main__':
    # Print startup information
    print("=" * 60)
    print("🚀 Brent Oil Price Intelligence Dashboard API")
    print("=" * 60)
    
    if data_manager.price_data is not None:
        print(f"📊 Data Summary:")
        print(f"   • Price records: {len(data_manager.price_data):,}")
        print(f"   • Date range: {data_manager.price_data['Date'].min().date()} to {data_manager.price_data['Date'].max().date()}")
        print(f"   • Price range: ${data_manager.price_data['Price'].min():.2f} - ${data_manager.price_data['Price'].max():.2f}")
        print(f"   • Average price: ${data_manager.price_data['Price'].mean():.2f}")
        print(f"   • Events loaded: {len(data_manager.events_data)}")
    
    print(f"\n🌐 API Endpoints:")
    print(f"   • http://127.0.0.1:5000/api/health - Health check")
    print(f"   • http://127.0.0.1:5000/api/prices - Price data with filtering")
    print(f"   • http://127.0.0.1:5000/api/events - Events with impact analysis")
    print(f"   • http://127.0.0.1:5000/api/metrics - Comprehensive metrics")
    print(f"   • http://127.0.0.1:5000/api/change-points - Statistical change points")
    print(f"   • http://127.0.0.1:5000/api/analysis/seasonality - Seasonality analysis")
    print(f"   • http://127.0.0.1:5000/api/config - Dashboard configuration")
    print(f"   • http://127.0.0.1:5000/api/export/<dataset> - Data export")
    print("=" * 60)
    
    # Run Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )