import logging
import sys
import os
# Set relative path for EbayAPI class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ebay_api import EbayAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ebay_api_with_keyword_nike_should_return_nike_products(ebay: EbayAPI, query_string: str):
    # Config search params
    query_search_params = {
        "q": query_string,
        "limit": 3
    }

    try:
        ebay_items = ebay.search_items(query_search_params)
        
        if len(ebay_items) == 0:
            logger.warn("No items found from eBay API")

        ebay_items_processed = ebay.process_ebay_items(ebay_items)
        
        try: 
            for item in ebay_items_processed:

                if "nike" not in item["title"].lower():

                    logger.info("Item from eBay API response did not contain Nike in title")
                
        except: 
            logger.warn("Missing or malformed title description from eBay API response")

        logger.info("Response from eBay API contained Nike items")
    

    except:
        logger.warn("Error occured when calling or processing eBay search items")


def main():
    """eBay API Integration Tests"""
    
    # Initialize the eBay API client
    auth_token = "EBAY AUTH TOKEN"
    ebay = EbayAPI(auth_token)

    test_ebay_api_with_keyword_nike_should_return_nike_products(ebay, "nike")


if __name__ == "__main__":
    main() 
