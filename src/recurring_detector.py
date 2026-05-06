"""
Recurring Expense Detector Module
Identifies and tracks recurring transactions
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecurringDetector:
    """
    Detects recurring expenses and calculates patterns.
    
    Attributes:
        data (pd.DataFrame): Expense data
        recurring_expenses (dict): Detected recurring expenses
    """
    
    def __init__(self, data):
        """
        Initialize recurring expense detector.
        
        Args:
            data (pd.DataFrame): Expense data
        """
        self.data = data.copy()
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.recurring_expenses = {}
    
    def detect_recurring(self, similarity_threshold=0.9):
        """
        Detect recurring expenses.
        
        Args:
            similarity_threshold (float): Similarity threshold (0-1)
            
        Returns:
            dict: Detected recurring expenses
        """
        logger.info("\n" + "="*50)
        logger.info("DETECTING RECURRING EXPENSES")
        logger.info("="*50)
        
        # Group by description
        grouped = self.data.groupby('Description')
        
        logger.info("\n--- Analyzing Patterns ---")
        
        for description, group in grouped:
            if len(group) >= 2:  # At least 2 occurrences
                amounts = group['Amount'].values
                dates = sorted(group['Date'].values)
                
                # Check if amounts are similar
                mean_amount = np.mean(amounts)
                std_amount = np.std(amounts)
                cv = std_amount / mean_amount if mean_amount > 0 else 0  # Coefficient of variation
                
                # Check if dates are regular
                if len(dates) >= 2:
                    date_diffs = [(pd.Timestamp(dates[i+1]) - pd.Timestamp(dates[i])).days 
                                  for i in range(len(dates)-1)]
                    avg_gap = np.mean(date_diffs)
                    gap_std = np.std(date_diffs)
                    
                    # Is it recurring? (Similar amounts & regular intervals)
                    if cv < (1 - similarity_threshold) and gap_std < avg_gap * 0.5:
                        frequency = self._determine_frequency(avg_gap)
                        
                        self.recurring_expenses[description] = {
                            'Count': len(group),
                            'Average Amount': mean_amount,
                            'Amount Std Dev': std_amount,
                            'Average Gap (Days)': avg_gap,
                            'Frequency': frequency,
                            'Last Date': dates[-1],
                            'Total Spent': group['Amount'].sum(),
                            'Category': group['Category'].iloc[0]
                        }
                        
                        logger.info(f"\n✓ {description}")
                        logger.info(f"  Count: {len(group)} times")
                        logger.info(f"  Frequency: {frequency}")
                        logger.info(f"  Average Amount: ₹{mean_amount:.2f}")
                        logger.info(f"  Average Gap: {avg_gap:.1f} days")
        
        logger.info(f"\n✓ Found {len(self.recurring_expenses)} recurring expense patterns")
        return self.recurring_expenses
    
    def _determine_frequency(self, days):
        """
        Determine frequency based on average gap.
        
        Args:
            days (float): Average days between transactions
            
        Returns:
            str: Frequency description
        """
        if days < 5:
            return "Daily"
        elif days < 10:
            return "Weekly"
        elif days < 20:
            return "Bi-weekly"
        elif days < 40:
            return "Monthly"
        elif days < 100:
            return "Quarterly"
        else:
            return "Annual"
    
    def calculate_monthly_recurring(self):
        """
        Calculate monthly recurring expense impact.
        
        Returns:
            dict: Monthly recurring impact
        """
        logger.info("\n" + "="*50)
        logger.info("MONTHLY RECURRING EXPENSE IMPACT")
        logger.info("="*50)
        
        monthly_impact = {}
        total_monthly_recurring = 0
        
        for description, details in self.recurring_expenses.items():
            frequency = details['Frequency']
            amount = details['Average Amount']
            
            # Calculate monthly equivalent
            if frequency == "Daily":
                monthly_equiv = amount * 30
            elif frequency == "Weekly":
                monthly_equiv = amount * 4.3
            elif frequency == "Bi-weekly":
                monthly_equiv = amount * 2.15
            elif frequency == "Monthly":
                monthly_equiv = amount
            elif frequency == "Quarterly":
                monthly_equiv = amount / 3
            elif frequency == "Annual":
                monthly_equiv = amount / 12
            else:
                monthly_equiv = 0
            
            monthly_impact[description] = monthly_equiv
            total_monthly_recurring += monthly_equiv
            
            logger.info(f"{description}: ₹{monthly_equiv:.2f}/month")
        
        logger.info(f"\nTotal Monthly Recurring: ₹{total_monthly_recurring:.2f}")
        
        return {
            'Individual': monthly_impact,
            'Total': total_monthly_recurring
        }
    
    def project_yearly_spending(self):
        """
        Project yearly spending based on recurring expenses.
        
        Returns:
            float: Projected yearly spending
        """
        monthly_recurring = self.calculate_monthly_recurring()['Total']
        yearly_projection = monthly_recurring * 12
        
        logger.info(f"\nProjected Yearly Spending (Recurring): ₹{yearly_projection:,.2f}")
        
        return yearly_projection
    
    def get_next_occurrences(self, days_ahead=30):
        """
        Predict next occurrences of recurring expenses.
        
        Args:
            days_ahead (int): Number of days to predict
            
        Returns:
            list: Predicted upcoming expenses
        """
        logger.info("\n" + "="*50)
        logger.info(f"PREDICTED EXPENSES (Next {days_ahead} Days)")
        logger.info("="*50)
        
        upcoming = []
        today = datetime.now()
        
        for description, details in self.recurring_expenses.items():
            last_date = pd.Timestamp(details['Last Date']).to_pydatetime()
            gap = details['Average Gap (Days)']
            amount = details['Average Amount']
            
            # Calculate next occurrence
            next_date = last_date + timedelta(days=int(gap))
            
            if next_date <= today + timedelta(days=days_ahead):
                upcoming.append({
                    'Description': description,
                    'Expected Date': next_date,
                    'Amount': amount,
                    'Category': details['Category']
                })
                
                days_until = (next_date - today).days
                logger.info(f"{description}: ₹{amount:.2f} on {next_date.date()} ({days_until} days)")
        
        return upcoming
    
    def display_summary(self):
        """Display recurring expenses summary."""
        logger.info("\n" + "="*50)
        logger.info("RECURRING EXPENSES SUMMARY")
        logger.info("="*50)
        
        if not self.recurring_expenses:
            logger.info("No recurring expenses detected")
            return
        
        logger.info(f"\nTotal Recurring Patterns: {len(self.recurring_expenses)}")
        
        # Top recurring by amount
        sorted_recurring = sorted(
            self.recurring_expenses.items(),
            key=lambda x: x[1]['Average Amount'],
            reverse=True
        )
        
        logger.info("\nTop Recurring Expenses:")
        for i, (desc, details) in enumerate(sorted_recurring[:5], 1):
            logger.info(f"{i}. {desc}: ₹{details['Average Amount']:.2f} ({details['Frequency']})")


def detect_recurring_expenses(data):
    """
    Convenience function to detect recurring expenses.
    
    Args:
        data (pd.DataFrame): Expense data
        
    Returns:
        RecurringDetector: Detector object with results
    """
    detector = RecurringDetector(data)
    detector.detect_recurring()
    detector.calculate_monthly_recurring()
    detector.project_yearly_spending()
    detector.get_next_occurrences()
    detector.display_summary()
    return detector


if __name__ == "__main__":
    print("Recurring Expense Detector - Ready for import")
