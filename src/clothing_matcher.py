from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
from typing import List, Dict
import logging
from src.ebay_api import EbayAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data for cleaning
nltk.download('stopwords', quiet=True)

class ClothingMatcher:
    """
    ClothingMatcher class provides functionality to compare clothing items from retail websites
        with similar items on resale platforms.
    """
    
    def __init__(self):
        """
        Initialize ClothingMatcher with necessary NLP components.
        """
        self.ps = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer()
    

    def clean_retail_product_title(self, text: str) -> str:
        """
        Remove stop words from product title prior to calling eBay API
        
        Args:
            text: product title description from retail website
            
        Returns:
            Cleaned retail product text string
        """
        # Split product title into indiviudal words
        words = text.split()
        
        # Lowercased and removed stopwords
        cleaned_words = [
            w.lower() for w in words if w.lower() not in self.stop_words 
        ]
        
        return ' '.join(cleaned_words)
    

    def clean_resale_product_titles(self, items: List[Dict]) -> List[Dict]:
        """
        Clean titles from eBay API response items while preserving additional product data.
        
        Args:
            items: List of dictionaries containing eBay item data (title, price, color, etc.)
            
        Returns:
            List of dictionaries with cleaned titles
        """
        cleaned_items = []
        for item in items:
            cleaned_item = item.copy()
            # Remove stopwords and stem the product titles 
            if 'title' in cleaned_item:
                words = cleaned_item['title'].split()
                cleaned_words = [
                    self.ps.stem(w.lower()) for w in words if w.lower() not in self.stop_words 
                ]
                cleaned_item['title'] = ' '.join(cleaned_words)

            cleaned_items.append(cleaned_item)
        
        return cleaned_items
    

    def calculate_cosine_similarities(self, retail_product_title: str, resale_products: List[Dict]) -> List[Dict]:
        """
        Calculate cosine similarities between retail product title and eBay resale items.
        
        Args:
            retail_product_title: Retail product title description with stop words removed
            resale_products: List of resale products to compare against from eBay API response
            
        Returns:
            List of product data including cosine similarity score
        """
        # Stem retail product title 
        words = retail_product_title.split()
        cleaned_query = ' '.join([
            self.ps.stem(w.lower()) for w in words
        ])
        cleaned_corpus = self.clean_resale_product_titles(resale_products)
        
        
        # Add product title to resale titles for vectorization
        cleaned_corpus_titles = [item["title"] for item in cleaned_corpus]
        all_texts = [cleaned_query] + cleaned_corpus_titles
        
        # Calculate TF-IDF vectors 
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity
        cosine_similarities = (tfidf_matrix * tfidf_matrix.T).toarray()[0][1:]

        # Add cosine similarity scores to product data
        for i, item in enumerate(resale_products):
            item['cosine_similarity'] = cosine_similarities[i]
        
        return resale_products