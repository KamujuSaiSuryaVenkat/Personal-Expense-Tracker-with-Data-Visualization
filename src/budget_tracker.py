"""
Budget Tracking Module
Manages expense budgets and generates overspending alerts
"""

import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BudgetTracker:
    """
    Tracks expenses against budgets and generates alerts.
    
    Attributes:
        data (pd.DataFrame): Expense data
        budgets (dict): Budget limits by category
        alerts (list): Generated alerts
    """
    
    def __init__(self, data, budgets=None):
        """
        Initialize budget tracker.
        
        Args:
            data (pd.DataFrame): Expense data
            budgets (dict): Budget limits by category
        """
        self.data = data
        self.budgets = budgets or self._default_budgets()
        self.alerts = []
    
    def _default_budgets(self):
        """
        Get default budgets.
        
        Returns:
            dict: Default budget limits
        """
        return {
            'Food & Dining': 10000,
            'Transportation': 8000,
            'Entertainment': 3000,
            'Shopping': 5000,
            'Utilities': 3000,
            'Health & Medical': 5000,
            'Education': 15000,
            'Subscriptions': 2000,
            'Personal Care': 2000,
            'Other': 3000
        }
    
    def check_budgets(self):
        """
        Check if expenses exceed budgets.
        
        Returns:
            dict: Budget status for each category
        """
        logger.info("\n" + "="*50)
        logger.info("BUDGET ANALYSIS")
        logger.info("="*50)
        
        budget_status = {}
        self.alerts = []
        
        # Group by category
        category_spending = self.data.groupby('Category')['Amount'].sum()
        
        logger.info("\n--- Category Budget Status ---")
        
        for category, spent in category_spending.items():
            budget = self.budgets.get(category, float('inf'))
            
            remaining = budget - spent
            percentage = (spent / budget * 100) if budget != float('inf') else 0
            
            status = {
                'Category': category,
                'Budget': budget,
                'Spent': spent,
                'Remaining': remaining,
                'Percentage': percentage
            }
            
            budget_status[category] = status
            
            # Generate alerts
            if percentage >= 100:
                alert = f"🚨 OVER BUDGET: {category} spent ₹{spent:.0f} (Budget: ₹{budget:.0f})"
                self.alerts.append(alert)
                logger.warning(alert)
            elif percentage >= 80:
                alert = f"⚠️ WARNING: {category} at {percentage:.1f}% of budget (₹{spent:.0f} / ₹{budget:.0f})"
                self.alerts.append(alert)
                logger.warning(alert)
            else:
                logger.info(f"✓ {category}: ₹{spent:.0f} / ₹{budget:.0f} ({percentage:.1f}%)")
        
        return budget_status
    
    def get_savings_potential(self):
        """
        Calculate potential savings.
        
        Returns:
            dict: Savings analysis
        """
        logger.info("\n" + "="*50)
        logger.info("SAVINGS POTENTIAL ANALYSIS")
        logger.info("="*50)
        
        category_spending = self.data.groupby('Category')['Amount'].sum()
        
        total_budget = sum(self.budgets.values())
        total_spent = self.data['Amount'].sum()
        potential_savings = total_budget - total_spent
        
        savings_data = {
            'Total Budget': total_budget,
            'Total Spent': total_spent,
            'Potential Savings': potential_savings,
            'Savings Percentage': (potential_savings / total_budget * 100) if total_budget > 0 else 0,
            'Categories Over Budget': len([s for s in category_spending.values() 
                                          if s > self.budgets.get(list(category_spending.index)[
                                              list(category_spending).index(s)], float('inf'))]),
            'Categories Within Budget': len([s for s in category_spending.values() 
                                            if s <= self.budgets.get(list(category_spending.index)[
                                                list(category_spending).index(s)], float('inf'))])
        }
        
        logger.info(f"Total Budget: ₹{total_budget:,.0f}")
        logger.info(f"Total Spent: ₹{total_spent:,.0f}")
        logger.info(f"Potential Savings: ₹{potential_savings:,.0f} ({savings_data['Savings Percentage']:.1f}%)")
        logger.info(f"Categories Over Budget: {savings_data['Categories Over Budget']}")
        logger.info(f"Categories Within Budget: {savings_data['Categories Within Budget']}")
        
        return savings_data
    
    def set_custom_budget(self, category, limit):
        """
        Set custom budget for category.
        
        Args:
            category (str): Category name
            limit (float): Budget limit
        """
        self.budgets[category] = limit
        logger.info(f"✓ Budget set for {category}: ₹{limit}")
    
    def get_monthly_budget_analysis(self):
        """
        Get monthly budget vs actual spending.
        
        Returns:
            pd.DataFrame: Monthly analysis
        """
        logger.info("\n--- Monthly Budget Analysis ---")
        
        # Convert to datetime
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.data['YearMonth'] = self.data['Date'].dt.to_period('M')
        
        monthly_spending = self.data.groupby('YearMonth')['Amount'].sum()
        monthly_budget = len(monthly_spending) * sum(self.budgets.values()) / 12
        
        analysis = pd.DataFrame({
            'Month': monthly_spending.index,
            'Budget': monthly_budget,
            'Actual': monthly_spending.values,
            'Difference': monthly_budget - monthly_spending.values
        })
        
        return analysis
    
    def display_alerts(self):
        """Display all generated alerts."""
        if self.alerts:
            logger.info("\n" + "="*50)
            logger.info("BUDGET ALERTS")
            logger.info("="*50)
            for alert in self.alerts:
                logger.warning(alert)
        else:
            logger.info("\n✓ No budget alerts - you're within budget!")
    
    def get_recommendation(self):
        """
        Get spending reduction recommendations.
        
        Returns:
            list: Recommendations
        """
        logger.info("\n" + "="*50)
        logger.info("RECOMMENDATIONS")
        logger.info("="*50)
        
        recommendations = []
        category_spending = self.data.groupby('Category')['Amount'].sum()
        
        for category, spent in category_spending.items():
            budget = self.budgets.get(category, float('inf'))
            
            if spent > budget:
                reduction_needed = spent - budget
                reduction_percentage = (reduction_needed / spent) * 100
                recommendation = f"Reduce {category} spending by ₹{reduction_needed:.0f} ({reduction_percentage:.1f}%)"
                recommendations.append(recommendation)
                logger.info(f"💡 {recommendation}")
        
        if not recommendations:
            logger.info("✓ No recommendations - keep up the good budgeting!")
        
        return recommendations


def analyze_budgets(data, budgets=None):
    """
    Convenience function to analyze budgets.
    
    Args:
        data (pd.DataFrame): Expense data
        budgets (dict): Budget limits
        
    Returns:
        BudgetTracker: Tracker object with results
    """
    tracker = BudgetTracker(data, budgets)
    tracker.check_budgets()
    tracker.display_alerts()
    tracker.get_savings_potential()
    tracker.get_recommendation()
    return tracker


if __name__ == "__main__":
    print("Budget Tracker Module - Ready for import")
