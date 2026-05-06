"""
Database Module
Handles SQLite database operations for expense data
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpenseDatabase:
    """
    Manages SQLite database operations for expenses.
    
    Attributes:
        db_path (str): Path to SQLite database file
        connection (sqlite3.Connection): Database connection object
    """
    
    def __init__(self, db_path):
        """
        Initialize database connection.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"✓ Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("✓ Database connection closed")
    
    def create_tables(self):
        """Create necessary database tables."""
        logger.info("\n" + "="*50)
        logger.info("CREATING DATABASE TABLES")
        logger.info("="*50)
        
        try:
            cursor = self.connection.cursor()
            
            # Create expenses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    payment_method TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create category summary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS category_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT UNIQUE NOT NULL,
                    total_amount REAL DEFAULT 0,
                    count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create monthly summary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year_month TEXT UNIQUE NOT NULL,
                    total_expense REAL DEFAULT 0,
                    transaction_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            logger.info("✓ Tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            self.connection.rollback()
            raise
    
    def insert_expenses(self, data):
        """
        Insert expense records into database.
        
        Args:
            data (pd.DataFrame): Expense data to insert
            
        Returns:
            int: Number of records inserted
        """
        logger.info("\n--- Inserting Expense Records ---")
        
        try:
            cursor = self.connection.cursor()
            
            inserted_count = 0
            
            for _, row in data.iterrows():
                cursor.execute('''
                    INSERT INTO expenses (date, description, amount, payment_method, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    str(row['Date']),
                    row['Description'],
                    row['Amount'],
                    row['PaymentMethod'],
                    row.get('Category', 'Other')
                ))
                inserted_count += 1
            
            self.connection.commit()
            logger.info(f"✓ Inserted {inserted_count} records into database")
            
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error inserting records: {str(e)}")
            self.connection.rollback()
            raise
    
    def get_all_expenses(self):
        """
        Retrieve all expenses from database.
        
        Returns:
            pd.DataFrame: All expense records
        """
        try:
            query = "SELECT * FROM expenses ORDER BY date DESC"
            data = pd.read_sql_query(query, self.connection)
            logger.info(f"✓ Retrieved {len(data)} records from database")
            return data
        except Exception as e:
            logger.error(f"Error retrieving expenses: {str(e)}")
            raise
    
    def get_expenses_by_category(self):
        """
        Get summary of expenses by category.
        
        Returns:
            pd.DataFrame: Category-wise summary
        """
        try:
            query = '''
                SELECT category, COUNT(*) as count, SUM(amount) as total
                FROM expenses
                GROUP BY category
                ORDER BY total DESC
            '''
            data = pd.read_sql_query(query, self.connection)
            return data
        except Exception as e:
            logger.error(f"Error retrieving category summary: {str(e)}")
            raise
    
    def get_expenses_by_payment_method(self):
        """
        Get summary of expenses by payment method.
        
        Returns:
            pd.DataFrame: Payment method-wise summary
        """
        try:
            query = '''
                SELECT payment_method, COUNT(*) as count, SUM(amount) as total
                FROM expenses
                GROUP BY payment_method
                ORDER BY total DESC
            '''
            data = pd.read_sql_query(query, self.connection)
            return data
        except Exception as e:
            logger.error(f"Error retrieving payment method summary: {str(e)}")
            raise
    
    def get_expenses_by_month(self):
        """
        Get monthly expense summary.
        
        Returns:
            pd.DataFrame: Monthly summary
        """
        try:
            query = '''
                SELECT 
                    strftime('%Y-%m', date) as month,
                    COUNT(*) as count,
                    SUM(amount) as total
                FROM expenses
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month DESC
            '''
            data = pd.read_sql_query(query, self.connection)
            return data
        except Exception as e:
            logger.error(f"Error retrieving monthly summary: {str(e)}")
            raise
    
    def get_statistics(self):
        """
        Get overall expense statistics.
        
        Returns:
            dict: Statistics summary
        """
        try:
            cursor = self.connection.cursor()
            
            # Total expenses
            cursor.execute("SELECT SUM(amount) FROM expenses")
            total = cursor.fetchone()[0] or 0
            
            # Number of transactions
            cursor.execute("SELECT COUNT(*) FROM expenses")
            count = cursor.fetchone()[0] or 0
            
            # Average transaction
            cursor.execute("SELECT AVG(amount) FROM expenses")
            average = cursor.fetchone()[0] or 0
            
            # Max transaction
            cursor.execute("SELECT MAX(amount) FROM expenses")
            max_amount = cursor.fetchone()[0] or 0
            
            # Date range
            cursor.execute("SELECT MIN(date), MAX(date) FROM expenses")
            result = cursor.fetchone()
            min_date, max_date = result if result else (None, None)
            
            statistics = {
                'Total Expenses': round(total, 2),
                'Transaction Count': count,
                'Average Transaction': round(average, 2),
                'Maximum Transaction': round(max_amount, 2),
                'Date Range': f"{min_date} to {max_date}" if min_date and max_date else "N/A"
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error retrieving statistics: {str(e)}")
            raise
    
    def clear_expenses(self):
        """Clear all expense records from database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM expenses")
            self.connection.commit()
            logger.info("✓ All expense records cleared")
        except Exception as e:
            logger.error(f"Error clearing records: {str(e)}")
            self.connection.rollback()
            raise
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Example usage
    db = ExpenseDatabase("db/expenses.db")
    db.connect()
    db.create_tables()
    db.close()
    
    print("Database initialized successfully!")
