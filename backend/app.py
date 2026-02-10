from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Get project root directory (one level up from backend)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

def load_data():
    """Load all required datasets from the correct locations"""
    try:
        print("📊 Loading data from:", DATA_DIR)
        
        # Load price data from root data directory
        price_path = os.path.join(DATA_DIR, 'raw', 'BrentOilPrices.csv')
        print("Looking for price data at:", price_path)
        
        if os.path.exists(price_path):
            price_df = pd.read_csv(price_path)
            # Try different date formats
            try:
                price_df['Date'] = pd.to_datetime(price_df['Date'], format='%d-%b-%y')
            except:
                price_df['Date'] = pd.to_datetime(price_df['Date'])
            
            print(f"✅ Price data loaded: {len(price_df):,} records")
            print(f"📅 Date range: {price_df['Date'].min()} to {price_df['Date'].max()}")
            print(f"📈 Price columns: {price_df.columns.tolist()}")
        else:
            print(f"❌ Price file not found at: {price_path}")
            # Check what files exist
            print("Files in data/raw:", os.listdir(os.path.join(DATA_DIR, 'raw')))
            return None
        
        # Load events data
        events_path = os.path.join(DATA_DIR, 'raw', 'events_1987_2022.csv')
        print("Looking for events data at:", events_path)
        
        if os.path.exists(events_path):
            events_df = pd.read_csv(events_path)
            events_df['Start_Date'] = pd.to_datetime(events_df['Start_Date'])
            print(f"✅ Events data loaded: {len(events_df)} events")
        else:
            # Create sample events based on your Task 2
            print("⚠️ Creating sample events data...")
            events_data = [
                {'Event_Name': 'Gulf War', 'Start_Date': '1990-08-02', 'Category': 'Geopolitical', 'Impact_Magnitude': 'Very High'},
                {'Event_Name': '2008 Financial Crisis', 'Start_Date': '2008-09-15', 'Category': 'Economic', 'Impact_Magnitude': 'Very High'},
                {'Event_Name': 'OPEC Price War 2014', 'Start_Date': '2014-11-27', 'Category': 'OPEC Decision', 'Impact_Magnitude': 'High'},
                {'Event_Name': 'COVID-19 Pandemic', 'Start_Date': '2020-03-11', 'Category': 'Economic', 'Impact_Magnitude': 'Very High'},
                {'Event_Name': 'Russia-Ukraine War', 'Start_Date': '2022-02-24', 'Category': 'Geopolitical', 'Impact_Magnitude': 'Very High'}
            ]
            events_df = pd.DataFrame(events_data)
            events_df['Start_Date'] = pd.to_datetime(events_df['Start_Date'])
        
        # Calculate additional metrics
        price_df['Returns'] = price_df['Price'].pct_change()
        price_df['Volatility'] = price_df['Returns'].rolling(30).std() * np.sqrt(252) * 100
        price_df['Log_Returns'] = np.log(price_df['Price']).diff()
        
        # Load or create change points
        cp_path = os.path.join(DATA_DIR, 'processed', 'change_points.csv')
        if os.path.exists(cp_path):
            change_points_df = pd.read_csv(cp_path)
            if 'date' in change_points_df.columns:
                change_points_df['date'] = pd.to_datetime(change_points_df['date'])
        else:
            # Create from your Task 2 results
            print("⚠️ Creating change points from Task 2...")
            change_points_data = [
                {'date': '2008-10-16', 'type': 'detected'},
                {'date': '2014-11-27', 'type': 'detected'},
                {'date': '2020-03-11', 'type': 'detected'},
                {'date': '2022-02-24', 'type': 'detected'}
            ]
            change_points_df = pd.DataFrame(change_points_data)
            change_points_df['date'] = pd.to_datetime(change_points_df['date'])
        
        # Load or create impacts
        impacts_path = os.path.join(DATA_DIR, 'processed', 'event_impacts.csv')
        if os.path.exists(impacts_path):
            impacts_df = pd.read_csv(impacts_path)
        else:
            # Create from your Task 2 results
            print("⚠️ Creating impacts from Task 2...")
            impacts_data = [
                {'event': '2008 Financial Crisis', 'cp': '2008-10-16', 'impact': -32.1},
                {'event': 'OPEC Price War 2014', 'cp': '2014-11-27', 'impact': -43.5},
                {'event': 'COVID-19 Pandemic', 'cp': '2020-03-11', 'impact': -34.9},
                {'event': 'Russia-Ukraine War', 'cp': '2022-02-24', 'impact': 32.7}
            ]
            impacts_df = pd.DataFrame(impacts_data)
        
        return {
            'price_data': price_df,
            'events': events_df,
            'change_points': change_points_df,
            'impacts': impacts_df
        }
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return None

# Global data store
data_store = load_data()

# Basic API endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if data_store else 'error',
        'message': 'Flask API is running',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': data_store is not None
    })

@app.route('/api/historical-prices', methods=['GET'])
def get_historical_prices():
    """Get historical price data"""
    if not data_store:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    try:
        df = data_store['price_data'].copy()
        
        # Convert to list of dictionaries for JSON
        result = []
        for _, row in df.iterrows():
            result.append({
                'Date': row['Date'].strftime('%Y-%m-%d'),
                'Price': float(row['Price']),
                'Returns': float(row['Returns']) if not pd.isna(row['Returns']) else 0,
                'Volatility': float(row['Volatility']) if not pd.isna(row['Volatility']) else 0
            })
        
        return jsonify({
            'success': True,
            'data': result[:1000],  # Limit for performance
            'count': len(result),
            'date_range': {
                'start': df['Date'].min().strftime('%Y-%m-%d'),
                'end': df['Date'].max().strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    if not data_store:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    try:
        df = data_store['events']
        price_df = data_store['price_data']
        
        events_list = []
        for _, event in df.iterrows():
            event_date = event['Start_Date']
            
            # Find nearest price data
            time_diff = (price_df['Date'] - event_date).abs()
            if len(time_diff) > 0:
                nearest_idx = time_diff.idxmin()
                price_at_event = price_df.loc[nearest_idx, 'Price']
                vol_at_event = price_df.loc[nearest_idx, 'Volatility'] if not pd.isna(price_df.loc[nearest_idx, 'Volatility']) else 0
            else:
                price_at_event = 0
                vol_at_event = 0
            
            events_list.append({
                'id': str(_),
                'event_name': event['Event_Name'],
                'date': event_date.strftime('%Y-%m-%d'),
                'category': event['Category'],
                'impact_magnitude': event['Impact_Magnitude'],
                'description': event.get('Description', ''),
                'price_at_event': round(price_at_event, 2),
                'volatility_at_event': round(vol_at_event, 2)
            })
        
        return jsonify({
            'success': True,
            'data': events_list,
            'count': len(events_list)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/change-points', methods=['GET'])
def get_change_points():
    """Get change points"""
    if not data_store:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    try:
        df = data_store['change_points']
        
        change_points_list = []
        for _, cp in df.iterrows():
            change_points_list.append({
                'date': cp['date'].strftime('%Y-%m-%d'),
                'type': cp.get('type', 'detected')
            })
        
        return jsonify({
            'success': True,
            'data': change_points_list,
            'count': len(change_points_list)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/summary-metrics', methods=['GET'])
def get_summary_metrics():
    """Get summary metrics"""
    if not data_store:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    try:
        price_df = data_store['price_data']
        events_df = data_store['events']
        
        metrics = {
            'total_days': len(price_df),
            'date_range': {
                'start': price_df['Date'].min().strftime('%Y-%m-%d'),
                'end': price_df['Date'].max().strftime('%Y-%m-%d')
            },
            'price_stats': {
                'current': round(price_df['Price'].iloc[-1], 2),
                'average': round(price_df['Price'].mean(), 2),
                'max': round(price_df['Price'].max(), 2),
                'min': round(price_df['Price'].min(), 2)
            },
            'event_stats': {
                'total_events': len(events_df),
                'events_by_category': events_df['Category'].value_counts().to_dict()
            }
        }
        
        return jsonify({'success': True, 'metrics': metrics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Simple test endpoint
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to check data structure"""
    if data_store:
        price_df = data_store['price_data']
        events_df = data_store['events']
        
        return jsonify({
            'success': True,
            'price_sample': price_df[['Date', 'Price']].head().to_dict('records'),
            'events_sample': events_df.head().to_dict('records'),
            'price_columns': price_df.columns.tolist(),
            'events_columns': events_df.columns.tolist()
        })
    else:
        return jsonify({'success': False, 'error': 'No data loaded'})

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Brent Oil Price Dashboard API")
    print("=" * 50)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Data loaded successfully: {data_store is not None}")
    
    if data_store:
        price_df = data_store['price_data']
        print(f"\n📊 Data Summary:")
        print(f"   • Price records: {len(price_df):,}")
        print(f"   • Date range: {price_df['Date'].min().date()} to {price_df['Date'].max().date()}")
        print(f"   • Price range: ${price_df['Price'].min():.2f} - ${price_df['Price'].max():.2f}")
        print(f"   • Events: {len(data_store['events'])}")
        print(f"   • Change points: {len(data_store['change_points'])}")
    
    print("\n🚀 Starting Flask server on http://127.0.0.1:5000")
    print("   • /api/health - Health check")
    print("   • /api/historical-prices - Price data")
    print("   • /api/events - Events data")
    print("   • /api/change-points - Change points")
    print("   • /api/summary-metrics - Summary metrics")
    print("   • /api/test - Test endpoint")
    print("=" * 50)
    
    app.run(debug=True, port=5000)