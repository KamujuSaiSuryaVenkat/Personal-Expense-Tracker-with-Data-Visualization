"""
Report Generation Module
Creates text and CSV reports from expense data
"""

import pandas as pd
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates reports from expense data.
    
    Attributes:
        data (pd.DataFrame): Expense data
        analysis_results (dict): Analysis results
        output_dir (str): Directory to save reports
    """
    
    def __init__(self, data, analysis_results=None, output_dir='outputs'):
        """
        Initialize report generator.
        
        Args:
            data (pd.DataFrame): Expense data
            analysis_results (dict): Analysis results
            output_dir (str): Directory to save reports
        """
        self.data = data
        self.analysis_results = analysis_results or {}
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_all_reports(self):
        """Generate all reports."""
        logger.info("\n" + "="*50)
        logger.info("GENERATING REPORTS")
        logger.info("="*50)
        
        self.generate_text_report()
        self.generate_csv_report()
        self.generate_category_report()
        self.generate_payment_method_report()
        self.generate_monthly_report()
        
        logger.info("\n✓ All reports generated successfully!")
    
    def generate_text_report(self):
        """Generate comprehensive text report."""
        logger.info("\n--- Generating Text Report ---")
        
        report_content = []
        report_content.append("="*70)
        report_content.append("PERSONAL EXPENSE TRACKER - COMPREHENSIVE REPORT")
        report_content.append("="*70)
        report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("")
        
        # Overall Summary
        report_content.append("\n" + "─"*70)
        report_content.append("1. OVERALL SUMMARY")
        report_content.append("─"*70)
        
        total_expense = self.data['Amount'].sum()
        total_transactions = len(self.data)
        avg_transaction = self.data['Amount'].mean()
        max_transaction = self.data['Amount'].max()
        min_transaction = self.data['Amount'].min()
        
        report_content.append(f"Total Expenses          : ₹{total_expense:,.2f}")
        report_content.append(f"Total Transactions      : {total_transactions}")
        report_content.append(f"Average per Transaction : ₹{avg_transaction:.2f}")
        report_content.append(f"Maximum Transaction     : ₹{max_transaction:.2f}")
        report_content.append(f"Minimum Transaction     : ₹{min_transaction:.2f}")
        report_content.append(f"Date Range              : {self.data['Date'].min()} to {self.data['Date'].max()}")
        
        # Category Analysis
        report_content.append("\n" + "─"*70)
        report_content.append("2. CATEGORY ANALYSIS")
        report_content.append("─"*70)
        
        category_summary = self.data.groupby('Category').agg({
            'Amount': ['sum', 'count', 'mean']
        }).round(2)
        
        category_summary.columns = ['Total', 'Count', 'Average']
        category_summary = category_summary.sort_values('Total', ascending=False)
        
        report_content.append(f"{'Category':<20} {'Total (₹)':<15} {'Count':<10} {'Average (₹)':<15}")
        report_content.append("─"*70)
        
        for category, row in category_summary.iterrows():
            total = row['Total']
            count = int(row['Count'])
            average = row['Average']
            percentage = (total / total_expense) * 100
            report_content.append(f"{category:<20} {total:>12,.2f}  {count:>8} {average:>12,.2f}  ({percentage:>5.1f}%)")
        
        # Payment Method Analysis
        report_content.append("\n" + "─"*70)
        report_content.append("3. PAYMENT METHOD ANALYSIS")
        report_content.append("─"*70)
        
        payment_summary = self.data.groupby('PaymentMethod').agg({
            'Amount': ['sum', 'count']
        }).round(2)
        
        payment_summary.columns = ['Total', 'Count']
        payment_summary = payment_summary.sort_values('Total', ascending=False)
        
        report_content.append(f"{'Payment Method':<20} {'Total (₹)':<15} {'Count':<10}")
        report_content.append("─"*70)
        
        for method, row in payment_summary.iterrows():
            total = row['Total']
            count = int(row['Count'])
            percentage = (total / total_expense) * 100
            report_content.append(f"{method:<20} {total:>12,.2f}  {count:>8}  ({percentage:>5.1f}%)")
        
        # Monthly Analysis
        report_content.append("\n" + "─"*70)
        report_content.append("4. MONTHLY ANALYSIS")
        report_content.append("─"*70)
        
        self.data['YearMonth'] = pd.to_datetime(self.data['Date']).dt.to_period('M')
        monthly_summary = self.data.groupby('YearMonth').agg({
            'Amount': ['sum', 'count', 'mean']
        }).round(2)
        
        monthly_summary.columns = ['Total', 'Count', 'Average']
        
        report_content.append(f"{'Month':<15} {'Total (₹)':<15} {'Count':<10} {'Average (₹)':<15}")
        report_content.append("─"*70)
        
        for month, row in monthly_summary.iterrows():
            total = row['Total']
            count = int(row['Count'])
            average = row['Average']
            report_content.append(f"{str(month):<15} {total:>12,.2f}  {count:>8} {average:>12,.2f}")
        
        # Top Transactions
        report_content.append("\n" + "─"*70)
        report_content.append("5. TOP 10 TRANSACTIONS")
        report_content.append("─"*70)
        
        top_transactions = self.data.nlargest(10, 'Amount')[['Date', 'Description', 'Amount', 'Category']]
        
        report_content.append(f"{'Date':<12} {'Description':<30} {'Amount (₹)':<15} {'Category':<15}")
        report_content.append("─"*70)
        
        for _, trans in top_transactions.iterrows():
            date = str(trans['Date']).split()[0]
            desc = str(trans['Description'])[:28]
            amount = trans['Amount']
            category = trans['Category']
            report_content.append(f"{date:<12} {desc:<30} {amount:>12,.2f}  {category:<15}")
        
        # Statistics
        report_content.append("\n" + "─"*70)
        report_content.append("6. STATISTICS & INSIGHTS")
        report_content.append("─"*70)
        
        std_dev = self.data['Amount'].std()
        highest_category = category_summary['Total'].idxmax()
        highest_amount = category_summary['Total'].max()
        
        report_content.append(f"Standard Deviation      : ₹{std_dev:.2f}")
        report_content.append(f"Highest Spending        : {highest_category} (₹{highest_amount:,.2f})")
        report_content.append(f"Daily Average           : ₹{total_expense / max((self.data['Date'].max() - self.data['Date'].min()).days, 1):.2f}")
        
        report_content.append("\n" + "="*70)
        report_content.append("END OF REPORT")
        report_content.append("="*70)
        
        # Write to file
        report_text = "\n".join(report_content)
        output_path = os.path.join(self.output_dir, 'expense_report.txt')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"✓ Saved: {output_path}")
        return report_text
    
    def generate_csv_report(self):
        """Generate CSV report of all transactions."""
        logger.info("\n--- Generating CSV Report ---")
        
        output_path = os.path.join(self.output_dir, 'all_transactions.csv')
        
        # Select and arrange columns
        export_data = self.data[['Date', 'Description', 'Amount', 'PaymentMethod', 'Category']].copy()
        export_data = export_data.sort_values('Date', ascending=False)
        
        export_data.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"✓ Saved: {output_path}")
    
    def generate_category_report(self):
        """Generate category-wise detailed report."""
        logger.info("\n--- Generating Category Report ---")
        
        category_summary = self.data.groupby('Category').agg({
            'Amount': ['sum', 'count', 'mean', 'min', 'max', 'std']
        }).round(2)
        
        category_summary.columns = ['Total', 'Count', 'Mean', 'Min', 'Max', 'Std Dev']
        category_summary = category_summary.sort_values('Total', ascending=False)
        
        output_path = os.path.join(self.output_dir, 'category_summary.csv')
        category_summary.to_csv(output_path, encoding='utf-8')
        
        logger.info(f"✓ Saved: {output_path}")
    
    def generate_payment_method_report(self):
        """Generate payment method-wise detailed report."""
        logger.info("\n--- Generating Payment Method Report ---")
        
        payment_summary = self.data.groupby('PaymentMethod').agg({
            'Amount': ['sum', 'count', 'mean', 'min', 'max']
        }).round(2)
        
        payment_summary.columns = ['Total', 'Count', 'Mean', 'Min', 'Max']
        payment_summary = payment_summary.sort_values('Total', ascending=False)
        
        output_path = os.path.join(self.output_dir, 'payment_method_summary.csv')
        payment_summary.to_csv(output_path, encoding='utf-8')
        
        logger.info(f"✓ Saved: {output_path}")
    
    def generate_monthly_report(self):
        """Generate monthly-wise detailed report."""
        logger.info("\n--- Generating Monthly Report ---")
        
        self.data['YearMonth'] = pd.to_datetime(self.data['Date']).dt.to_period('M')
        monthly_summary = self.data.groupby('YearMonth').agg({
            'Amount': ['sum', 'count', 'mean', 'min', 'max']
        }).round(2)
        
        monthly_summary.columns = ['Total', 'Count', 'Mean', 'Min', 'Max']
        
        output_path = os.path.join(self.output_dir, 'monthly_summary.csv')
        monthly_summary.to_csv(output_path, encoding='utf-8')
        
        logger.info(f"✓ Saved: {output_path}")
    
    def get_report_files(self):
        """
        Get list of generated report files.
        
        Returns:
            list: Paths to generated files
        """
        return [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) 
                if f.endswith('.txt') or f.endswith('.csv')]


def generate_reports(data, analysis_results=None, output_dir='outputs'):
    """
    Convenience function to generate all reports.
    
    Args:
        data (pd.DataFrame): Expense data
        analysis_results (dict): Analysis results
        output_dir (str): Directory to save reports
    """
    generator = ReportGenerator(data, analysis_results, output_dir)
    generator.generate_all_reports()


if __name__ == "__main__":
    print("This module is meant to be imported and used within the main pipeline.")
