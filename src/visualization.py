"""
Visualization Module
Creates charts and visual representations of expense data
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpenseVisualizer:
    """
    Creates visualizations for expense data.
    
    Attributes:
        data (pd.DataFrame): Expense data
        output_dir (str): Directory to save visualizations
    """
    
    def __init__(self, data, output_dir='outputs'):
        """
        Initialize visualizer.
        
        Args:
            data (pd.DataFrame): Expense data
            output_dir (str): Directory to save charts
        """
        self.data = data
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def generate_all_visualizations(self):
        """Generate all visualizations."""
        logger.info("\n" + "="*50)
        logger.info("GENERATING VISUALIZATIONS")
        logger.info("="*50)
        
        self.plot_category_analysis()
        self.plot_monthly_trend()
        self.plot_payment_method()
        self.plot_category_pie_chart()
        self.plot_daily_pattern()
        self.plot_combined_dashboard()
        
        logger.info("\n✓ All visualizations generated successfully!")
    
    def plot_category_analysis(self):
        """Create category-wise expense bar chart."""
        logger.info("\n--- Generating Category Analysis Chart ---")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Group by category
        category_data = self.data.groupby('Category')['Amount'].sum().sort_values(ascending=True)
        
        # Create bar chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_data)))
        category_data.plot(kind='barh', ax=ax, color=colors)
        
        ax.set_xlabel('Amount (₹)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Category', fontsize=12, fontweight='bold')
        ax.set_title('Expense Distribution by Category', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(category_data.values):
            ax.text(v + 100, i, f'₹{v:.0f}', va='center', fontweight='bold')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'category.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def plot_monthly_trend(self):
        """Create monthly spending trend line chart."""
        logger.info("\n--- Generating Monthly Trend Chart ---")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convert date to datetime
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        
        # Group by month
        monthly_data = self.data.groupby(self.data['Date'].dt.to_period('M'))['Amount'].sum()
        monthly_data.index = monthly_data.index.to_timestamp()
        
        # Create line chart
        ax.plot(monthly_data.index, monthly_data.values, marker='o', linewidth=2.5, 
                markersize=8, color='#2E86AB', label='Monthly Expense')
        
        # Fill area under the line
        ax.fill_between(monthly_data.index, monthly_data.values, alpha=0.3, color='#2E86AB')
        
        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount (₹)', fontsize=12, fontweight='bold')
        ax.set_title('Monthly Expense Trend', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format x-axis
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'monthly.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def plot_payment_method(self):
        """Create payment method distribution bar chart."""
        logger.info("\n--- Generating Payment Method Chart ---")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Group by payment method
        payment_data = self.data.groupby('PaymentMethod')['Amount'].sum().sort_values(ascending=False)
        
        # Create bar chart
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(payment_data)))
        bars = ax.bar(range(len(payment_data)), payment_data.values, color=colors, edgecolor='black', linewidth=1.5)
        
        ax.set_xticks(range(len(payment_data)))
        ax.set_xticklabels(payment_data.index, rotation=45, ha='right')
        ax.set_ylabel('Amount (₹)', fontsize=12, fontweight='bold')
        ax.set_title('Expense Distribution by Payment Method', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'₹{height:.0f}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'payment.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def plot_category_pie_chart(self):
        """Create category distribution pie chart."""
        logger.info("\n--- Generating Category Pie Chart ---")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Group by category
        category_data = self.data.groupby('Category')['Amount'].sum()
        
        # Create pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_data)))
        wedges, texts, autotexts = ax.pie(category_data.values, labels=category_data.index, 
                                           autopct='%1.1f%%', colors=colors, startangle=90,
                                           textprops={'fontsize': 10, 'fontweight': 'bold'})
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Expense Breakdown by Category', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'category_pie.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def plot_daily_pattern(self):
        """Create daily spending pattern chart."""
        logger.info("\n--- Generating Daily Pattern Chart ---")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Get day of week
        self.data['DayOfWeek'] = self.data['Date'].dt.day_name()
        
        # Define day order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Group by day
        daily_data = self.data.groupby('DayOfWeek')['Amount'].sum().reindex(
            [d for d in day_order if d in self.data['DayOfWeek'].unique()]
        )
        
        # Create bar chart
        colors = ['#FF6B6B' if day in ['Saturday', 'Sunday'] else '#4ECDC4' for day in daily_data.index]
        daily_data.plot(kind='bar', ax=ax, color=colors, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Day of Week', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount (₹)', fontsize=12, fontweight='bold')
        ax.set_title('Daily Spending Pattern', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticklabels(daily_data.index, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'daily_pattern.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def plot_combined_dashboard(self):
        """Create a combined dashboard with multiple visualizations."""
        logger.info("\n--- Generating Combined Dashboard ---")
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Category bar chart
        ax1 = fig.add_subplot(gs[0, 0])
        category_data = self.data.groupby('Category')['Amount'].sum().sort_values(ascending=False).head(6)
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_data)))
        ax1.barh(range(len(category_data)), category_data.values, color=colors)
        ax1.set_yticks(range(len(category_data)))
        ax1.set_yticklabels(category_data.index)
        ax1.set_xlabel('Amount (₹)', fontweight='bold')
        ax1.set_title('Top 6 Categories', fontweight='bold', fontsize=12)
        ax1.grid(axis='x', alpha=0.3)
        
        # 2. Payment method pie chart
        ax2 = fig.add_subplot(gs[0, 1])
        payment_data = self.data.groupby('PaymentMethod')['Amount'].sum()
        ax2.pie(payment_data.values, labels=payment_data.index, autopct='%1.1f%%',
               colors=plt.cm.Pastel1(np.linspace(0, 1, len(payment_data))))
        ax2.set_title('Payment Method Distribution', fontweight='bold', fontsize=12)
        
        # 3. Monthly trend
        ax3 = fig.add_subplot(gs[1, :])
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        monthly_data = self.data.groupby(self.data['Date'].dt.to_period('M'))['Amount'].sum()
        monthly_data.index = monthly_data.index.to_timestamp()
        ax3.plot(monthly_data.index, monthly_data.values, marker='o', linewidth=2.5, markersize=8, color='#2E86AB')
        ax3.fill_between(monthly_data.index, monthly_data.values, alpha=0.3, color='#2E86AB')
        ax3.set_xlabel('Month', fontweight='bold')
        ax3.set_ylabel('Amount (₹)', fontweight='bold')
        ax3.set_title('Monthly Spending Trend', fontweight='bold', fontsize=12)
        ax3.grid(True, alpha=0.3)
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        # 4. Category pie chart
        ax4 = fig.add_subplot(gs[2, 0])
        category_data = self.data.groupby('Category')['Amount'].sum()
        ax4.pie(category_data.values, labels=category_data.index, autopct='%1.1f%%',
               colors=plt.cm.Set3(np.linspace(0, 1, len(category_data))))
        ax4.set_title('Category Distribution', fontweight='bold', fontsize=12)
        
        # 5. Statistics text box
        ax5 = fig.add_subplot(gs[2, 1])
        ax5.axis('off')
        
        total = self.data['Amount'].sum()
        count = len(self.data)
        avg = self.data['Amount'].mean()
        max_trans = self.data['Amount'].max()
        
        stats_text = f"""
        EXPENSE SUMMARY
        ━━━━━━━━━━━━━━━━━━━
        Total Expenses: ₹{total:.2f}
        Total Transactions: {count}
        Average per Transaction: ₹{avg:.2f}
        Highest Transaction: ₹{max_trans:.2f}
        ━━━━━━━━━━━━━━━━━━━
        """
        
        ax5.text(0.5, 0.5, stats_text, transform=ax5.transAxes, fontsize=11,
                verticalalignment='center', horizontalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                family='monospace', fontweight='bold')
        
        fig.suptitle('Expense Tracker Dashboard', fontsize=16, fontweight='bold', y=0.995)
        
        output_path = os.path.join(self.output_dir, 'dashboard.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def get_output_files(self):
        """
        Get list of generated visualization files.
        
        Returns:
            list: Paths to generated files
        """
        return [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) 
                if f.endswith('.png')]


def visualize_expenses(data, output_dir='outputs'):
    """
    Convenience function to generate visualizations.
    
    Args:
        data (pd.DataFrame): Expense data
        output_dir (str): Directory to save charts
    """
    visualizer = ExpenseVisualizer(data, output_dir)
    visualizer.generate_all_visualizations()


if __name__ == "__main__":
    print("This module is meant to be imported and used within the main pipeline.")
