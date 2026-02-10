import pymc as pm
import arviz as az
import numpy as np
import pandas as pd
from typing import Dict, List, Any

class BayesianChangePointModel:
    """Bayesian Change Point Detection Model"""
    
    def __init__(self, price_df):
        self.price_df = price_df
        self.model = None
        self.trace = None
        self.log_returns = np.log(price_df['Price']).diff().dropna().values
        
    def build_simple_mean_model(self):
        """Build simple mean shift model"""
        n = len(self.log_returns)
        
        with pm.Model() as model:
            # Prior for change point (uniform over all days)
            tau = pm.DiscreteUniform("tau", lower=1, upper=n-1)
            
            # Priors for means before and after change
            mu1 = pm.Normal("mu1", mu=0, sigma=1)
            mu2 = pm.Normal("mu2", mu=0, sigma=1)
            
            # Prior for standard deviation
            sigma = pm.HalfNormal("sigma", sigma=1)
            
            # Mean function using switch
            mean = pm.math.switch(tau > np.arange(n), mu1, mu2)
            
            # Likelihood
            likelihood = pm.Normal("returns", mu=mean, sigma=sigma, 
                                 observed=self.log_returns)
            
            self.model = model
    
    def run_sampling(self, n_samples=2000, n_chains=4):
        """Run MCMC sampling"""
        with self.model:
            self.trace = pm.sample(
                draws=n_samples,
                chains=n_chains,
                tune=1000,
                return_inferencedata=True,
                random_seed=42
            )
        
        return {
            'n_samples': n_samples,
            'n_chains': n_chains,
            'r_hat_stats': az.rhat(self.trace),
            'trace': self.trace
        }
    
    def identify_change_points(self, threshold=0.1):
        """Identify significant change points"""
        tau_samples = self.trace.posterior["tau"].values.flatten()
        
        # Find most probable change point
        unique, counts = np.unique(tau_samples, return_counts=True)
        probabilities = counts / len(tau_samples)
        
        change_points = []
        for tau, prob in zip(unique, probabilities):
            if prob > threshold:
                date = self.price_df['Date'].iloc[int(tau)]
                
                # Calculate means before and after
                mask = np.arange(len(self.log_returns)) < tau
                mean_before = np.exp(self.log_returns[mask].mean()) - 1
                mean_after = np.exp(self.log_returns[~mask].mean()) - 1
                
                change_points.append({
                    'tau': int(tau),
                    'date': date,
                    'probability': float(prob),
                    'mean_before': float(mean_before),
                    'mean_after': float(mean_after),
                    'mean_change': float(mean_after - mean_before),
                    'pct_change': float((mean_after/mean_before - 1) * 100)
                })
        
        return sorted(change_points, key=lambda x: x['probability'], reverse=True)
    
    def display_convergence_diagnostics(self):
        """Display convergence statistics"""
        summary = az.summary(self.trace, var_names=["tau", "mu1", "mu2", "sigma"])
        print("\n📊 CONVERGENCE DIAGNOSTICS:")
        print("-" * 40)
        print(summary)
        
        # Check R-hat values
        r_hat = summary['r_hat'].values
        print(f"\n✅ All R-hat values < 1.01: {np.all(r_hat < 1.01)}")
    
    def plot_traces(self):
        """Plot trace plots"""
        az.plot_trace(self.trace, var_names=["tau", "mu1", "mu2", "sigma"])