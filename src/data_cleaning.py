"""
Data Cleaning Module
Handles data validation, cleaning, and preprocessing
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Cleans and validates expense data.
    
    Attributes:
        data (pd.DataFrame): Input data
        cleaned_data (pd.DataFrame): Processed data
    """
    
    def __init__(self, data):
        """
        Initialize DataCleaner with raw data.
        
        Args:
            data (pd.DataFrame): Raw expense data
        """
        self.data = data.copy()
        self.cleaned_data = None
        self.cleaning_report = {}
    
    def clean(self):
        """
        Execute complete cleaning pipeline.
        
        Returns:
            pd.DataFrame: Cleaned data
        """
        logger.info("\n" + "="*50)
        logger.info("STARTING DATA CLEANING PROCESS")
        logger.info("="*50)
        
        # Step 1: Handle missing values
        self._handle_missing_values()
        
        # Step 2: Convert data types
        self._convert_data_types()
        
        # Step 3: Remove duplicates
        self._remove_duplicates()
        
        # Step 4: Standardize text
        self._standardize_text()
        
        # Step 5: Validate amount
        self._validate_amounts()
        
        # Step 6: Validate dates
        self._validate_dates()
        
        self.cleaned_data = self.data
        logger.info("\n✓ Data cleaning completed successfully!")
        return self.cleaned_data
    
    def _handle_missing_values(self):
        """Handle missing values in the data."""
        logger.info("\n--- Handling Missing Values ---")
        
        missing_before = self.data.isnull().sum().sum()
        
        # Drop rows where Amount is missing (critical field)
        self.data = self.data.dropna(subset=['Amount'])
        
        # Fill missing Description with "Unknown"
        if 'Description' in self.data.columns:
            self.data['Description'] = self.data['Description'].fillna('Unknown')
        
        # Fill missing PaymentMethod with "Cash"
        if 'PaymentMethod' in self.data.columns:
            self.data['PaymentMethod'] = self.data['PaymentMethod'].fillna('Cash')
        
        missing_after = self.data.isnull().sum().sum()
        
        logger.info(f"Missing values before: {missing_before}")
        logger.info(f"Missing values after: {missing_after}")
        self.cleaning_report['Missing Values Removed'] = missing_before - missing_after
    
    def _convert_data_types(self):
        """Convert columns to appropriate data types."""
        logger.info("\n--- Converting Data Types ---")
        
        try:
            # Convert Date to datetime
            self.data['Date'] = pd.to_datetime(self.data['Date'], format='mixed', dayfirst=True)
            logger.info("✓ Date converted to datetime")
            
            # Convert Amount to float
            self.data['Amount'] = pd.to_numeric(self.data['Amount'], errors='coerce')
            logger.info("✓ Amount converted to float")
            
            # Convert Description and PaymentMethod to string
            self.data['Description'] = self.data['Description'].astype(str)
            self.data['PaymentMethod'] = self.data['PaymentMethod'].astype(str)
            logger.info("✓ Text columns converted to string")
            
        except Exception as e:
            logger.error(f"Error converting data types: {str(e)}")
            raise
    
    def _remove_duplicates(self):
        """Remove duplicate entries."""
        logger.info("\n--- Removing Duplicates ---")
        
        duplicates_before = len(self.data)
        
        # Remove complete duplicates
        self.data = self.data.drop_duplicates()
        
        duplicates_after = len(self.data)
        removed = duplicates_before - duplicates_after
        
        logger.info(f"Duplicates removed: {removed}")
        self.cleaning_report['Duplicates Removed'] = removed
    
    def _standardize_text(self):
        """Standardize text fields."""
        logger.info("\n--- Standardizing Text ---")
        
        # Strip whitespace
        self.data['Description'] = self.data['Description'].str.strip()
        self.data['PaymentMethod'] = self.data['PaymentMethod'].str.strip()
        
        # Convert to title case for consistency
        self.data['PaymentMethod'] = self.data['PaymentMethod'].str.title()
        
        logger.info("✓ Text standardized")
    
    def _validate_amounts(self):
        """Validate and handle amount values."""
        logger.info("\n--- Validating Amounts ---")
        
        # Check for non-positive amounts
        invalid_amounts = (self.data['Amount'] <= 0).sum()
        
        if invalid_amounts > 0:
            logger.warning(f"Found {invalid_amounts} non-positive amounts. Removing them.")
            self.data = self.data[self.data['Amount'] > 0]
        
        logger.info(f"✓ Amount validation completed")
        self.cleaning_report['Invalid Amounts Removed'] = invalid_amounts
    
    def _validate_dates(self):
        """Validate date values."""
        logger.info("\n--- Validating Dates ---")
        
        # Check for future dates (optional - depends on use case)
        today = datetime.now()
        future_dates = (self.data['Date'] > today).sum()
        
        if future_dates > 0:
            logger.warning(f"Found {future_dates} future dates. Keeping them (might be budgeted expenses).")
        
        logger.info("✓ Date validation completed")
        self.cleaning_report['Future Dates Found'] = future_dates
    
    def get_cleaning_report(self):
        """
        Get cleaning report.
        
        Returns:
            dict: Summary of cleaning operations
        """
        return self.cleaning_report
    
    def display_report(self):
        """Display cleaning report."""
        logger.info("\n" + "="*50)
        logger.info("CLEANING REPORT")
        logger.info("="*50)
        
        for key, value in self.cleaning_report.items():
            logger.info(f"{key}: {value}")
        
        logger.info(f"\nFinal record count: {len(self.cleaned_data)}")


def clean_expense_data(data):
    """
    Convenience function to clean expense data.
    
    Args:
        data (pd.DataFrame): Raw expense data
        
    Returns:
        pd.DataFrame: Cleaned data
    """
    cleaner = DataCleaner(data)
    return cleaner.clean()


if __name__ == "__main__":
    # Example usage
    print("This module is meant to be imported and used within the main pipeline.")
