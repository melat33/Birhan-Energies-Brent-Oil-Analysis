"""
Alternative fast change point methods
For when Bayesian is too slow
"""

import numpy as np
import pandas as pd
from typing import List, Dict
from scipy import stats
from ruptures import Binseg, Window

class FastChangePointMethods:
    """Non-Bayesian fast change point methods"""
    
    @staticmethod
    def cusum_method(prices, n_changepoints=5):
        """CUSUM algorithm - very fast"""
        from ruptures import Binseg
        
        algo = Binseg(model="rbf").fit(prices)
        return algo.predict(n_bkps=n_changepoints)
    
    @staticmethod
    def window_method(prices, width=30, n_changepoints=5):
        """Sliding window method"""
        from ruptures import Window
        
        algo = Window(width=width).fit(prices)
        return algo.predict(n_bkps=n_changepoints)
    
    @staticmethod
    def pruned_exact_method(prices, n_changepoints=5):
        """Pruned Exact Linear Time (PELT)"""
        from ruptures import Pelt
        
        algo = Pelt(model="rbf").fit(prices)
        return algo.predict(pen=10)
    
    @staticmethod
    def binary_segmentation(prices, n_changepoints=5):
        """Binary segmentation"""
        from ruptures import Binseg
        
        algo = Binseg(model="l2").fit(prices)
        return algo.predict(n_bkps=n_changepoints)


def quick_change_point_analysis(price_df, method='binary', n_points=5):
    """Ultra-fast change point analysis"""
    
    prices = price_df['Price'].values
    dates = price_df['Date'].values
    
    methods = FastChangePointMethods()
    
    if method == 'binary':
        cp_indices = methods.binary_segmentation(prices, n_changepoints=n_points)
    elif method == 'cusum':
        cp_indices = methods.cusum_method(prices, n_changepoints=n_points)
    elif method == 'window':
        cp_indices = methods.window_method(prices, n_changepoints=n_points)
    else:
        cp_indices = methods.pruned_exact_method(prices)
    
    # Convert to dates
    results = []
    cp_indices = cp_indices[:-1]  # Remove last index
    
    for idx in cp_indices:
        if idx < len(dates):
            results.append({
                'index': idx,
                'date': pd.to_datetime(dates[idx]),
                'price': prices[idx]
            })
    
    return results