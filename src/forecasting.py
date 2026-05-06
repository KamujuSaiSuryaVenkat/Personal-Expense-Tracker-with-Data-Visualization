"""
Spending Forecasting Module
Predicts future spending based on historical patterns
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpendingForecaster:
    """
    Forecasts future spending using machine learning.
    
    Attributes:
        data (pd.DataFrame): Historical expense data
        forecasts (dict): Generated forecasts
    """
    
    def __init__(self, data):
        """
        Initialize spending forecaster.
        
        Args:
            data (pd.DataFrame): Expense data
        """
        self.data = data.copy()
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.forecasts = {}
    
    def forecast_monthly_spending(self, months_ahead=3):
        """
        Forecast monthly spending for next N months.
        
        Args:
            months_ahead (int): Number of months to forecast
            
        Returns:
            pd.DataFrame: Forecasted monthly spending
        """
        logger.info("\n" + "="*50)
        logger.info(f"FORECASTING NEXT {months_ahead} MONTHS")
        logger.info("="*50)
        
        # Get monthly spending
        self.data['YearMonth'] = self.data['Date'].dt.to_period('M')
        monthly_data = self.data.groupby('YearMonth')['Amount'].sum()
        
        # Prepare data for linear regression
        X = np.array(range(len(monthly_data))).reshape(-1, 1)
        y = monthly_data.values
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Forecast future months
        future_X = np.array(range(len(monthly_data), len(monthly_data) + months_ahead)).reshape(-1, 1)
        forecasted = model.predict(future_X)
        
        # Create forecast dataframe
        last_date = monthly_data.index[-1]
        forecast_dates = []
        for i in range(1, months_ahead + 1):
            forecast_dates.append(last_date + i)
        
        forecast_df = pd.DataFrame({
            'Month': forecast_dates,
            'Forecasted Amount': forecasted,
            'Upper Bound (95%)': forecasted * 1.2,
            'Lower Bound (95%)': forecasted * 0.8
        })
        
        logger.info("\n--- Forecasted Monthly Spending ---")
        for _, row in forecast_df.iterrows():
            logger.info(f"{row['Month']}: ₹{row['Forecasted Amount']:.0f} " +
                       f"(₹{row['Lower Bound (95%)']:.0f} - ₹{row['Upper Bound (95%)']:.0f})")
        
        self.forecasts['monthly'] = forecast_df
        return forecast_df
    
    def forecast_by_category(self, months_ahead=3):
        """
        Forecast spending by category.
        
        Args:
            months_ahead (int): Number of months to forecast
            
        Returns:
            dict: Forecasts by category
        """
        logger.info(f"\n--- Forecasting by Category ({months_ahead} months) ---")
        
        category_forecasts = {}
        
        for category in self.data['Category'].unique():
            category_data = self.data[self.data['Category'] == category]
            category_data_grouped = category_data.groupby(
                category_data['Date'].dt.to_period('M')
            )['Amount'].sum()
            
            if len(category_data_grouped) >= 2:
                X = np.array(range(len(category_data_grouped))).reshape(-1, 1)
                y = category_data_grouped.values
                
                model = LinearRegression()
                model.fit(X, y)
                
                future_X = np.array(range(len(category_data_grouped), 
                                        len(category_data_grouped) + months_ahead)).reshape(-1, 1)
                forecasted = model.predict(future_X)
                
                category_forecasts[category] = {
                    'Average': np.mean(forecasted),
                    'Total': np.sum(forecasted),
                    'Monthly_Forecast': forecasted.tolist()
                }
                
                logger.info(f"{category}: ₹{np.mean(forecasted):.0f}/month")
        
        self.forecasts['by_category'] = category_forecasts
        return category_forecasts
    
    def forecast_yearly_spending(self):
        """
        Forecast yearly spending.
        
        Returns:
            dict: Yearly forecast
        """
        logger.info("\n--- Yearly Spending Forecast ---")
        
        # Get monthly data
        self.data['YearMonth'] = self.data['Date'].dt.to_period('M')
        monthly_spending = self.data.groupby('YearMonth')['Amount'].sum()
        
        # Calculate average monthly and project yearly
        avg_monthly = monthly_spending.mean()
        projected_yearly = avg_monthly * 12
        
        # Estimate with confidence interval
        std_monthly = monthly_spending.std()
        upper_bound = (avg_monthly + 2 * std_monthly) * 12
        lower_bound = (avg_monthly - 2 * std_monthly) * 12
        
        yearly_forecast = {
            'Projected Amount': projected_yearly,
            'Upper Bound (95%)': upper_bound,
            'Lower Bound (95%)': lower_bound,
            'Average Monthly': avg_monthly,
            'Std Dev Monthly': std_monthly
        }
        
        logger.info(f"Projected Yearly Spending: ₹{projected_yearly:,.0f}")
        logger.info(f"Range: ₹{lower_bound:,.0f} - ₹{upper_bound:,.0f}")
        
        self.forecasts['yearly'] = yearly_forecast
        return yearly_forecast
    
    def detect_spending_trends(self):
        """
        Detect spending trends (increasing/decreasing).
        
        Returns:
            dict: Trend analysis
        """
        logger.info("\n" + "="*50)
        logger.info("SPENDING TRENDS ANALYSIS")
        logger.info("="*50)
        
        self.data['YearMonth'] = self.data['Date'].dt.to_period('M')
        monthly_spending = self.data.groupby('YearMonth')['Amount'].sum()
        
        # Calculate trend
        X = np.array(range(len(monthly_spending))).reshape(-1, 1)
        y = monthly_spending.values
        
        model = LinearRegression()
        model.fit(X, y)
        
        slope = model.coef_[0]
        trend_direction = "Increasing" if slope > 0 else "Decreasing"
        trend_magnitude = abs(slope)
        
        trends = {
            'Direction': trend_direction,
            'Monthly Change': slope,
            'R-squared': model.score(X, y),
            'Category Trends': {}
        }
        
        logger.info(f"Overall Trend: {trend_direction} (₹{slope:.2f}/month)")
        logger.info(f"Trend Strength: {trends['R-squared']:.2%}")
        
        # Category trends
        logger.info("\n--- Category Trends ---")
        for category in self.data['Category'].unique():
            cat_data = self.data[self.data['Category'] == category]
            cat_monthly = cat_data.groupby(cat_data['Date'].dt.to_period('M'))['Amount'].sum()
            
            if len(cat_monthly) >= 2:
                X_cat = np.array(range(len(cat_monthly))).reshape(-1, 1)
                y_cat = cat_monthly.values
                
                model_cat = LinearRegression()
                model_cat.fit(X_cat, y_cat)
                
                cat_slope = model_cat.coef_[0]
                cat_trend = "📈 Increasing" if cat_slope > 0 else "📉 Decreasing"
                
                trends['Category Trends'][category] = {
                    'Direction': cat_trend,
                    'Monthly Change': cat_slope
                }
                
                logger.info(f"{category}: {cat_trend} (₹{cat_slope:.2f}/month)")
        
        self.forecasts['trends'] = trends
        return trends
    
    def get_forecast_summary(self):
        """
        Get comprehensive forecast summary.
        
        Returns:
            dict: Summary of all forecasts
        """
        logger.info("\n" + "="*50)
        logger.info("FORECAST SUMMARY")
        logger.info("="*50)
        
        summary = {
            'Forecasts Generated': len(self.forecasts),
            'Available Forecasts': list(self.forecasts.keys())
        }
        
        logger.info(f"Generated {summary['Forecasts Generated']} forecasts:")
        for key in summary['Available Forecasts']:
            logger.info(f"  ✓ {key.replace('_', ' ').title()}")
        
        return summary


def forecast_spending(data):
    """
    Convenience function to generate forecasts.
    
    Args:
        data (pd.DataFrame): Expense data
        
    Returns:
        SpendingForecaster: Forecaster object
    """
    forecaster = SpendingForecaster(data)
    forecaster.forecast_monthly_spending(months_ahead=3)
    forecaster.forecast_by_category(months_ahead=3)
    forecaster.forecast_yearly_spending()
    forecaster.detect_spending_trends()
    forecaster.get_forecast_summary()
    return forecaster


if __name__ == "__main__":
    print("Spending Forecasting Module - Ready for import")
