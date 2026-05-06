"""
Data Loader Module
Handles reading expense data from CSV files
"""

import pandas as pd
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads expense data from CSV files.
    
    Attributes:
        file_path (str): Path to the CSV file
        required_columns (list): Expected columns in the CSV
    """
    
    def __init__(self, file_path):
        """
        Initialize DataLoader with file path.
        
        Args:
            file_path (str): Path to the CSV file
        """
        self.file_path = file_path
        self.required_columns = ['Date', 'Description', 'Amount', 'PaymentMethod']
        self.data = None
    
    def load_csv(self):
        """
        Load data from CSV file.
        
        Returns:
            pd.DataFrame: Loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required columns are missing
        """
        try:
            # Check if file exists
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found: {self.file_path}")
            
            # Read CSV file
            self.data = pd.read_csv(self.file_path)
            logger.info(f"Successfully loaded {len(self.data)} records from {self.file_path}")
            
            # Validate columns
            self._validate_columns()
            
            return self.data
        
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise
    
    def _validate_columns(self):
        """
        Validate if all required columns are present.
        
        Raises:
            ValueError: If required columns are missing
        """
        missing_columns = [col for col in self.required_columns if col not in self.data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        logger.info("✓ All required columns present")
    
    def get_data(self):
        """
        Get loaded data.
        
        Returns:
            pd.DataFrame: Expense data
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_csv() first.")
        return self.data
    
    def display_summary(self):
        """
        Display data summary.
        
        Returns:
            dict: Summary statistics
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_csv() first.")
        
        summary = {
            'Total Records': len(self.data),
            'Columns': list(self.data.columns),
            'Data Types': dict(self.data.dtypes),
            'Missing Values': dict(self.data.isnull().sum())
        }
        
        logger.info("\n" + "="*50)
        logger.info("DATA SUMMARY")
        logger.info("="*50)
        logger.info(f"Total Records: {summary['Total Records']}")
        logger.info(f"Missing Values:\n{summary['Missing Values']}")
        
        return summary


def load_expense_data(file_path):
    """
    Convenience function to load expense data.
    
    Args:
        file_path (str): Path to CSV file
        
    Returns:
        pd.DataFrame: Expense data
    """
    loader = DataLoader(file_path)
    return loader.load_csv()


if __name__ == "__main__":
    # Example usage
    sample_file = "data/sample_expenses.csv"
    
    if os.path.exists(sample_file):
        loader = DataLoader(sample_file)
        data = loader.load_csv()
        loader.display_summary()
        print("\nFirst few records:")
        print(data.head())
    else:
        print(f"Sample file not found: {sample_file}")
