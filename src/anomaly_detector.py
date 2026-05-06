"""
Anomaly Detection Module
Identifies unusual spending patterns and outliers
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detects anomalies and unusual patterns in spending.
    
    Attributes:
        data (pd.DataFrame): Expense data
        anomalies (list): Detected anomalies
    """
    
    def __init__(self, data):
        """
        Initialize anomaly detector.
        
        Args:
            data (pd.DataFrame): Expense data
        """
        self.data = data.copy()
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.anomalies = []
    
    def detect_outliers(self, method='iqr'):
        """
        Detect spending outliers.
        
        Args:
            method (str): Detection method ('iqr' or 'zscore')
            
        Returns:
            list: Detected outliers
        """
        logger.info("\n" + "="*50)
        logger.info("DETECTING SPENDING OUTLIERS")
        logger.info("="*50)
        
        amounts = self.data['Amount'].values
        
        if method == 'iqr':
            Q1 = np.percentile(amounts, 25)
            Q3 = np.percentile(amounts, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = self.data[(self.data['Amount'] < lower_bound) | 
                               (self.data['Amount'] > upper_bound)]
        
        elif method == 'zscore':
            mean = np.mean(amounts)
            std = np.std(amounts)
            z_scores = np.abs((amounts - mean) / std) if std > 0 else 0
            outliers = self.data[z_scores > 2.5]
        
        logger.info(f"\n--- Found {len(outliers)} Outlier Transactions ---")
        
        for _, row in outliers.iterrows():
            anomaly = {
                'Type': 'Outlier',
                'Date': row['Date'],
                'Description': row['Description'],
                'Amount': row['Amount'],
                'Category': row['Category'],
                'Severity': self._calculate_severity(row['Amount'], amounts)
            }
            self.anomalies.append(anomaly)
            
            logger.info(f"  ₹{row['Amount']:.0f} - {row['Description']} ({anomaly['Severity']})")
        
        return outliers
    
    def _calculate_severity(self, amount, all_amounts):
        """
        Calculate severity of anomaly.
        
        Args:
            amount (float): Transaction amount
            all_amounts (array): All amounts
            
        Returns:
            str: Severity level
        """
        percentile = (np.sum(all_amounts <= amount) / len(all_amounts)) * 100
        
        if percentile > 95:
            return "CRITICAL"
        elif percentile > 85:
            return "HIGH"
        elif percentile > 75:
            return "MEDIUM"
        else:
            return "LOW"
    
    def detect_unusual_patterns(self):
        """
        Detect unusual spending patterns.
        
        Returns:
            list: Detected patterns
        """
        logger.info("\n" + "="*50)
        logger.info("DETECTING UNUSUAL PATTERNS")
        logger.info("="*50)
        
        patterns = []
        
        # 1. Unusual category spending
        logger.info("\n--- Category Anomalies ---")
        category_stats = self.data.groupby('Category')['Amount'].agg(['mean', 'std', 'count'])
        
        for category in category_stats.index:
            category_data = self.data[self.data['Category'] == category]
            high_spending = category_data[category_data['Amount'] > 
                                        (category_stats.loc[category, 'mean'] + 
                                         2 * category_stats.loc[category, 'std'])]
            
            if len(high_spending) > 0:
                for _, row in high_spending.iterrows():
                    pattern = f"🚨 Unusual {category} spending: ₹{row['Amount']:.0f}"
                    patterns.append(pattern)
                    logger.warning(f"  {pattern}")
        
        # 2. Daily spending spike
        logger.info("\n--- Daily Spending Spikes ---")
        daily_spending = self.data.groupby(self.data['Date'].dt.date)['Amount'].sum()
        daily_mean = daily_spending.mean()
        daily_std = daily_spending.std()
        
        spikes = daily_spending[daily_spending > (daily_mean + 2 * daily_std)]
        
        for date, amount in spikes.items():
            pattern = f"Daily spending spike on {date}: ₹{amount:.0f}"
            patterns.append(pattern)
            logger.warning(f"  {pattern}")
        
        # 3. Unusual payment method
        logger.info("\n--- Payment Method Anomalies ---")
        payment_stats = self.data.groupby('PaymentMethod')['Amount'].agg(['mean', 'count'])
        
        for _, row in self.data.iterrows():
            method = row['PaymentMethod']
            if method in payment_stats.index:
                method_mean = payment_stats.loc[method, 'mean']
                if row['Amount'] > (method_mean * 3):
                    pattern = f"Unusual {method} transaction: ₹{row['Amount']:.0f}"
                    patterns.append(pattern)
        
        return patterns
    
    def detect_spending_surge(self, threshold_increase=50):
        """
        Detect sudden spending surges.
        
        Args:
            threshold_increase (float): Percentage increase threshold
            
        Returns:
            list: Detected surges
        """
        logger.info(f"\n--- Detecting Spending Surges (>{threshold_increase}% increase) ---")
        
        # Group by month
        self.data['YearMonth'] = self.data['Date'].dt.to_period('M')
        monthly_spending = self.data.groupby('YearMonth')['Amount'].sum()
        
        surges = []
        
        for i in range(1, len(monthly_spending)):
            prev_month = monthly_spending.iloc[i-1]
            curr_month = monthly_spending.iloc[i]
            
            if prev_month > 0:
                increase_pct = ((curr_month - prev_month) / prev_month) * 100
                
                if increase_pct > threshold_increase:
                    surge = {
                        'Month': monthly_spending.index[i],
                        'Previous': prev_month,
                        'Current': curr_month,
                        'Increase': increase_pct
                    }
                    surges.append(surge)
                    
                    logger.warning(f"  {surge['Month']}: +{increase_pct:.1f}% " +
                                 f"(₹{prev_month:.0f} → ₹{curr_month:.0f})")
        
        return surges
    
    def get_suspicious_transactions(self):
        """
        Get all suspicious transactions.
        
        Returns:
            list: Suspicious transactions with reasons
        """
        logger.info("\n" + "="*50)
        logger.info("SUSPICIOUS TRANSACTIONS")
        logger.info("="*50)
        
        suspicious = []
        
        for anomaly in self.anomalies:
            suspicious.append({
                'Date': anomaly['Date'],
                'Description': anomaly['Description'],
                'Amount': anomaly['Amount'],
                'Category': anomaly['Category'],
                'Reason': f"{anomaly['Type']} ({anomaly['Severity']})"
            })
        
        logger.info(f"\nFound {len(suspicious)} suspicious transactions")
        
        for trans in suspicious[:10]:  # Show top 10
            logger.info(f"  {trans['Date'].date()}: ₹{trans['Amount']:.0f} - {trans['Description']}")
        
        return suspicious
    
    def generate_alert_report(self):
        """
        Generate comprehensive alert report.
        
        Returns:
            dict: Alert report
        """
        logger.info("\n" + "="*50)
        logger.info("ANOMALY DETECTION REPORT")
        logger.info("="*50)
        
        report = {
            'Outliers Detected': len([a for a in self.anomalies if a['Type'] == 'Outlier']),
            'Critical Anomalies': len([a for a in self.anomalies if a['Severity'] == 'CRITICAL']),
            'High Severity': len([a for a in self.anomalies if a['Severity'] == 'HIGH']),
            'Medium Severity': len([a for a in self.anomalies if a['Severity'] == 'MEDIUM']),
            'Total Anomalies': len(self.anomalies)
        }
        
        logger.info("\nANOMALY SUMMARY:")
        logger.info(f"  Outliers: {report['Outliers Detected']}")
        logger.info(f"  Critical: {report['Critical Anomalies']}")
        logger.info(f"  High: {report['High Severity']}")
        logger.info(f"  Medium: {report['Medium Severity']}")
        logger.info(f"  Total: {report['Total Anomalies']}")
        
        return report


def detect_anomalies(data):
    """
    Convenience function to detect anomalies.
    
    Args:
        data (pd.DataFrame): Expense data
        
    Returns:
        AnomalyDetector: Detector object
    """
    detector = AnomalyDetector(data)
    detector.detect_outliers()
    detector.detect_unusual_patterns()
    detector.detect_spending_surge()
    detector.get_suspicious_transactions()
    detector.generate_alert_report()
    return detector


if __name__ == "__main__":
    print("Anomaly Detection Module - Ready for import")
