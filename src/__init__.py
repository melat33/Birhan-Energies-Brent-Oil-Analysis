"""
Birhan Energies Analytics Package
Professional Oil Price Analysis
"""

__version__ = "1.0.0"
__author__ = "Birhan Energies Data Science Team"

from .data_manager import DataManager
from .event_creator import EventCreator
from .visualization import Task1Visualizer
from .report_generator import ReportGenerator

__all__ = [
    'DataManager',
    'EventCreator',
    'Task1Visualizer',
    'ReportGenerator'
]