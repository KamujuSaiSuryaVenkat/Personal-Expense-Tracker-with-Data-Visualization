# 💰 Personal Expense Tracker

A comprehensive Python-based expense tracking system with data analysis, categorization, and visualization capabilities.

## 🎯 Project Overview

This project demonstrates industry-level data engineering and analytics practices by building a complete expense tracking system that:

- ✅ Loads expense data from CSV files
- ✅ Cleans and validates data
- ✅ Automatically categorizes transactions
- ✅ Stores data in SQLite database
- ✅ Performs statistical analysis
- ✅ Generates professional visualizations
- ✅ Creates comprehensive reports
- ✅ Supports an advanced interactive Dash showcase with budgeting, forecasting, anomaly detection, and recurring expense insights

## 🏗️ Project Structure

```
expense-tracker/
│
├── data/                          # Input data folder
│   └── sample_expenses.csv        # Sample expense data
│
├── db/                            # Database folder
│   └── expenses.db                # SQLite database (generated)
│
├── outputs/                       # Output folder
│   ├── category.png               # Category analysis chart
│   ├── monthly.png                # Monthly trend chart
│   ├── payment.png                # Payment method chart
│   ├── category_pie.png           # Category distribution pie chart
│   ├── daily_pattern.png          # Daily spending pattern
│   ├── dashboard.png              # Combined dashboard
│   ├── expense_report.txt         # Text report
│   ├── all_transactions.csv       # All transactions export
│   ├── category_summary.csv       # Category summary
│   ├── payment_method_summary.csv # Payment method summary
│   └── monthly_summary.csv        # Monthly summary
│
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── data_loader.py             # Load CSV data
│   ├── data_cleaning.py           # Clean & validate data
│   ├── categorize.py              # Auto-categorization
│   ├── database.py                # SQLite operations
│   ├── analysis.py                # Statistical analysis
│   ├── visualization.py           # Chart generation
│   └── report.py                  # Report generation
│
├── main.py                        # Main application orchestrator
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### 2. Installation

```bash
# Clone or download the project
cd expense-tracker

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Execute the main pipeline
python main.py
```

The application will:
1. Load data from `data/sample_expenses.csv`
2. Clean and validate the data
3. Categorize all transactions
4. Store data in SQLite database
5. Perform comprehensive analysis
6. Generate visualizations and reports

### 4. Launch the Advanced Dashboard

```bash
# Launch the interactive Dash dashboard after the pipeline
python main.py --dashboard
```

Or run the dashboard directly:

```bash
python src/dash_dashboard.py
```

### 5. View Results

Check the `outputs/` folder for:
- **Charts**: PNG files with visualizations
- **Reports**: Text and CSV files with analysis
- **Database**: SQLite database in `db/` folder

## 📊 Features & Modules

### 1. Data Loader (`src/data_loader.py`)
- Reads CSV files with proper validation
- Ensures all required columns present
- Displays data summary

**Key Classes:**
- `DataLoader`: Loads and validates expense data

### 2. Data Cleaning (`src/data_cleaning.py`)
- Handles missing values
- Converts data types
- Removes duplicates
- Standardizes text
- Validates amounts and dates

**Key Classes:**
- `DataCleaner`: Cleans and preprocesses data

### 3. Categorization (`src/categorize.py`)
- Automatic transaction categorization using keywords
- Pre-configured categories:
  - Food & Dining
  - Transportation
  - Entertainment
  - Shopping
  - Utilities
  - Health & Medical
  - Education
  - Subscriptions
  - Personal Care
  - Other

**Key Classes:**
- `TransactionCategorizer`: Categorizes transactions

### 4. Database (`src/database.py`)
- SQLite database operations
- Creates structured tables
- Performs efficient queries
- Generates summaries

**Key Classes:**
- `ExpenseDatabase`: Manages SQLite operations

### 5. Analysis (`src/analysis.py`)
- Statistical calculations
- Category-wise analysis
- Monthly trends
- Daily patterns
- Payment method analysis
- Top transactions

**Key Classes:**
- `ExpenseAnalyzer`: Performs comprehensive analysis

### 6. Visualization (`src/visualization.py`)
- Bar charts (categories, payment methods)
- Line charts (monthly trends)
- Pie charts (distributions)
- Daily pattern charts
- Combined dashboard

**Key Classes:**
- `ExpenseVisualizer`: Generates visualizations

### 7. Report Generation (`src/report.py`)
- Text reports (comprehensive summary)
- CSV exports (structured data)
- Category summaries
- Payment method reports
- Monthly reports

**Key Classes:**
- `ReportGenerator`: Generates reports

## 📈 Sample Data Format

The `data/sample_expenses.csv` contains:

```
Date,Description,Amount,PaymentMethod
2024-01-01,Starbucks Coffee,150,Card
2024-01-02,Uber Ride,350,UPI
2024-01-03,Grocery Store,2500,Cash
...
```

**Columns:**
- **Date**: Transaction date (YYYY-MM-DD)
- **Description**: Transaction description
- **Amount**: Amount spent (in ₹)
- **PaymentMethod**: Payment method (Card, UPI, Cash, Transfer)

## 🔧 Advanced Usage

### Using Individual Modules

```python
# Load data
from src.data_loader import DataLoader

loader = DataLoader('data/sample_expenses.csv')
data = loader.load_csv()

# Clean data
from src.data_cleaning import DataCleaner

cleaner = DataCleaner(data)
cleaned_data = cleaner.clean()

# Categorize
from src.categorize import TransactionCategorizer

categorizer = TransactionCategorizer()
categorized_data = categorizer.categorize(cleaned_data)

# Analyze
from src.analysis import ExpenseAnalyzer

analyzer = ExpenseAnalyzer(categorized_data)
results = analyzer.analyze()

# Visualize
from src.visualization import ExpenseVisualizer

visualizer = ExpenseVisualizer(categorized_data)
visualizer.generate_all_visualizations()

# Generate reports
from src.report import ReportGenerator

generator = ReportGenerator(categorized_data, results)
generator.generate_all_reports()
```

### Custom Configuration

```python
# In main.py, modify config:
config = {
    'data_file': 'your_data.csv',
    'db_file': 'your_database.db',
    'output_dir': 'your_outputs'
}

app = ExpenseTrackerApp(config)
app.run()
```

### Add Custom Categories

```python
from src.categorize import TransactionCategorizer

categorizer = TransactionCategorizer()
categorizer.add_custom_rule('Investments', ['stocks', 'mutual fund', 'crypto'])
```

## 📊 Output Examples

### Console Output
```
==================================================
STARTING PERSONAL EXPENSE TRACKER APPLICATION
==================================================

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
STEP 1: LOADING DATA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
✓ Successfully loaded 90 records from data/sample_expenses.csv
✓ All required columns present

==================================================
DATA SUMMARY
==================================================
Total Records: 90
Missing Values:
Amount: 0
...
```

### Generated Files
- `expense_report.txt`: Comprehensive text report
- `all_transactions.csv`: All transactions in CSV format
- `category_summary.csv`: Category-wise breakdown
- `payment_method_summary.csv`: Payment method breakdown
- `monthly_summary.csv`: Monthly analysis
- `category.png`: Category spending chart
- `monthly.png`: Monthly trend chart
- `payment.png`: Payment method distribution
- `dashboard.png`: Combined visualization dashboard

## 💡 Key Insights from Analysis

The system automatically generates:
- **Total expenses**: Sum of all transactions
- **Average transaction**: Mean amount per transaction
- **Category breakdown**: Top spending categories
- **Monthly trends**: Spending patterns over time
- **Payment method analysis**: Which payment methods are used most
- **Daily patterns**: When transactions typically occur
- **Top transactions**: Highest individual expenses

## 🎓 Learning Outcomes

This project teaches:

1. **Python Programming**
   - Object-oriented design
   - Module organization
   - Exception handling
   - File I/O operations

2. **Data Analysis**
   - Pandas DataFrame operations
   - Data cleaning techniques
   - Statistical calculations
   - Data aggregation

3. **Databases**
   - SQLite operations
   - Table design
   - Query optimization

4. **Data Visualization**
   - Matplotlib charts
   - Dashboard design
   - Color schemes
   - Data representation

5. **Software Engineering**
   - Code organization
   - Documentation
   - Error handling
   - Industry best practices

## 🚀 Advanced Features

### Budget Tracking (TODO)
```python
# Add budget limits
BUDGET = {
    'Food & Dining': 5000,
    'Transportation': 2000,
    'Entertainment': 1500
}

# Check overspending
```

### Machine Learning Categorization (TODO)
```python
# Use ML for automatic categorization
from sklearn.naive_bayes import MultinomialNB
# Train on description patterns
```

### Streamlit Dashboard (TODO)
```bash
pip install streamlit
streamlit run streamlit_app.py
```

## 🐛 Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution:** Install requirements: `pip install -r requirements.txt`

### File Not Found
```
FileNotFoundError: File not found: data/sample_expenses.csv
```
**Solution:** Ensure the CSV file exists in the `data/` folder

### Database Locked
```
sqlite3.OperationalError: database is locked
```
**Solution:** Close other connections and try again

### Chart Display Issues
If charts don't display, ensure matplotlib backend is configured:
```python
import matplotlib
matplotlib.use('Agg')  # For non-interactive backend
```

## 📋 Data Quality Checks

The system performs:
- ✅ Missing value handling
- ✅ Duplicate removal
- ✅ Data type validation
- ✅ Amount validation (must be > 0)
- ✅ Date format standardization
- ✅ Text normalization

## 🔐 Security Considerations

- No sensitive data is hardcoded
- Database uses local SQLite (suitable for personal use)
- For production, use encrypted databases
- Implement user authentication if sharing data

## 📦 Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **matplotlib**: Data visualization
- **sqlite3**: Database operations (included in Python)
- **datetime**: Date/time handling (included in Python)

## 🤝 Contributing

Suggestions for improvements:
1. Add budget alerts
2. Implement recurring expense tracking
3. Add export to Excel
4. Create web dashboard with Flask/Django
5. Add email notifications
6. Implement user authentication

## 📄 License

This project is open source and available for educational purposes.

---

**Happy Expense Tracking! 💳💰📊**

*Built with ❤️ for learning and portfolio development*
