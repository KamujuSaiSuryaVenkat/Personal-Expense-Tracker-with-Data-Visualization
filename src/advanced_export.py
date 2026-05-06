"""
Advanced Export Module
Exports data to formatted Excel files with visualizations
"""

import pandas as pd
import os
import logging
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedExporter:
    """
    Exports expense data to formatted Excel files.
    
    Attributes:
        data (pd.DataFrame): Expense data
        output_dir (str): Output directory
    """
    
    def __init__(self, data, analysis_results=None, output_dir='outputs'):
        """
        Initialize advanced exporter.
        
        Args:
            data (pd.DataFrame): Expense data
            analysis_results (dict): Analysis results
            output_dir (str): Output directory
        """
        self.data = data.copy()
        self.analysis_results = analysis_results or {}
        self.output_dir = output_dir
        
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def export_to_excel(self, filename='expense_report.xlsx'):
        """
        Export complete report to Excel.
        
        Args:
            filename (str): Output filename
        """
        logger.info("\n" + "="*50)
        logger.info("EXPORTING TO EXCEL")
        logger.info("="*50)
        
        output_path = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Summary
            self._create_summary_sheet(writer)
            
            # Sheet 2: All Transactions
            self._create_transactions_sheet(writer)
            
            # Sheet 3: Category Summary
            self._create_category_sheet(writer)
            
            # Sheet 4: Monthly Analysis
            self._create_monthly_sheet(writer)
            
            # Sheet 5: Payment Method
            self._create_payment_sheet(writer)
            
            # Format all sheets
            self._format_workbook(writer.book)
        
        logger.info(f"✓ Saved: {output_path}")
    
    def _create_summary_sheet(self, writer):
        """Create summary sheet."""
        logger.info("  Creating Summary sheet...")
        
        summary_data = {
            'Metric': [
                'Total Expenses',
                'Total Transactions',
                'Average Transaction',
                'Maximum Transaction',
                'Minimum Transaction',
                'Median Transaction',
                'Std Deviation',
                'Date Range Start',
                'Date Range End'
            ],
            'Value': [
                self.data['Amount'].sum(),
                len(self.data),
                self.data['Amount'].mean(),
                self.data['Amount'].max(),
                self.data['Amount'].min(),
                self.data['Amount'].median(),
                self.data['Amount'].std(),
                self.data['Date'].min(),
                self.data['Date'].max()
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    def _create_transactions_sheet(self, writer):
        """Create transactions sheet."""
        logger.info("  Creating Transactions sheet...")
        
        export_data = self.data[['Date', 'Description', 'Amount', 
                                 'PaymentMethod', 'Category']].copy()
        export_data = export_data.sort_values('Date', ascending=False)
        
        export_data.to_excel(writer, sheet_name='Transactions', index=False)
    
    def _create_category_sheet(self, writer):
        """Create category summary sheet."""
        logger.info("  Creating Category Summary sheet...")
        
        category_summary = self.data.groupby('Category').agg({
            'Amount': ['sum', 'count', 'mean', 'min', 'max', 'std']
        }).round(2)
        
        category_summary.columns = ['Total', 'Count', 'Average', 'Min', 'Max', 'Std Dev']
        category_summary = category_summary.sort_values('Total', ascending=False)
        
        # Add percentage
        total = category_summary['Total'].sum()
        category_summary['Percentage'] = (category_summary['Total'] / total * 100).round(2)
        
        category_summary.to_excel(writer, sheet_name='Category Summary')
    
    def _create_monthly_sheet(self, writer):
        """Create monthly analysis sheet."""
        logger.info("  Creating Monthly Analysis sheet...")
        
        self.data['YearMonth'] = pd.to_datetime(self.data['Date']).dt.to_period('M')
        monthly_summary = self.data.groupby('YearMonth').agg({
            'Amount': ['sum', 'count', 'mean', 'min', 'max']
        }).round(2)
        
        monthly_summary.columns = ['Total', 'Count', 'Average', 'Min', 'Max']
        
        monthly_summary.to_excel(writer, sheet_name='Monthly Analysis')
    
    def _create_payment_sheet(self, writer):
        """Create payment method sheet."""
        logger.info("  Creating Payment Method sheet...")
        
        payment_summary = self.data.groupby('PaymentMethod').agg({
            'Amount': ['sum', 'count', 'mean', 'min', 'max']
        }).round(2)
        
        payment_summary.columns = ['Total', 'Count', 'Average', 'Min', 'Max']
        payment_summary = payment_summary.sort_values('Total', ascending=False)
        
        payment_summary.to_excel(writer, sheet_name='Payment Method')
    
    def _format_workbook(self, workbook):
        """Format workbook with colors and styles."""
        logger.info("  Formatting workbook...")
        
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        
        for sheet in workbook.sheetnames:
            ws = workbook[sheet]
            
            # Format header row
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
    
    def export_by_category(self, filename='expenses_by_category.xlsx'):
        """
        Export transactions grouped by category.
        
        Args:
            filename (str): Output filename
        """
        logger.info(f"  Exporting by category: {filename}")
        
        output_path = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for category in self.data['Category'].unique():
                category_data = self.data[self.data['Category'] == category]
                category_data = category_data[['Date', 'Description', 'Amount', 'PaymentMethod']]
                category_data = category_data.sort_values('Date', ascending=False)
                
                # Create sheet name (max 31 chars)
                sheet_name = category[:30] if len(category) <= 31 else category[:27] + '...'
                category_data.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"✓ Saved: {output_path}")
    
    def export_by_payment_method(self, filename='expenses_by_payment.xlsx'):
        """
        Export transactions grouped by payment method.
        
        Args:
            filename (str): Output filename
        """
        logger.info(f"  Exporting by payment method: {filename}")
        
        output_path = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for method in self.data['PaymentMethod'].unique():
                method_data = self.data[self.data['PaymentMethod'] == method]
                method_data = method_data[['Date', 'Description', 'Amount', 'Category']]
                method_data = method_data.sort_values('Date', ascending=False)
                
                method_data.to_excel(writer, sheet_name=method, index=False)
        
        logger.info(f"✓ Saved: {output_path}")
    
    def export_for_tax(self, filename='tax_report.xlsx'):
        """
        Export data formatted for tax purposes.
        
        Args:
            filename (str): Output filename
        """
        logger.info(f"  Exporting tax report: {filename}")
        
        output_path = os.path.join(self.output_dir, filename)
        
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.data['Month'] = self.data['Date'].dt.to_period('M')
        self.data['Year'] = self.data['Date'].dt.year
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Detailed transactions
            tax_data = self.data[['Date', 'Description', 'Amount', 'Category', 'PaymentMethod']]
            tax_data = tax_data.sort_values('Date')
            tax_data.to_excel(writer, sheet_name='Transactions', index=False)
            
            # Sheet 2: Monthly summary by category
            monthly_cat = self.data.groupby(['Month', 'Category'])['Amount'].sum().unstack(fill_value=0)
            monthly_cat.to_excel(writer, sheet_name='Monthly by Category')
            
            # Sheet 3: Annual summary
            annual = self.data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            annual.to_excel(writer, sheet_name='Annual Summary', header=['Amount'])
        
        logger.info(f"✓ Saved: {output_path}")
    
    def export_all(self):
        """Export all available formats."""
        logger.info("\n--- Exporting All Formats ---")
        
        self.export_to_excel('expense_report.xlsx')
        self.export_by_category('expenses_by_category.xlsx')
        self.export_by_payment_method('expenses_by_payment_method.xlsx')
        self.export_for_tax('tax_report.xlsx')
        
        logger.info("\n✓ All export formats completed!")


def export_data(data, analysis_results=None, output_dir='outputs'):
    """
    Convenience function to export data.
    
    Args:
        data (pd.DataFrame): Expense data
        analysis_results (dict): Analysis results
        output_dir (str): Output directory
    """
    exporter = AdvancedExporter(data, analysis_results, output_dir)
    exporter.export_all()


if __name__ == "__main__":
    print("Advanced Export Module - Ready for import")
