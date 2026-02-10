# src/time_series_analyzer.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.tsa.stattools import adfuller

class TimeSeriesAnalyzer:
    """Comprehensive time series analysis for Brent oil prices"""
    
    def __init__(self, price_df):
        self.price_df = price_df.copy()
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare data for analysis"""
        self.price_df['Returns'] = self.price_df['Price'].pct_change()
        self.price_df['Log_Returns'] = np.log(self.price_df['Price']).diff()
        
    def display_complete_analysis(self):
        """Display all analysis in one view"""
        print("📈 TIME SERIES PROPERTIES ANALYSIS")
        print("="*60)
        
        self._create_visualizations()
        self._calculate_statistics()
        
    def _create_visualizations(self):
        """Create comprehensive visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # 1. Price timeline
        axes[0,0].plot(self.price_df['Date'], self.price_df['Price'], 
                      linewidth=0.5, color='blue', alpha=0.7)
        axes[0,0].set_title('Brent Oil Price (1987-2022)', fontweight='bold')
        axes[0,0].set_ylabel('Price ($/barrel)')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. Trend analysis
        window = 252
        rolling_mean = self.price_df['Price'].rolling(window=window).mean()
        rolling_std = self.price_df['Price'].rolling(window=window).std()
        
        axes[0,1].plot(self.price_df['Date'], self.price_df['Price'], 
                      linewidth=0.5, color='blue', alpha=0.3, label='Price')
        axes[0,1].plot(self.price_df['Date'], rolling_mean, linewidth=2, 
                      color='red', label=f'{window}-day MA')
        axes[0,1].fill_between(self.price_df['Date'], 
                              rolling_mean-rolling_std, 
                              rolling_mean+rolling_std, 
                              alpha=0.2, color='red')
        axes[0,1].set_title('Trend Analysis', fontweight='bold')
        axes[0,1].set_ylabel('Price ($/barrel)')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. Returns distribution
        returns = self.price_df['Returns'].dropna() * 100
        axes[1,0].hist(returns, bins=100, color='skyblue', 
                      edgecolor='black', alpha=0.7)
        axes[1,0].axvline(returns.mean(), color='red', linestyle='--', 
                         label=f'Mean: {returns.mean():.2f}%')
        axes[1,0].set_title('Daily Returns Distribution', fontweight='bold')
        axes[1,0].set_xlabel('Daily Return (%)')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].legend()
        
        # 4. Volatility clustering
        volatility = self.price_df['Returns'].abs().rolling(window=30).mean() * 100
        axes[1,1].plot(self.price_df['Date'], volatility, 
                      linewidth=1, color='green', alpha=0.7)
        axes[1,1].set_title('Volatility Clustering', fontweight='bold')
        axes[1,1].set_ylabel('30-day Avg Volatility (%)')
        axes[1,1].grid(True, alpha=0.3)
        
        plt.suptitle('BIRHAN ENERGIES: Time Series Properties', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
    def _calculate_statistics(self):
        """Calculate key statistics"""
        returns = self.price_df['Returns'].dropna() * 100
        
        # Trend
        x = np.arange(len(self.price_df))
        slope, _, r_value, _, _ = stats.linregress(x, self.price_df['Price'])
        
        # Stationarity tests
        adf_price = adfuller(self.price_df['Price'].dropna())
        adf_returns = adfuller(self.price_df['Returns'].dropna())
        
        # Volatility metrics
        acf_vol = self.price_df['Returns'].abs().autocorr(lag=1)
        
        print("\n📊 STATISTICAL ANALYSIS:")
        print("-" * 40)
        print(f"📈 Trend: ${slope*365:.2f}/year (R²={r_value**2:.3f})")
        print(f"📅 Price Stationarity: p={adf_price[1]:.6f} ({'Non-stationary' if adf_price[1] > 0.05 else 'Stationary'})")
        print(f"📅 Returns Stationarity: p={adf_returns[1]:.6f} ({'Non-stationary' if adf_returns[1] > 0.05 else 'Stationary'})")
        print(f"⚡ Volatility: {returns.std():.2f}% daily, {returns.std()*np.sqrt(252):.1f}% annual")
        print(f"📊 Max Move: {returns.abs().max():.1f}%, Clustering: {'Yes' if abs(acf_vol) > 0.1 else 'No'}")
        print("-" * 40)
        
    def get_summary(self):
        """Return comprehensive summary as dictionary"""
        returns = self.price_df['Returns'].dropna() * 100
        x = np.arange(len(self.price_df))
        slope, _, r_value, _, _ = stats.linregress(x, self.price_df['Price'])
        
        return {
            'trend_annual': slope * 365,
            'r_squared': r_value**2,
            'price_stationary': adfuller(self.price_df['Price'].dropna())[1] < 0.05,
            'returns_stationary': adfuller(self.price_df['Returns'].dropna())[1] < 0.05,
            'daily_volatility': returns.std(),
            'annual_volatility': returns.std() * np.sqrt(252),
            'mean_return': returns.mean(),
            'max_move': returns.abs().max()
        }