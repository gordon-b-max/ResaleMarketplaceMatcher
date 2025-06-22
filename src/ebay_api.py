import requests
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EbayAPI:
    
    def __init__(self, auth_token: str):
        """
        EBayAPI class provides functionality to search for items on eBay using their free API.
            Application Name: ResaleMarketplaceMatcher.
            API Documentation: https://developer.ebay.com/api-docs/buy/browse/overview.html
        
        Args:
            auth_token: temp auth token for calling browse prod API endpoint
        """

        self._auth_token = auth_token.replace('\n', '').strip()
        self._headers = {
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US" # Specify the marketplace
        }
        self.ebay_app_name = "ResaleMarketplaceMatcher"
    

    def search_items(self, query_params: object) -> List:
        """
        Request eBay browse API endpoint

        Args:
            query_params: query metadata including product title for search

        Returns:
            Item summaries from eBay API
        """

        base_browse_api_endpoint = "https://api.ebay.com/buy/browse/v1/item_summary/search?"

        try:
            response = requests.get(base_browse_api_endpoint, headers = self._headers, params = query_params)
            response.raise_for_status()

            data = response.json()
            return data.get('itemSummaries', [])

        except Exception as e:
            logger.error(f"Error during eBay API request: {str(e)}")
            raise


    def process_ebay_items(self, resale_items: List) -> List[Dict]:
        """
        Process resale items data from eBay browse API endpoint

        Args:
            resale_items: Response item summaries object from eBay API

        Returns:
            List of resale product details from eBay (title, price, color, size, etc.)
        """

        if len(resale_items) == 0:
            logger.info("No items found from eBay browse API")
            return []
        
        resale_products_data = []

        for item in resale_items:
            product_data = {}
            
            product_data["title"] = item.get('title', 'missing-product-title')
            product_data["ebay_url"] = item.get('itemWebUrl', 'missing-ebay-url')

            # Extract price of product nested in value field
            price_obj = item.get('price', {})
            product_data["price"] = price_obj.get('value', 'missing-price') if isinstance(price_obj, dict) else 'missing-price'
            
            resale_products_data.append(product_data)


        return resale_products_data