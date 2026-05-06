"""
Machine Learning-Based Categorization Module
Trains and uses ML models for automatic transaction categorization
"""

import pandas as pd
import numpy as np
import logging
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLCategorizer:
    """
    Machine learning-based transaction categorizer.
    Uses TF-IDF + Naive Bayes for category prediction.
    
    Attributes:
        model: Trained Naive Bayes classifier
        vectorizer: TF-IDF vectorizer
        categories: List of category labels
        metrics: Model performance metrics
    """
    
    def __init__(self, model_path=None):
        """
        Initialize ML categorizer.
        
        Args:
            model_path (str): Path to load pre-trained model
        """
        self.model = None
        self.vectorizer = None
        self.categories = None
        self.metrics = {}
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def train(self, data, test_size=0.2, save_path='models/ml_categorizer.pkl'):
        """
        Train ML model on expense data.
        
        Args:
            data (pd.DataFrame): Training data with 'Description' and 'Category' columns
            test_size (float): Test data percentage
            save_path (str): Path to save trained model
        """
        logger.info("\n" + "="*50)
        logger.info("TRAINING ML CATEGORIZER")
        logger.info("="*50)
        
        # Prepare data - convert to lists to avoid sklearn indexing issues
        descriptions = data['Description'].values.tolist()
        categories = data['Category'].values.tolist()
        self.categories = np.unique(categories)
        
        logger.info(f"\nTraining Data:")
        logger.info(f"  Total samples: {len(descriptions)}")
        logger.info(f"  Categories: {list(self.categories)}")
        logger.info(f"  Category distribution:")
        
        for cat in self.categories:
            count = sum(1 for c in categories if c == cat)
            percentage = (count / len(categories)) * 100
            logger.info(f"    {cat}: {count} ({percentage:.1f}%)")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            descriptions, categories, test_size=test_size, random_state=42
        )
        
        logger.info(f"\n--- Training Parameters ---")
        logger.info(f"Training samples: {len(X_train)}")
        logger.info(f"Test samples: {len(X_test)}")
        
        # Vectorize text
        logger.info("\n--- Vectorizing Text (TF-IDF) ---")
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        logger.info(f"Vocabulary size: {len(self.vectorizer.get_feature_names_out())}")
        logger.info(f"Feature vector shape: {X_train_vec.shape}")
        
        # Train model
        logger.info("\n--- Training Naive Bayes Classifier ---")
        self.model = MultinomialNB(alpha=1.0)
        self.model.fit(X_train_vec, y_train)
        
        # Evaluate
        logger.info("\n--- Model Evaluation ---")
        self._evaluate_model(X_train_vec, y_train, X_test_vec, y_test)
        
        # Save model
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        self.save_model(save_path)
        
        logger.info(f"\n✓ Model trained and saved: {save_path}")
    
    def _evaluate_model(self, X_train, y_train, X_test, y_test):
        """Evaluate model performance."""
        
        # Training accuracy
        y_train_pred = self.model.predict(X_train)
        train_acc = accuracy_score(y_train, y_train_pred)
        
        # Test accuracy
        y_test_pred = self.model.predict(X_test)
        test_acc = accuracy_score(y_test, y_test_pred)
        
        # Precision, recall, F1
        precision = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
        
        logger.info(f"Training Accuracy: {train_acc:.2%}")
        logger.info(f"Test Accuracy: {test_acc:.2%}")
        logger.info(f"Precision (weighted): {precision:.2%}")
        logger.info(f"Recall (weighted): {recall:.2%}")
        logger.info(f"F1-Score (weighted): {f1:.2%}")
        
        # Per-category metrics
        logger.info("\n--- Per-Category Performance ---")
        for cat in self.categories:
            cat_mask = y_test == cat
            if np.sum(cat_mask) > 0:
                cat_acc = accuracy_score(y_test[cat_mask], y_test_pred[cat_mask])
                logger.info(f"{cat}: {cat_acc:.2%}")
        
        # Store metrics
        self.metrics = {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def predict(self, descriptions):
        """
        Predict categories for transactions.
        
        Args:
            descriptions (list/pd.Series): Transaction descriptions
            
        Returns:
            np.array: Predicted categories
        """
        if self.model is None or self.vectorizer is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if isinstance(descriptions, pd.Series):
            descriptions = descriptions.values.tolist()
        elif isinstance(descriptions, np.ndarray):
            descriptions = descriptions.tolist()
        
        X_vec = self.vectorizer.transform(descriptions)
        predictions = self.model.predict(X_vec)
        
        return predictions
    
    def predict_with_confidence(self, descriptions):
        """
        Predict categories with confidence scores.
        
        Args:
            descriptions (list/pd.Series): Transaction descriptions
            
        Returns:
            list: Dicts with 'category', 'confidence', 'alternatives'
        """
        if self.model is None or self.vectorizer is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if isinstance(descriptions, pd.Series):
            descriptions = descriptions.values.tolist()
        elif isinstance(descriptions, np.ndarray):
            descriptions = descriptions.tolist()
        
        X_vec = self.vectorizer.transform(descriptions)
        probabilities = self.model.predict_proba(X_vec)
        predictions = self.model.predict(X_vec)
        
        results = []
        for i, description in enumerate(descriptions):
            pred_idx = np.argmax(probabilities[i])
            confidence = probabilities[i][pred_idx]
            
            # Get top 3 alternatives
            top_indices = np.argsort(probabilities[i])[-3:][::-1]
            alternatives = [
                {'category': self.categories[idx], 'confidence': float(probabilities[i][idx])}
                for idx in top_indices if probabilities[i][idx] < confidence
            ]
            
            results.append({
                'description': description,
                'category': predictions[i],
                'confidence': float(confidence),
                'alternatives': alternatives
            })
        
        return results
    
    def save_model(self, path):
        """
        Save trained model to disk.
        
        Args:
            path (str): Save path
        """
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'vectorizer': self.vectorizer,
                'categories': self.categories,
                'metrics': self.metrics
            }, f)
        
        logger.info(f"Model saved: {path}")
    
    def load_model(self, path):
        """
        Load trained model from disk.
        
        Args:
            path (str): Model file path
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.vectorizer = data['vectorizer']
            self.categories = data['categories']
            self.metrics = data['metrics']
        
        logger.info(f"Model loaded: {path}")
    
    def compare_with_keyword_model(self, data, keyword_categories):
        """
        Compare ML model predictions with keyword-based categories.
        
        Args:
            data (pd.DataFrame): Data with 'Description' column
            keyword_categories (pd.Series): Keyword-based category assignments
            
        Returns:
            dict: Comparison results
        """
        logger.info("\n" + "="*50)
        logger.info("COMPARING ML VS KEYWORD-BASED CATEGORIZATION")
        logger.info("="*50)
        
        descriptions = data['Description'].values
        actual_categories = data['Category'].values
        keyword_cats = keyword_categories.values
        
        ml_predictions = self.predict(descriptions)
        
        # Calculate agreement
        agreement = np.sum(ml_predictions == keyword_cats) / len(ml_predictions)
        
        # Calculate accuracy vs actual categories
        ml_accuracy = accuracy_score(actual_categories, ml_predictions)
        keyword_accuracy = accuracy_score(actual_categories, keyword_cats)
        
        logger.info(f"\n--- Model Accuracy ---")
        logger.info(f"ML Model: {ml_accuracy:.2%}")
        logger.info(f"Keyword-Based: {keyword_accuracy:.2%}")
        logger.info(f"ML vs Keyword Agreement: {agreement:.2%}")
        
        # Disagreements
        disagreements = ml_predictions != keyword_cats
        logger.info(f"\n--- Disagreements ---")
        logger.info(f"Total disagreements: {np.sum(disagreements)} ({(np.sum(disagreements)/len(disagreements)*100):.1f}%)")
        
        if np.sum(disagreements) > 0:
            logger.info("\nSample disagreements:")
            disagreement_indices = np.where(disagreements)[0][:5]
            for idx in disagreement_indices:
                logger.info(f"  {descriptions[idx]}")
                logger.info(f"    ML: {ml_predictions[idx]}, Keyword: {keyword_cats[idx]}, Actual: {actual_categories[idx]}")
        
        return {
            'ml_accuracy': ml_accuracy,
            'keyword_accuracy': keyword_accuracy,
            'agreement': agreement,
            'disagreement_count': int(np.sum(disagreements)),
            'disagreement_percentage': float((np.sum(disagreements)/len(disagreements)*100))
        }
    
    def get_top_features(self, category, top_n=10):
        """
        Get top features (words) for a category.
        
        Args:
            category (str): Category name
            top_n (int): Number of top features to return
            
        Returns:
            list: Top features for the category
        """
        if self.model is None or self.vectorizer is None:
            raise ValueError("Model not trained.")
        
        cat_idx = np.where(self.categories == category)[0]
        if len(cat_idx) == 0:
            return []
        
        cat_idx = cat_idx[0]
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get top features for this category
        top_indices = np.argsort(self.model.feature_log_prob_[cat_idx])[-top_n:][::-1]
        
        return [feature_names[i] for i in top_indices]
    
    def display_model_info(self):
        """Display model information."""
        logger.info("\n" + "="*50)
        logger.info("ML CATEGORIZER MODEL INFO")
        logger.info("="*50)
        
        if self.model is None:
            logger.info("No model trained yet")
            return
        
        logger.info(f"\nModel Type: Multinomial Naive Bayes")
        logger.info(f"Number of categories: {len(self.categories)}")
        logger.info(f"Categories: {list(self.categories)}")
        logger.info(f"Vocabulary size: {len(self.vectorizer.get_feature_names_out())}")
        
        logger.info(f"\n--- Model Metrics ---")
        for key, value in self.metrics.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value:.2%}")
        
        logger.info(f"\n--- Top Features by Category ---")
        for category in self.categories[:5]:  # Show first 5 categories
            features = self.get_top_features(category, top_n=5)
            logger.info(f"{category}: {', '.join(features)}")


def train_categorizer(data, save_path='models/ml_categorizer.pkl'):
    """
    Convenience function to train categorizer.
    
    Args:
        data (pd.DataFrame): Training data
        save_path (str): Model save path
    """
    categorizer = MLCategorizer()
    categorizer.train(data, save_path=save_path)
    categorizer.display_model_info()
    return categorizer


if __name__ == "__main__":
    print("ML Categorizer Module - Ready for import")
