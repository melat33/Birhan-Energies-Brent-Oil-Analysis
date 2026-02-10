import pandas as pd
import numpy as np
import os

class DataLoader:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.price_data = None
        self.events_data = None
        
    def load_all_data(self):
        """Load all datasets"""
        self.load_price_data()
        self.load_events_data()
        self.calculate_metrics()
        
    def load_price_data(self):
        """Load Brent oil price data"""
        file_path = os.path.join(self.data_dir, 'raw', 'BrentOilPrices.csv')
        self.price_data = pd.read_csv(file_path)
        self.price_data['Date'] = pd.to_datetime(self.price_data['Date'])
        
    def load_events_data(self):
        """Load events data"""
        file_path = os.path.join(self.data_dir, 'raw', 'events_1987_2022.csv')
        self.events_data = pd.read_csv(file_path)
        self.events_data['Start_Date'] = pd.to_datetime(self.events_data['Start_Date'])
        
    def calculate_metrics(self):
        """Calculate derived metrics"""
        if self.price_data is not None:
            self.price_data['Returns'] = self.price_data['Price'].pct_change()
            self.price_data['Log_Returns'] = np.log(self.price_data['Price']).diff()
            self.price_data['Volatility'] = self.price_data['Returns'].rolling(30).std() * np.sqrt(252) * 100