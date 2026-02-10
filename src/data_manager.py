"""
Data Manager - Professional Data Handling
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from datetime import datetime

class DataManager:
    """Load and analyze price data professionally"""
    
    def load_prices(self, filepath):
        """Load Brent oil prices"""
        df = pd.read_csv(filepath)
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y')
        return df
    
    def analyze_time_series(self, price_df):
        """Analyze time series properties"""
        prices = price_df['Price']
        
        # Trend analysis
        trend = self._calculate_trend(prices)
        
        # Stationarity test
        stationarity = self._test_stationarity(prices)
        
        # Volatility patterns
        volatility = self._analyze_volatility(prices)
        
        return {
            'mean': prices.mean(),
            'std': prices.std(),
            'trend': trend,
            'stationarity': stationarity,
            'volatility': volatility
        }
    
    def _calculate_trend(self, prices):
        """Calculate price trend"""
        from scipy import stats
        x = np.arange(len(prices))
        slope, _, _, _, _ = stats.linregress(x, prices)
        return slope * 365  # Annual trend
    
    def _test_stationarity(self, prices):
        """ADF test for stationarity"""
        result = adfuller(prices.dropna())
        return {'p_value': result[1], 'stationary': result[1] < 0.05}
    
    def _analyze_volatility(self, prices):
        """Analyze volatility patterns"""
        returns = prices.pct_change().dropna()
        return {
            'daily_vol': returns.std(),
            'annual_vol': returns.std() * np.sqrt(252),
            'vol_clusters': self._detect_vol_clusters(returns)
        }
    
    def _detect_vol_clusters(self, returns):
        """Detect volatility clustering"""
        from scipy import stats
        # Simple autocorrelation test
        acf = pd.Series(returns).autocorr(lag=1)
        return abs(acf) > 0.1  # Significant autocorrelation