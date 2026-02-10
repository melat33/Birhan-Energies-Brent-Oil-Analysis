"""
Event Creator - Professional Event Database
Creates 15+ events from 1987-2022
"""
import pandas as pd
import os
from datetime import datetime

class EventCreator:
    """Create comprehensive event database"""
    
    def create_events_1987_2022(self):
        """Create events from 1987 to 2022"""
        events = [
            # ========== 1987-1999 ==========
            {
                'Event_Name': 'Black Monday Stock Crash',
                'Start_Date': '1987-10-19',
                'Category': 'Economic',
                'Expected_Impact': 'Negative',
                'Impact_Magnitude': 'High',
                'Region': 'Global',
                'Description': 'Largest one-day stock market decline affecting oil demand'
            },
            {
                'Event_Name': 'Iran-Iraq War Ends',
                'Start_Date': '1988-08-20',
                'Category': 'Geopolitical',
                'Expected_Impact': 'Negative',
                'Impact_Magnitude': 'High',
                'Region': 'Middle East',
                'Description': 'End of 8-year war that disrupted oil production'
            },
            {
                'Event_Name': 'Exxon Valdez Oil Spill',
                'Start_Date': '1989-03-24',
                'Category': 'Environmental',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'Medium',
                'Region': 'North America',
                'Description': 'Massive oil spill increasing environmental regulations'
            },
            {
                'Event_Name': 'Gulf War',
                'Start_Date': '1990-08-02',
                'Category': 'Geopolitical',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'Very High',
                'Region': 'Middle East',
                'Description': 'Iraq invasion of Kuwait causing supply disruption'
            },
            {
                'Event_Name': 'Asian Financial Crisis',
                'Start_Date': '1997-07-02',
                'Category': 'Economic',
                'Expected_Impact': 'Negative',
                'Impact_Magnitude': 'High',
                'Region': 'Asia',
                'Description': 'Regional economic collapse reducing oil demand'
            },
            
            # ========== 2000-2009 ==========
            {
                'Event_Name': '9/11 Attacks',
                'Start_Date': '2001-09-11',
                'Category': 'Geopolitical',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'High',
                'Region': 'Global',
                'Description': 'Terrorism fears increasing Middle East risk premium'
            },
            {
                'Event_Name': 'Iraq War',
                'Start_Date': '2003-03-20',
                'Category': 'Geopolitical',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'Very High',
                'Region': 'Middle East',
                'Description': 'US invasion creating supply uncertainty'
            },
            {
                'Event_Name': 'Hurricane Katrina',
                'Start_Date': '2005-08-23',
                'Category': 'Supply',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'High',
                'Region': 'North America',
                'Description': 'Gulf of Mexico production shutdown'
            },
            {
                'Event_Name': '2008 Financial Crisis',
                'Start_Date': '2008-09-15',
                'Category': 'Economic',
                'Expected_Impact': 'Negative',
                'Impact_Magnitude': 'Very High',
                'Region': 'Global',
                'Description': 'Global recession crushing oil demand'
            },
            {
                'Event_Name': 'OPEC Production Cut 2008',
                'Start_Date': '2008-12-17',
                'Category': 'OPEC Decision',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'High',
                'Region': 'Global',
                'Description': 'OPEC cuts production to stabilize prices'
            },
            
            # ========== 2010-2022 ==========
            {
                'Event_Name': 'Arab Spring',
                'Start_Date': '2010-12-17',
                'Category': 'Geopolitical',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'Medium',
                'Region': 'Middle East',
                'Description': 'Regional instability affecting oil production'
            },
            {
                'Event_Name': 'Libyan Civil War',
                'Start_Date': '2011-02-15',
                'Category': 'Geopolitical',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'High',
                'Region': 'Africa',
                'Description': 'Major oil producer supply disruption'
            },
            {
                'Event_Name': 'US Shale Boom',
                'Start_Date': '2014-01-01',
                'Category': 'Supply',
                'Expected_Impact': 'Negative',
                'Impact_Magnitude': 'High',
                'Region': 'North America',
                'Description': 'Fracking revolution increases oil supply'
            },
            {
                'Event_Name': 'OPEC Price War 2014',
                'Start_Date': '2014-11-27',
                'Category': 'OPEC Decision',
                'Expected_Impact': 'Negative',
                'Impact_Magnitude': 'Very High',
                'Region': 'Global',
                'Description': 'OPEC maintains production despite oversupply'
            },
            {
                'Event_Name': 'COVID-19 Pandemic',
                'Start_Date': '2020-03-11',
                'Category': 'Economic',
                'Expected_Impact': 'Negative',
                'Impact_Magnitude': 'Very High',
                'Region': 'Global',
                'Description': 'Global lockdowns causing demand collapse'
            },
            {
                'Event_Name': 'OPEC+ Historic Cut 2020',
                'Start_Date': '2020-04-12',
                'Category': 'OPEC Decision',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'Very High',
                'Region': 'Global',
                'Description': 'Largest production cut in history'
            },
            {
                'Event_Name': 'Russia-Ukraine War',
                'Start_Date': '2022-02-24',
                'Category': 'Geopolitical',
                'Expected_Impact': 'Positive',
                'Impact_Magnitude': 'Very High',
                'Region': 'Europe',
                'Description': 'Sanctions and supply chain disruptions'
            }
        ]
        
        df = pd.DataFrame(events)
        df['Start_Date'] = pd.to_datetime(df['Start_Date'])
        df['Year'] = df['Start_Date'].dt.year
        df['Impact_Score'] = df['Impact_Magnitude'].map({
            'Very High': 4, 'High': 3, 'Medium': 2, 'Low': 1
        })
        
        return df
    
    def save_to_csv(self, filepath='data/raw/events_1987_2022.csv'):
        """Save events to CSV"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        events_df = self.create_events_1987_2022()
        events_df.to_csv(filepath, index=False)
        print(f"Events saved to: {filepath}")
        print(f"Total events created: {len(events_df)}")
        print(f"Date range: {events_df['Year'].min()} - {events_df['Year'].max()}")
        
        return events_df

# Main execution
if __name__ == "__main__":
    # Create EventCreator instance
    event_creator = EventCreator()
    
    # Save events to data/raw directory
    events_df = event_creator.save_to_csv()
    
    # Display summary
    print("\n=== Event Database Summary ===")
    print(events_df[['Event_Name', 'Start_Date', 'Category', 'Impact_Magnitude']].head())
    
    print("\n=== Category Distribution ===")
    print(events_df['Category'].value_counts())
    
    print("\n=== Impact Distribution ===")
    print(events_df['Impact_Magnitude'].value_counts())