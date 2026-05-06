"""
Main Application Module
Orchestrates the entire expense tracking pipeline
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import DataLoader
from data_cleaning import DataCleaner
from categorize import TransactionCategorizer
from database import ExpenseDatabase
from analysis import ExpenseAnalyzer
from visualization import ExpenseVisualizer
from report import ReportGenerator
from budget_tracker import BudgetTracker
from recurring_detector import RecurringDetector
from anomaly_detector import AnomalyDetector
from forecasting import SpendingForecaster
from advanced_export import AdvancedExporter
from ml_categorizer import MLCategorizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExpenseTrackerApp:
    """
    Main application class that orchestrates the expense tracking pipeline.
    """
    
    def __init__(self, config=None):
        """
        Initialize the expense tracker application.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config or {}
        self.data_file = self.config.get('data_file', 'data/sample_expenses.csv')
        self.db_file = self.config.get('db_file', 'db/expenses.db')
        self.output_dir = self.config.get('output_dir', 'outputs')
        
        self.raw_data = None
        self.cleaned_data = None
        self.categorized_data = None
        self.analysis_results = None
    
    def run(self):
        """
        Execute the complete expense tracking pipeline.
        """
        logger.info("\n" + "="*70)
        logger.info("STARTING PERSONAL EXPENSE TRACKER APPLICATION")
        logger.info("="*70)
        
        try:
            # Step 1: Load data
            self._step_load_data()
            
            # Step 2: Clean data
            self._step_clean_data()
            
            # Step 3: Categorize transactions
            self._step_categorize()
            
            # Step 4: Store in database
            self._step_store_database()
            
            # Step 5: Analyze data
            self._step_analyze()
            
            # Step 6: Budget Tracking
            self._step_budget_analysis()
            
            # Step 7: Recurring Expense Detection
            self._step_recurring_analysis()
            
            # Step 8: Anomaly Detection
            self._step_anomaly_detection()
            
            # Step 9: Spending Forecasting
            self._step_forecast_spending()
            
            # Step 10: ML Categorizer Training
            self._step_train_ml_categorizer()
            
            # Step 11: Generate visualizations
            self._step_visualize()
            
            # Step 12: Advanced Export
            self._step_advanced_export()
            
            # Step 13: Generate reports
            self._step_generate_reports()
            
            # Step 14: Display summary
            self._display_summary()
            
            logger.info("\n" + "="*70)
            logger.info("✓ APPLICATION COMPLETED SUCCESSFULLY!")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"\n✗ APPLICATION FAILED: {str(e)}")
            raise
    
    def _step_load_data(self):
        """Step 1: Load expense data from CSV."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 1: LOADING DATA")
        logger.info("~"*70)
        
        try:
            if not os.path.exists(self.data_file):
                raise FileNotFoundError(f"Data file not found: {self.data_file}")
            
            loader = DataLoader(self.data_file)
            self.raw_data = loader.load_csv()
            loader.display_summary()
            
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise
    
    def _step_clean_data(self):
        """Step 2: Clean and validate data."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 2: CLEANING DATA")
        logger.info("~"*70)
        
        try:
            cleaner = DataCleaner(self.raw_data)
            self.cleaned_data = cleaner.clean()
            cleaner.display_report()
            
        except Exception as e:
            logger.error(f"Failed to clean data: {str(e)}")
            raise
    
    def _step_categorize(self):
        """Step 3: Categorize transactions."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 3: CATEGORIZING TRANSACTIONS")
        logger.info("~"*70)
        
        try:
            categorizer = TransactionCategorizer()
            self.categorized_data = categorizer.categorize(self.cleaned_data)
            
        except Exception as e:
            logger.error(f"Failed to categorize data: {str(e)}")
            raise
    
    def _step_store_database(self):
        """Step 4: Store data in SQLite database."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 4: STORING DATA IN DATABASE")
        logger.info("~"*70)
        
        try:
            # Create db directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_file) if os.path.dirname(self.db_file) else '.', exist_ok=True)
            
            with ExpenseDatabase(self.db_file) as db:
                db.create_tables()
                db.insert_expenses(self.categorized_data)
                
                # Display statistics
                logger.info("\n--- Database Statistics ---")
                stats = db.get_statistics()
                for key, value in stats.items():
                    logger.info(f"{key}: {value}")
            
        except Exception as e:
            logger.error(f"Failed to store data in database: {str(e)}")
            raise
    
    def _step_analyze(self):
        """Step 5: Analyze expense data."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 5: ANALYZING DATA")
        logger.info("~"*70)
        
        try:
            analyzer = ExpenseAnalyzer(self.categorized_data)
            self.analysis_results = analyzer.analyze()
            analyzer.display_summary()
            
        except Exception as e:
            logger.error(f"Failed to analyze data: {str(e)}")
            raise
    
    def _step_budget_analysis(self):
        """Step 6: Budget tracking and analysis."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 6: BUDGET ANALYSIS")
        logger.info("~"*70)
        
        try:
            # Define budget limits (can be customized)
            budgets = {
                'Food & Dining': 10000,
                'Transportation': 8000,
                'Entertainment': 5000,
                'Shopping': 15000,
                'Utilities': 5000,
                'Health & Medical': 3000,
                'Education': 2000,
                'Subscriptions': 2000,
                'Personal Care': 1000,
                'Other': 5000
            }
            
            budget_tracker = BudgetTracker(self.categorized_data, budgets)
            budget_status = budget_tracker.check_budgets()
            budget_tracker.display_alerts()
            
        except Exception as e:
            logger.error(f"Failed in budget analysis: {str(e)}")
            raise
    
    def _step_recurring_analysis(self):
        """Step 7: Recurring expense detection."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 7: RECURRING EXPENSE ANALYSIS")
        logger.info("~"*70)
        
        try:
            recurring_detector = RecurringDetector(self.categorized_data)
            recurring_expenses = recurring_detector.detect_recurring(similarity_threshold=0.9)
            monthly_recurring = recurring_detector.calculate_monthly_recurring()
            yearly_projection = recurring_detector.project_yearly_spending()
            
        except Exception as e:
            logger.error(f"Failed in recurring analysis: {str(e)}")
            raise
    
    def _step_anomaly_detection(self):
        """Step 8: Anomaly and outlier detection."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 8: ANOMALY DETECTION")
        logger.info("~"*70)
        
        try:
            anomaly_detector = AnomalyDetector(self.categorized_data)
            outliers = anomaly_detector.detect_outliers(method='iqr')
            patterns = anomaly_detector.detect_unusual_patterns()
            surges = anomaly_detector.detect_spending_surge(threshold_increase=50)
            suspicious = anomaly_detector.get_suspicious_transactions()
            
        except Exception as e:
            logger.error(f"Failed in anomaly detection: {str(e)}")
            raise
    
    def _step_forecast_spending(self):
        """Step 9: Spending forecasting."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 9: SPENDING FORECASTING")
        logger.info("~"*70)
        
        try:
            forecaster = SpendingForecaster(self.categorized_data)
            monthly_forecast = forecaster.forecast_monthly_spending(months_ahead=3)
            category_forecast = forecaster.forecast_by_category(months_ahead=3)
            yearly_forecast = forecaster.forecast_yearly_spending()
            trends = forecaster.detect_spending_trends()
            
        except Exception as e:
            logger.error(f"Failed in spending forecasting: {str(e)}")
            raise
    
    def _step_train_ml_categorizer(self):
        """Step 10: Train ML categorizer model."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 10: TRAINING ML CATEGORIZER")
        logger.info("~"*70)
        
        try:
            os.makedirs('models', exist_ok=True)
            
            ml_cat = MLCategorizer()
            ml_cat.train(self.categorized_data, save_path='models/ml_categorizer.pkl')
            ml_cat.display_model_info()
            
            # Compare with keyword-based categorization
            logger.info("\n--- ML Model Performance Comparison ---")
            ml_cat.compare_with_keyword_model(self.categorized_data, 
                                             self.categorized_data['Category'])
            
        except Exception as e:
            logger.error(f"Failed in ML categorizer training: {str(e)}")
            raise
    
    def _step_visualize(self):
        """Step 11: Generate visualizations."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 11: GENERATING VISUALIZATIONS")
        logger.info("~"*70)
        
        try:
            visualizer = ExpenseVisualizer(self.categorized_data, self.output_dir)
            visualizer.generate_all_visualizations()
            
        except Exception as e:
            logger.error(f"Failed to generate visualizations: {str(e)}")
            raise
    
    def _step_advanced_export(self):
        """Step 12: Advanced export to Excel."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 12: ADVANCED EXPORT TO EXCEL")
        logger.info("~"*70)
        
        try:
            exporter = AdvancedExporter(self.categorized_data, self.analysis_results, self.output_dir)
            exporter.export_all()
            
        except Exception as e:
            logger.error(f"Failed in advanced export: {str(e)}")
            raise
    
    def _step_generate_reports(self):
        """Step 13: Generate reports."""
        logger.info("\n" + "~"*70)
        logger.info("STEP 13: GENERATING REPORTS")
        logger.info("~"*70)
        
        try:
            generator = ReportGenerator(self.categorized_data, self.analysis_results, self.output_dir)
            generator.generate_all_reports()
            
        except Exception as e:
            logger.error(f"Failed to generate reports: {str(e)}")
            raise
    
    def _display_summary(self):
        """Display final summary."""
        logger.info("\n" + "="*70)
        logger.info("FINAL SUMMARY")
        logger.info("="*70)
        
        logger.info(f"\n✓ Data loaded: {len(self.raw_data)} records")
        logger.info(f"✓ Data cleaned: {len(self.cleaned_data)} records retained")
        logger.info(f"✓ Data categorized: {self.categorized_data['Category'].nunique()} categories")
        logger.info(f"✓ Database saved: {self.db_file}")
        
        logger.info("\n📊 ADVANCED ANALYSIS COMPLETED:")
        logger.info(f"  ✓ Budget Tracking & Alerts")
        logger.info(f"  ✓ Recurring Expense Detection")
        logger.info(f"  ✓ Anomaly Detection & Outliers")
        logger.info(f"  ✓ Spending Forecasting")
        logger.info(f"  ✓ ML Categorizer Trained (TF-IDF + Naive Bayes)")
        logger.info(f"  ✓ Visualizations saved: {self.output_dir}/")
        logger.info(f"  ✓ Reports saved: {self.output_dir}/")
        logger.info(f"  ✓ Excel exports saved: {self.output_dir}/")
        
        logger.info("\n📊 OUTPUT FILES:")
        logger.info(f"  - Database: {self.db_file}")
        logger.info(f"  - ML Model: models/ml_categorizer.pkl")
        logger.info(f"  - Charts: {os.path.join(self.output_dir, '*.png')}")
        logger.info(f"  - Reports: {os.path.join(self.output_dir, '*.txt')}")
        logger.info(f"  - Excel: {os.path.join(self.output_dir, '*.xlsx')}")
        
        logger.info("\n🎯 TO RUN INTERACTIVE DASHBOARD:")
        logger.info(f"  python src/dash_dashboard.py")
        logger.info(f"  - Data: {os.path.join(self.output_dir, '*.csv')}")
        
        logger.info("\n" + "="*70)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Run the advanced expense tracker pipeline and optional dashboard.')
    parser.add_argument('--dashboard', action='store_true', help='Launch the Dash dashboard after pipeline execution')
    parser.add_argument('--data-file', default='data/sample_expenses.csv', help='Path to the input CSV file')
    parser.add_argument('--db-file', default='db/expenses.db', help='Path to the SQLite database file')
    parser.add_argument('--output-dir', default='outputs', help='Directory for output files')
    args = parser.parse_args()

    config = {
        'data_file': args.data_file,
        'db_file': args.db_file,
        'output_dir': args.output_dir
    }
    
    app = ExpenseTrackerApp(config)
    app.run()

    if args.dashboard:
        logger.info("Launching advanced Dash dashboard...")
        dashboard_path = os.path.join(os.getcwd(), 'src', 'dash_dashboard.py')
        os.execv(sys.executable, [sys.executable, dashboard_path])


if __name__ == "__main__":
    main()
