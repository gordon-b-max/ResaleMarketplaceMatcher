from src.clothing_matcher import ClothingMatcher
from src.ebay_api import EbayAPI
import logging
import pandas as pd
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    

def main():
    """
    Main package execution function for calling and extracting similar resale products from eBay.
    """
    # Replace with your temp eBay auth token to access eBay API
    temp_ebay_auth_token = "EBAY AUTH TOKEN HERE"

    # Replace with product title based on retail product of interest
    retail_product_title = "Women's Nano Puff® Jacket"

    # Initialize EbayAPI class 
    ebay_api_client = EbayAPI(temp_ebay_auth_token)
    
    # Initialize ClothingMatcher class
    clothing_matcher = ClothingMatcher()

    # Begin back-end execution for finding and matching similar resale items
    retail_product_title_cleaned = clothing_matcher.clean_retail_product_title(retail_product_title)    

    # Configure pagination parameters
    max_items = 5000  # Total items to receive
    items_per_request = 200  # Max allowed by eBay API per request
    all_resale_products = []
    
    logger.info(f"Begin fetching items from eBay API for {retail_product_title_cleaned}")
    for offset in range(0, max_items, items_per_request):
        # Modify eBay API search params based on preferences
        query_search_params = {
            "q": retail_product_title_cleaned,
            "limit": items_per_request,
            "offset": offset
        }
        
        logger.info(f"Fetching items {offset + 1} to {offset + items_per_request}")
        resale_similar_products = ebay_api_client.search_items(query_search_params)
        
        if not resale_similar_products:
            logger.info(f"No more items found at offset {offset}")
            break
            
        all_resale_products.extend(resale_similar_products)
        
        # Add a small delay for API calls
        time.sleep(0.1)
    
    # Process results from eBay API response
    resale_similar_products_processed = ebay_api_client.process_ebay_items(all_resale_products)

    # Create cosine similarity scores between retail and resale products
    product_data = clothing_matcher.calculate_cosine_similarities(retail_product_title_cleaned, 
                                                                  resale_similar_products_processed)

    # Adjust threshold to filter for items with more or less similar title descriptions 
    cosine_similarity_threshold = .60

    similar_products = [
        item for item in product_data
        if item.get('cosine_similarity', 0) >= cosine_similarity_threshold
    ]

    # Convert to DataFrame and sort by price ascending
    products = pd.DataFrame(similar_products)
    products['price'] = pd.to_numeric(products['price'], errors = 'coerce')  # Convert price to numeric
    products_sorted = products.sort_values('price', ascending = True)
    
    # Save execution results to CSV
    products_sorted.to_csv("results/similar_resale_products_sorted.csv", index=False)

    logger.info("Finished executing resale marketplace logic")


if __name__ == "__main__":
    main()