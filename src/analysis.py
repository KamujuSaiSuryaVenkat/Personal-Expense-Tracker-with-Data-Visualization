"""
Analysis Module
Performs statistical and analytical operations on expense data
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpenseAnalyzer:
    """
    Analyzes expense data and generates insights.
    
    Attributes:
        data (pd.DataFrame): Expense data
        analysis_results (dict): Stores analysis results
    """
    
    def __init__(self, data):
        """
        Initialize analyzer with expense data.
        
        Args:
            data (pd.DataFrame): Expense data
        """
        self.data = data
        self.analysis_results = {}
    
    def analyze(self):
        """
        Execute complete analysis pipeline.
        
        Returns:
            dict: Analysis results
        """
        logger.info("\n" + "="*50)
        logger.info("STARTING EXPENSE ANALYSIS")
        logger.info("="*50)
        
        # Overall statistics
        self._calculate_overall_stats()
        
        # Category analysis
        self._analyze_categories()
        
        # Payment method analysis
        self._analyze_payment_methods()
        
        # Monthly analysis
        self._analyze_monthly_trends()
        
        # Daily analysis
        self._analyze_daily_patterns()
        
        # Top transactions
        self._find_top_transactions()
        
        logger.info("\n✓ Analysis completed successfully!")
        return self.analysis_results
    
    def _calculate_overall_stats(self):
        """Calculate overall statistics."""
        logger.info("\n--- Overall Statistics ---")
        
        total_expense = self.data['Amount'].sum()
        avg_expense = self.data['Amount'].mean()
        median_expense = self.data['Amount'].median()
        max_expense = self.data['Amount'].max()
        min_expense = self.data['Amount'].min()
        std_dev = self.data['Amount'].std()
        
        self.analysis_results['Overall Statistics'] = {
            'Total Expense': round(total_expense, 2),
            'Average Transaction': round(avg_expense, 2),
            'Median Transaction': round(median_expense, 2),
            'Maximum Transaction': round(max_expense, 2),
            'Minimum Transaction': round(min_expense, 2),
            'Std Deviation': round(std_dev, 2),
            'Total Transactions': len(self.data)
        }
        
        for key, value in self.analysis_results['Overall Statistics'].items():
            logger.info(f"{key}: {value}")
    
    def _analyze_categories(self):
        """Analyze expenses by category."""
        logger.info("\n--- Category Analysis ---")
        
        category_analysis = self.data.groupby('Category').agg({
            'Amount': ['sum', 'count', 'mean', 'std']
        }).round(2)
        
        category_analysis.columns = ['Total', 'Count', 'Average', 'Std Dev']
        category_analysis = category_analysis.sort_values('Total', ascending=False)
        
        self.analysis_results['Category Analysis'] = category_analysis.to_dict('index')
        
        logger.info("\nTop 5 Categories by Spending:")
        for idx, (category, row) in enumerate(category_analysis.head().iterrows(), 1):
            logger.info(f"{idx}. {category}: ₹{row['Total']} ({row['Count']} transactions)")
    
    def _analyze_payment_methods(self):
        """Analyze expenses by payment method."""
        logger.info("\n--- Payment Method Analysis ---")
        
        payment_analysis = self.data.groupby('PaymentMethod').agg({
            'Amount': ['sum', 'count', 'mean']
        }).round(2)
        
        payment_analysis.columns = ['Total', 'Count', 'Average']
        payment_analysis = payment_analysis.sort_values('Total', ascending=False)
        
        self.analysis_results['Payment Method Analysis'] = payment_analysis.to_dict('index')
        
        for method, stats in self.analysis_results['Payment Method Analysis'].items():
            logger.info(f"{method}: ₹{stats['Total']} ({stats['Count']} transactions)")
    
    def _analyze_monthly_trends(self):
        """Analyze monthly spending trends."""
        logger.info("\n--- Monthly Trend Analysis ---")
        
        # Convert date to datetime if not already
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        
        # Extract year-month
        self.data['YearMonth'] = self.data['Date'].dt.to_period('M')
        
        monthly_analysis = self.data.groupby('YearMonth').agg({
            'Amount': ['sum', 'count', 'mean']
        }).round(2)
        
        monthly_analysis.columns = ['Total', 'Count', 'Average']
        
        self.analysis_results['Monthly Analysis'] = monthly_analysis.to_dict('index')
        
        logger.info("\nMonthly Spending:")
        for month, stats in self.analysis_results['Monthly Analysis'].items():
            logger.info(f"{month}: ₹{stats['Total']} ({stats['Count']} transactions)")
    
    def _analyze_daily_patterns(self):
        """Analyze daily spending patterns."""
        logger.info("\n--- Daily Pattern Analysis ---")
        
        # Day of week analysis
        self.data['DayOfWeek'] = self.data['Date'].dt.day_name()
        
        daily_analysis = self.data.groupby('DayOfWeek').agg({
            'Amount': ['sum', 'count', 'mean']
        }).round(2)
        
        daily_analysis.columns = ['Total', 'Count', 'Average']
        
        # Reorder by day
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_analysis = daily_analysis.reindex([d for d in day_order if d in daily_analysis.index])
        
        self.analysis_results['Daily Pattern Analysis'] = daily_analysis.to_dict('index')
        
        logger.info("\nSpending by Day of Week:")
        for day, stats in daily_analysis.iterrows():
            logger.info(f"{day}: ₹{stats['Total']} (avg: ₹{stats['Average']})")
    
    def _find_top_transactions(self):
        """Find top transactions."""
        logger.info("\n--- Top Transactions ---")
        
        top_transactions = self.data.nlargest(5, 'Amount')[['Date', 'Description', 'Amount', 'Category']]
        
        self.analysis_results['Top Transactions'] = top_transactions.to_dict('records')
        
        logger.info("\nTop 5 Transactions:")
        for idx, (_, trans) in enumerate(top_transactions.iterrows(), 1):
            logger.info(f"{idx}. ₹{trans['Amount']} - {trans['Description']} ({trans['Category']})")
    
    def get_category_breakdown(self):
        """
        Get category breakdown with percentages.
        
        Returns:
            pd.DataFrame: Category breakdown
        """
        category_totals = self.data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        total = category_totals.sum()
        
        breakdown = pd.DataFrame({
            'Category': category_totals.index,
            'Amount': category_totals.values,
            'Percentage': (category_totals.values / total * 100).round(2)
        })
        
        return breakdown
    
    def get_spending_insights(self):
        """
        Get spending insights and recommendations.
        
        Returns:
            dict: Insights and recommendations
        """
        insights = {}
        
        # Highest spending category
        category_totals = self.data.groupby('Category')['Amount'].sum()
        highest_category = category_totals.idxmax()
        highest_amount = category_totals.max()
        
        insights['Highest Spending'] = f"{highest_category}: ₹{highest_amount:.2f}"
        
        # Average daily spending
        date_range = (self.data['Date'].max() - self.data['Date'].min()).days + 1
        daily_avg = self.data['Amount'].sum() / max(date_range, 1)
        
        insights['Daily Average'] = f"₹{daily_avg:.2f}"
        
        # Most used payment method
        payment_method_counts = self.data['PaymentMethod'].value_counts()
        most_used = payment_method_counts.idxmax()
        
        insights['Most Used Payment Method'] = most_used
        
        return insights
    
    def display_summary(self):
        """Display analysis summary."""
        logger.info("\n" + "="*50)
        logger.info("ANALYSIS SUMMARY")
        logger.info("="*50)
        
        if 'Overall Statistics' in self.analysis_results:
            logger.info("\nOverall Statistics:")
            for key, value in self.analysis_results['Overall Statistics'].items():
                logger.info(f"  {key}: {value}")


def analyze_expenses(data):
    """
    Convenience function to analyze expenses.
    
    Args:
        data (pd.DataFrame): Expense data
        
    Returns:
        dict: Analysis results
    """
    analyzer = ExpenseAnalyzer(data)
    return analyzer.analyze()


if __name__ == "__main__":
    print("This module is meant to be imported and used within the main pipeline.")
