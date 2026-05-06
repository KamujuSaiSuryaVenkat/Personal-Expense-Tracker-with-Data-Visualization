"""
Transaction Categorization Module
Automatically categorizes expenses into predefined categories
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionCategorizer:
    """
    Categorizes transactions based on description and amount.
    
    Attributes:
        category_rules (dict): Mapping of keywords to categories
        default_category (str): Default category for unmatched transactions
    """
    
    def __init__(self):
        """Initialize categorizer with predefined rules."""
        # Define category rules based on keywords
        self.category_rules = {
            'Food & Dining': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food', 
                            'lunch', 'breakfast', 'dinner', 'meal', 'fastfood', 'snack', 
                            'bakery', 'grocery', 'supermarket', 'market', 'fruit', 'milk'],
            
            'Transportation': ['taxi', 'uber', 'cab', 'autorickshaw', 'fuel', 'petrol', 
                             'diesel', 'bus', 'train', 'metro', 'parking', 'toll', 
                             'vehicle', 'bike', 'car', 'travel', 'flight', 'ticket'],
            
            'Entertainment': ['movie', 'cinema', 'game', 'sport', 'concert', 'show', 
                            'netflix', 'spotify', 'music', 'streaming', 'entertainment',
                            'hobby', 'book', 'magazine', 'ticket'],
            
            'Shopping': ['store', 'mall', 'shop', 'clothing', 'dress', 'shoe', 'amazon', 
                        'flipkart', 'clothing', 'apparel', 'fashion', 'retail'],
            
            'Utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'mobile', 
                         'utility', 'bill', 'broadband', 'landline'],
            
            'Health & Medical': ['hospital', 'doctor', 'medicine', 'pharmacy', 'health', 
                               'gym', 'fitness', 'clinic', 'dental', 'medical', 'vaccine',
                               'supplement', 'wellness'],
            
            'Education': ['school', 'college', 'university', 'course', 'training', 'tuition',
                         'books', 'fees', 'education', 'learning', 'class'],
            
            'Subscriptions': ['subscription', 'membership', 'premium', 'plan', 'annual'],
            
            'Personal Care': ['salon', 'haircut', 'spa', 'beauty', 'cosmetic', 'grooming'],
            
            'Other': []  # Default category
        }
        
        self.default_category = 'Other'
    
    def categorize(self, data):
        """
        Categorize all transactions in the dataframe.
        
        Args:
            data (pd.DataFrame): DataFrame with 'Description' column
            
        Returns:
            pd.DataFrame: DataFrame with new 'Category' column
        """
        logger.info("\n" + "="*50)
        logger.info("CATEGORIZING TRANSACTIONS")
        logger.info("="*50)
        
        data = data.copy()
        
        # Apply categorization
        data['Category'] = data['Description'].apply(self._categorize_transaction)
        
        # Display categorization summary
        self._display_categorization_summary(data)
        
        logger.info("✓ Categorization completed")
        return data
    
    def _categorize_transaction(self, description):
        """
        Categorize a single transaction based on its description.
        
        Args:
            description (str): Transaction description
            
        Returns:
            str: Category name
        """
        description_lower = str(description).lower()
        
        # Check each category's keywords
        for category, keywords in self.category_rules.items():
            if category == 'Other':
                continue
            
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        # Return default category if no match found
        return self.default_category
    
    def _display_categorization_summary(self, data):
        """Display categorization summary."""
        logger.info("\n--- Categorization Summary ---")
        
        category_counts = data['Category'].value_counts()
        
        for category, count in category_counts.items():
            percentage = (count / len(data)) * 100
            logger.info(f"{category}: {count} ({percentage:.1f}%)")
    
    def add_custom_rule(self, category, keywords):
        """
        Add custom categorization rule.
        
        Args:
            category (str): Category name
            keywords (list): List of keywords
        """
        if category not in self.category_rules:
            self.category_rules[category] = []
        
        self.category_rules[category].extend(keywords)
        logger.info(f"✓ Added {len(keywords)} keywords to '{category}' category")
    
    def get_category_rules(self):
        """
        Get all category rules.
        
        Returns:
            dict: Category rules
        """
        return self.category_rules
    
    def display_rules(self):
        """Display all categorization rules."""
        logger.info("\n" + "="*50)
        logger.info("CATEGORIZATION RULES")
        logger.info("="*50)
        
        for category, keywords in self.category_rules.items():
            if keywords:  # Only display if keywords exist
                logger.info(f"\n{category}:")
                logger.info(f"  Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")


def categorize_transactions(data):
    """
    Convenience function to categorize transactions.
    
    Args:
        data (pd.DataFrame): Expense data with Description column
        
    Returns:
        pd.DataFrame: Data with Category column added
    """
    categorizer = TransactionCategorizer()
    return categorizer.categorize(data)


if __name__ == "__main__":
    # Example usage
    categorizer = TransactionCategorizer()
    categorizer.display_rules()
    
    # Example data
    sample_descriptions = [
        "Starbucks Coffee",
        "Uber Ride",
        "Netflix Subscription",
        "Amazon Clothing",
        "Electricity Bill"
    ]
    
    print("\n--- Example Categorization ---")
    for desc in sample_descriptions:
        category = categorizer._categorize_transaction(desc)
        print(f"{desc} -> {category}")
