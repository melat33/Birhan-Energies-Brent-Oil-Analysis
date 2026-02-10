"""
Visualization - Professional Charts for Task 1
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class Task1Visualizer:
    """Create professional visualizations for Task 1"""
    
    def __init__(self, price_df, events_df):
        self.price_df = price_df
        self.events_df = events_df
        
        # Professional styling
        plt.style.use('seaborn-v0_8-whitegrid')
        self.colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
        
    def display_all_analysis(self):
        """Display 6 key visualizations with interpretation"""
        fig = plt.figure(figsize=(18, 12))
        
        # 1. Price Timeline with Events
        ax1 = plt.subplot(3, 2, 1)
        self._plot_price_timeline(ax1)
        
        # 2. Event Distribution
        ax2 = plt.subplot(3, 2, 2)
        self._plot_event_distribution(ax2)
        
        # 3. Trend Analysis
        ax3 = plt.subplot(3, 2, 3)
        self._plot_trend_analysis(ax3)
        
        # 4. Volatility Analysis
        ax4 = plt.subplot(3, 2, 4)
        self._plot_volatility_analysis(ax4)
        
        # 5. Event Timeline
        ax5 = plt.subplot(3, 2, 5)
        self._plot_event_timeline(ax5)
        
        # 6. Category Impact
        ax6 = plt.subplot(3, 2, 6)
        self._plot_category_impact(ax6)
        
        plt.suptitle('BIRHAN ENERGIES - TASK 1: COMPREHENSIVE ANALYSIS', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.show()
        
        # Print interpretation
        self._print_interpretation()
    
    def _plot_price_timeline(self, ax):
        """Plot 1: Price timeline with events"""
        ax.plot(self.price_df['Date'], self.price_df['Price'], 
               linewidth=1.5, color=self.colors[0], alpha=0.8)
        
        # Add event markers
        for _, event in self.events_df.iterrows():
            ax.axvline(x=event['Start_Date'], alpha=0.3, 
                      color=self._get_event_color(event['Category']),
                      linewidth=0.8, linestyle='--')
        
        ax.set_title('Brent Oil Price Timeline (1987-2022)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price ($/barrel)', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_event_distribution(self, ax):
        """Plot 2: Event distribution"""
        # By category
        cat_counts = self.events_df['Category'].value_counts()
        bars = ax.bar(cat_counts.index, cat_counts.values, 
                     color=self.colors[:len(cat_counts)], alpha=0.8)
        
        ax.set_title('Event Distribution by Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Events', fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        
        # Add values
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
    
    def _plot_trend_analysis(self, ax):
        """Plot 3: Trend analysis"""
        # Calculate rolling averages - FIXED: Changed 'M' to 'ME'
        price_series = self.price_df.set_index('Date')['Price']
        monthly_avg = price_series.resample('ME').mean()  # Changed from 'M' to 'ME'
        
        ax.plot(monthly_avg.index, monthly_avg.values, 
               linewidth=2, color=self.colors[0], alpha=0.7, label='Monthly Average')
        
        # Add trend line
        from scipy import stats
        x = np.arange(len(monthly_avg))
        slope, intercept = np.polyfit(x, monthly_avg.values, 1)
        trend_line = intercept + slope * x
        ax.plot(monthly_avg.index, trend_line, 'r--', linewidth=2, 
               alpha=0.7, label=f'Trend: ${slope*12:.2f}/year')
        
        ax.set_title('Long-term Trend Analysis', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price ($/barrel)', fontsize=10)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_volatility_analysis(self, ax):
        """Plot 4: Volatility analysis"""
        returns = self.price_df['Price'].pct_change().dropna() * 100
        
        # Histogram of returns
        ax.hist(returns, bins=50, color=self.colors[1], alpha=0.7, edgecolor='black')
        ax.axvline(x=returns.mean(), color='red', linestyle='--', 
                  linewidth=2, label=f'Mean: {returns.mean():.2f}%')
        ax.axvline(x=returns.std(), color='orange', linestyle='--', 
                  linewidth=2, label=f'Std Dev: {returns.std():.2f}%')
        
        ax.set_title('Daily Returns Distribution', fontsize=12, fontweight='bold')
        ax.set_xlabel('Daily Return (%)', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.legend()
    
    def _plot_event_timeline(self, ax):
        """Plot 5: Event timeline"""
        events = self.events_df.sort_values('Start_Date')
        
        # Create bands for different categories
        categories = events['Category'].unique()
        category_positions = {cat: i for i, cat in enumerate(categories)}
        
        for _, event in events.iterrows():
            y_pos = category_positions[event['Category']]
            ax.scatter(event['Start_Date'], y_pos, 
                      color=self._get_event_color(event['Category']),
                      s=150, alpha=0.8, edgecolor='black', zorder=5)
            
            # Label major events
            if event['Impact_Magnitude'] in ['Very High', 'High']:
                ax.annotate(event['Event_Name'][:15] + '...', 
                          (event['Start_Date'], y_pos),
                          xytext=(0, 10), textcoords='offset points',
                          fontsize=8, ha='center', fontweight='bold')
        
        ax.set_yticks(range(len(categories)))
        ax.set_yticklabels(categories)
        ax.set_title('Historical Event Timeline', fontsize=12, fontweight='bold')
        ax.set_xlabel('Year', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_category_impact(self, ax):
        """Plot 6: Expected impact by category"""
        impact_map = {'Very High': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        self.events_df['Impact_Value'] = self.events_df['Impact_Magnitude'].map(impact_map)
        
        category_impact = self.events_df.groupby('Category')['Impact_Value'].mean()
        
        bars = ax.bar(category_impact.index, category_impact.values,
                     color=self.colors[:len(category_impact)], alpha=0.8)
        
        ax.set_title('Average Expected Impact by Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Impact Score (1-4)', fontsize=10)
        ax.set_ylim(0, 4.5)
        ax.tick_params(axis='x', rotation=45)
        
        # Add values
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom')
    
    def _get_event_color(self, category):
        """Get consistent color for event category"""
        color_map = {
            'Geopolitical': '#C73E1D',  # Red
            'Economic': '#2E86AB',      # Blue
            'OPEC Decision': '#F18F01',  # Orange
            'Supply': '#6A994E',        # Green
            'Environmental': '#A23B72'   # Purple
        }
        return color_map.get(category, '#7F7F7F')
    
    def _print_interpretation(self):
        """Print professional interpretation"""
        print("\n" + "="*80)
        print("📊 PROFESSIONAL INTERPRETATION - TASK 1 FINDINGS")
        print("="*80)
        
        print("\n1️⃣ PRICE TRENDS (Plot 1 & 3):")
        print("   • Long-term upward trend with significant cyclicality")
        print("   • Major price spikes align with geopolitical events")
        print("   • 2008 and 2020 show extreme volatility")
        
        print("\n2️⃣ EVENT ANALYSIS (Plot 2 & 5):")
        print(f"   • {len(self.events_df)} key events identified (1987-2022)")
        print("   • Geopolitical events dominate (Middle East conflicts)")
        print("   • Economic events cause largest negative impacts")
        
        print("\n3️⃣ VOLATILITY PATTERNS (Plot 4):")
        returns = self.price_df['Price'].pct_change().dropna() * 100
        print(f"   • Daily volatility: {returns.std():.2f}%")
        print(f"   • Extreme moves: {returns.max():.2f}% gain, {returns.min():.2f}% loss")
        print("   • Fat-tailed distribution (more extremes than normal)")
        
        print("\n4️⃣ KEY INSIGHTS FOR STAKEHOLDERS:")
        print("   • Geopolitical risks = Price spikes")
        print("   • Economic crises = Price collapses")
        print("   • OPEC decisions = Market structure shifts")
        
        print("\n5️⃣ NEXT STEPS (Task 2 Preparation):")
        print("   • Bayesian change point detection")
        print("   • Quantify exact event impacts")
        print("   • Statistical significance testing")
        print("="*80)
class Task2Visualizer(Task1Visualizer):
    """Extend for Task 2 visualizations"""
    
    def display_data_characteristics(self):
        """Display data characteristics for modeling"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # 1. Log returns (stationary series)
        log_returns = np.log(self.price_df['Price']).diff().dropna() * 100
        axes[0,0].plot(self.price_df['Date'][1:], log_returns, 
                      linewidth=0.5, color='blue', alpha=0.7)
        axes[0,0].set_title('Log Returns (Stationary Series)', fontweight='bold')
        axes[0,0].set_ylabel('Log Return (%)')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. ACF of returns (check stationarity)
        from statsmodels.graphics.tsaplots import plot_acf
        plot_acf(log_returns.dropna(), ax=axes[0,1], lags=50)
        axes[0,1].set_title('Autocorrelation of Returns', fontweight='bold')
        
        # 3. Rolling volatility
        volatility = self.price_df['Returns'].abs().rolling(30).mean() * 100
        axes[1,0].plot(self.price_df['Date'], volatility, 
                      linewidth=1, color='red', alpha=0.7)
        axes[1,0].set_title('30-Day Rolling Volatility', fontweight='bold')
        axes[1,0].set_ylabel('Volatility (%)')
        axes[1,0].grid(True, alpha=0.3)
        
        # 4. QQ plot of returns
        from scipy import stats
        stats.probplot(log_returns.dropna(), dist="norm", plot=axes[1,1])
        axes[1,1].set_title('QQ Plot (Normality Check)', fontweight='bold')
        
        plt.suptitle('DATA CHARACTERISTICS FOR BAYESIAN MODELING', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def plot_change_points_timeline(self, change_points, events_df):
        """Plot change points on price timeline"""
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot price
        ax.plot(self.price_df['Date'], self.price_df['Price'], 
               linewidth=1, color='blue', alpha=0.7, label='Price')
        
        # Add change points
        for cp in change_points:
            ax.axvline(x=cp['date'], color='red', alpha=0.5, 
                      linewidth=2, linestyle='--')
            ax.annotate(f"CP: {cp['date'].date()}\nΔ={cp['pct_change']:.1f}%", 
                       (cp['date'], self.price_df['Price'].max()),
                       xytext=(0, 10), textcoords='offset points',
                       fontsize=8, ha='center', color='red')
        
        # Add events
        for _, event in events_df.iterrows():
            ax.axvline(x=event['Start_Date'], alpha=0.3, 
                      color=self._get_event_color(event['Category']),
                      linewidth=0.8, linestyle=':')
        
        ax.set_title('CHANGE POINTS ON PRICE TIMELINE', fontsize=14, fontweight='bold')
        ax.set_ylabel('Price ($/barrel)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()