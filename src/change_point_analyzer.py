import pandas as pd
import numpy as np
from typing import List, Dict

class ChangePointAnalyzer:
    """Analyze change points and correlate with events"""
    
    def __init__(self, change_points, events_df):
        self.change_points = change_points
        self.events_df = events_df
    
    def find_event_correlations(self, window_days=30):
        """Find events correlated with change points"""
        correlations = {}
        
        for cp in self.change_points:
            cp_date = cp['date']
            correlated_events = []
            
            for _, event in self.events_df.iterrows():
                days_diff = abs((event['Start_Date'] - cp_date).days)
                
                if days_diff <= window_days:
                    # Calculate correlation probability
                    probability = max(0, 1 - (days_diff / window_days))
                    
                    correlated_events.append({
                        'event_name': event['Event_Name'],
                        'event_date': event['Start_Date'],
                        'days_diff': days_diff,
                        'probability': probability,
                        'category': event['Category'],
                        'impact_magnitude': event['Impact_Magnitude']
                    })
            
            if correlated_events:
                # Sort by probability
                correlated_events.sort(key=lambda x: x['probability'], reverse=True)
                correlations[cp_date] = correlated_events
        
        return correlations
    
    def quantify_impacts(self):
        """Quantify impact of each correlated event"""
        impacts = []
        correlations = self.find_event_correlations()
        
        for cp_date, events in correlations.items():
            # Get the change point data
            cp_data = next(cp for cp in self.change_points if cp['date'] == cp_date)
            
            for event in events:
                impact = {
                    'event_name': event['event_name'],
                    'event_date': event['event_date'],
                    'change_point_date': cp_date,
                    'days_difference': event['days_diff'],
                    'price_change': cp_data['mean_change'] * 100,  # Convert to percentage
                    'pct_change': cp_data['pct_change'],
                    'probability': event['probability'],
                    'confidence': cp_data['probability'] * event['probability'],
                    'category': event['category'],
                    'impact_magnitude': event['impact_magnitude'],
                    'pre_event_price': 100 * (1 + cp_data['mean_before']),  # Base 100
                    'post_event_price': 100 * (1 + cp_data['mean_after'])
                }
                impacts.append(impact)
        
        return sorted(impacts, key=lambda x: x['confidence'], reverse=True)