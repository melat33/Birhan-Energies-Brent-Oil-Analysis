"""
Fast Bayesian Change Point Detection
Optimized for speed while maintaining accuracy
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from typing import Dict, List, Any, Optional
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class FastBayesianCPD:
    """Optimized Bayesian Change Point Detection"""
    
    def __init__(self, price_df: pd.DataFrame):
        self.price_df = price_df.copy()
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare optimized data"""
        self.prices = self.price_df['Price'].values.astype(np.float32)
        self.dates = self.price_df['Date'].values
        self.log_prices = np.log(self.prices)
        self.returns = np.diff(self.log_prices)
        self.n = len(self.returns)
        
        # Data statistics for informed priors
        self.data_mean = np.mean(self.returns)
        self.data_std = np.std(self.returns)
    
    def build_lightweight_model(self, n_changepoints: int = 1):
        """Build optimized PyMC model"""
        
        if n_changepoints == 1:
            return self._build_single_cp_model()
        else:
            return self._build_multiple_cp_model(n_changepoints)
    
    def _build_single_cp_model(self):
        """Single change point model (fastest)"""
        
        with pm.Model() as model:
            # Informed priors for faster convergence
            tau = pm.DiscreteUniform('tau', 
                                   lower=int(self.n * 0.1), 
                                   upper=int(self.n * 0.9))
            
            mu1 = pm.Normal('mu1', mu=self.data_mean, sigma=self.data_std * 2)
            mu2 = pm.Normal('mu2', mu=self.data_mean, sigma=self.data_std * 2)
            
            # Use HalfStudentT for robustness
            sigma = pm.HalfStudentT('sigma', nu=3, sigma=self.data_std)
            
            # Vectorized mean function
            idx = np.arange(self.n)
            mean = pm.math.switch(idx < tau, mu1, mu2)
            
            # Likelihood with float32
            pm.StudentT('returns', 
                       nu=4,
                       mu=mean, 
                       sigma=sigma, 
                       observed=self.returns.astype(np.float32))
        
        return model
    
    def _build_multiple_cp_model(self, n_cp: int):
        """Multiple change points model"""
        
        with pm.Model() as model:
            # Dirichlet prior for change points
            alpha = np.ones(n_cp + 1)
            p = pm.Dirichlet('p', a=alpha)
            
            # Cumulative probabilities
            cp_probs = np.cumsum(p)[:-1] * self.n
            tau = pm.Deterministic('tau', cp_probs.astype(int))
            
            # Segment means
            mu = pm.Normal('mu', mu=self.data_mean, sigma=self.data_std, 
                          shape=n_cp + 1)
            
            # Segment volatilities
            sigma = pm.HalfStudentT('sigma', nu=3, sigma=self.data_std, 
                                  shape=n_cp + 1)
            
            # Assign observations to segments
            segment_idx = np.searchsorted(tau, np.arange(self.n))
            
            # Vectorized likelihood
            mu_vec = mu[segment_idx]
            sigma_vec = sigma[segment_idx]
            
            pm.StudentT('returns', nu=4, mu=mu_vec, sigma=sigma_vec, 
                       observed=self.returns.astype(np.float32))
        
        return model
    
    def run_optimized_sampling(self, model, 
                              draws: int = 500, 
                              chains: int = 2,
                              target_accept: float = 0.8):
        """Run optimized MCMC sampling"""
        
        print(f"🔄 Sampling: {draws} draws × {chains} chains...")
        
        with model:
            trace = pm.sample(
                draws=draws,
                tune=int(draws * 0.5),  # Less tuning for speed
                chains=chains,
                cores=min(chains, 4),  # Limit cores
                target_accept=target_accept,
                progressbar=True,
                random_seed=42,
                return_inferencedata=True
            )
        
        return trace
    
    def analyze_results(self, trace, threshold: float = 0.05):
        """Analyze and extract change points"""
        
        if 'tau' in trace.posterior:
            tau_samples = trace.posterior['tau'].values.flatten()
        else:
            raise ValueError("No 'tau' parameter found in trace")
        
        # Find significant change points
        unique, counts = np.unique(tau_samples, return_counts=True)
        probabilities = counts / len(tau_samples)
        
        results = []
        for idx, (tau, prob) in enumerate(zip(unique, probabilities)):
            if prob > threshold:
                # Get date
                date_idx = int(tau)
                if date_idx < len(self.dates):
                    date = pd.to_datetime(self.dates[date_idx])
                else:
                    date = pd.to_datetime(self.dates[-1])
                
                # Calculate statistics
                segment_mask = np.arange(self.n) < tau
                
                if np.any(segment_mask) and np.any(~segment_mask):
                    mean_before = np.exp(np.mean(self.returns[segment_mask])) - 1
                    mean_after = np.exp(np.mean(self.returns[~segment_mask])) - 1
                    
                    results.append({
                        'index': int(tau),
                        'date': date,
                        'probability': float(prob),
                        'mean_before': float(mean_before),
                        'mean_after': float(mean_after),
                        'pct_change': float((mean_after / mean_before - 1) * 100),
                        'volatility_before': float(np.std(self.returns[segment_mask])),
                        'volatility_after': float(np.std(self.returns[~segment_mask]))
                    })
        
        return sorted(results, key=lambda x: x['probability'], reverse=True)
    
    def plot_results(self, results, top_n: int = 5):
        """Plot results quickly"""
        
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: Price with change points
        ax1 = axes[0, 0]
        ax1.plot(self.dates, self.prices, 'b-', alpha=0.7, linewidth=1)
        
        for i, cp in enumerate(results[:top_n]):
            ax1.axvline(x=cp['date'], color='red' if i == 0 else 'orange', 
                       linestyle='--', alpha=0.7)
            ax1.text(cp['date'], self.prices.max() * 0.95, 
                    f"{cp['date'].strftime('%Y-%m')}\nΔ={cp['pct_change']:.1f}%",
                    rotation=90, fontsize=8, ha='right')
        
        ax1.set_title('Price with Change Points', fontsize=12)
        ax1.set_ylabel('Price ($)')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Returns distribution
        ax2 = axes[0, 1]
        ax2.hist(self.returns * 100, bins=50, alpha=0.7, edgecolor='black')
        ax2.set_title('Returns Distribution', fontsize=12)
        ax2.set_xlabel('Daily Return (%)')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Rolling volatility
        ax3 = axes[1, 0]
        window = 30
        rolling_vol = pd.Series(self.returns).rolling(window).std() * np.sqrt(252) * 100
        
        ax3.plot(self.dates[window:], rolling_vol[window:], 'g-', alpha=0.7)
        for cp in results[:top_n]:
            if cp['index'] > window:
                ax3.axvline(x=cp['date'], color='red', linestyle='--', alpha=0.5)
        
        ax3.set_title(f'{window}-Day Rolling Volatility', fontsize=12)
        ax3.set_ylabel('Annualized Vol (%)')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Probability distribution of change points
        ax4 = axes[1, 1]
        indices = [cp['index'] for cp in results[:top_n]]
        probs = [cp['probability'] for cp in results[:top_n]]
        
        bars = ax4.bar(range(len(indices)), probs, color=['red'] + ['orange'] * (len(indices)-1))
        ax4.set_xticks(range(len(indices)))
        ax4.set_xticklabels([f"τ={i}" for i in indices], rotation=45)
        ax4.set_title('Change Point Probabilities', fontsize=12)
        ax4.set_ylabel('Probability')
        
        # Add probability labels
        for bar, prob in zip(bars, probs):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{prob:.1%}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def generate_report(self, results):
        """Generate summary report"""
        
        print("\n" + "="*60)
        print("📊 BAYESIAN CHANGE POINT ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📈 Data Summary:")
        print(f"   • Total observations: {len(self.prices):,}")
        print(f"   • Date range: {pd.to_datetime(self.dates[0]).date()} to "
              f"{pd.to_datetime(self.dates[-1]).date()}")
        print(f"   • Mean return: {self.data_mean * 100:.3f}%")
        print(f"   • Volatility: {self.data_std * 100:.2f}%")
        
        print(f"\n🎯 Detected Change Points (p > 0.05): {len(results)}")
        print("-" * 80)
        
        if results:
            headers = ["Date", "Index", "Prob", "μ_before", "μ_after", "Δ%", "Vol_bef", "Vol_aft"]
            print(f"{headers[0]:<12} {headers[1]:<8} {headers[2]:<6} {headers[3]:<10} "
                  f"{headers[4]:<10} {headers[5]:<8} {headers[6]:<10} {headers[7]:<10}")
            print("-" * 80)
            
            for cp in results[:10]:  # Show top 10
                date_str = cp['date'].strftime('%Y-%m-%d')
                print(f"{date_str:<12} "
                      f"{cp['index']:<8} "
                      f"{cp['probability']:<6.1%} "
                      f"{cp['mean_before']*100:<10.2f}% "
                      f"{cp['mean_after']*100:<10.2f}% "
                      f"{cp['pct_change']:<8.1f}% "
                      f"{cp['volatility_before']*100:<10.2f}% "
                      f"{cp['volatility_after']*100:<10.2f}%")
        
        print("-" * 80)
        
        return results


# Convenience function for quick analysis
def analyze_brent_oil(price_df, n_changepoints=1, fast_mode=True):
    """Quick analysis wrapper"""
    
    analyzer = FastBayesianCPD(price_df)
    
    if fast_mode:
        # Ultra-fast single change point
        model = analyzer.build_lightweight_model(n_changepoints=1)
        trace = analyzer.run_optimized_sampling(model, draws=300, chains=2)
    else:
        # More thorough analysis
        model = analyzer.build_lightweight_model(n_changepoints=n_changepoints)
        trace = analyzer.run_optimized_sampling(model, draws=1000, chains=4)
    
    results = analyzer.analyze_results(trace, threshold=0.05)
    analyzer.generate_report(results)
    analyzer.plot_results(results)
    
    return analyzer, trace, results