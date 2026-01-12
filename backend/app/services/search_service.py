"""Azure AI Search service for product catalog."""

import os
import logging
from typing import Optional

from azure.identity.aio import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching product catalog using Azure AI Search."""
    
    def __init__(self):
        self.endpoint = os.getenv("SEARCH_ENDPOINT")
        self.index_name = "products"
        self.client: SearchClient = None
        self._initialized = False
        
        # Mock product data for development
        self._mock_products = [
            {
                "id": "prod-001",
                "name": "Fresh Clean Shampoo",
                "category": "shampoo",
                "price": 12.99,
                "description": "Gentle daily shampoo with aloe vera and tea tree oil. Perfect for all hair types.",
                "ingredients": ["Water", "Sodium Lauryl Sulfate", "Aloe Vera Extract", "Tea Tree Oil", "Vitamin E"],
                "size": "16 oz",
                "benefits": ["Moisturizing", "Scalp-healthy", "Daily use", "Paraben-free"]
            },
            {
                "id": "prod-002",
                "name": "Repair & Restore Shampoo",
                "category": "shampoo",
                "price": 15.99,
                "description": "Intensive repair formula for damaged and color-treated hair with keratin and argan oil.",
                "ingredients": ["Water", "Keratin", "Argan Oil", "Biotin", "Coconut Oil"],
                "size": "16 oz",
                "benefits": ["Repairs damage", "Color-safe", "Strengthening", "Sulfate-free"]
            },
            {
                "id": "prod-003",
                "name": "Ocean Breeze Laundry Detergent",
                "category": "detergent",
                "price": 18.99,
                "description": "Powerful plant-based laundry detergent with ocean-fresh scent. Works in all machines.",
                "ingredients": ["Plant-based surfactants", "Enzymes", "Natural fragrance", "Water softeners"],
                "size": "64 loads",
                "benefits": ["HE compatible", "Plant-based", "Tough on stains", "Fresh scent"]
            },
            {
                "id": "prod-004",
                "name": "Sensitive Skin Laundry Detergent",
                "category": "detergent",
                "price": 21.99,
                "description": "Hypoallergenic formula for sensitive skin. Free of dyes and perfumes.",
                "ingredients": ["Plant-based surfactants", "Enzymes", "Water"],
                "size": "64 loads",
                "benefits": ["Hypoallergenic", "Fragrance-free", "Dermatologist tested", "Baby-safe"]
            },
            {
                "id": "prod-005",
                "name": "Gentle Hand Soap",
                "category": "soap",
                "price": 5.99,
                "description": "Moisturizing hand soap with shea butter and vitamin E. Gentle on hands.",
                "ingredients": ["Water", "Shea Butter", "Vitamin E", "Glycerin", "Natural fragrance"],
                "size": "12 oz",
                "benefits": ["Moisturizing", "Gentle formula", "Pleasant scent", "Refillable"]
            },
            {
                "id": "prod-006",
                "name": "Antibacterial Hand Soap",
                "category": "soap",
                "price": 6.99,
                "description": "Effective antibacterial formula that eliminates 99.9% of germs.",
                "ingredients": ["Water", "Benzalkonium Chloride", "Aloe Vera", "Glycerin"],
                "size": "12 oz",
                "benefits": ["Kills 99.9% of germs", "Non-drying", "Family safe", "Fresh scent"]
            },
            {
                "id": "prod-007",
                "name": "All-Purpose Cleaner",
                "category": "cleaner",
                "price": 8.99,
                "description": "Versatile cleaner for all surfaces. Cuts through grease and grime.",
                "ingredients": ["Water", "Citric Acid", "Plant-based surfactants", "Essential oils"],
                "size": "32 oz",
                "benefits": ["Multi-surface", "Non-toxic", "Streak-free", "Lemon scent"]
            },
            {
                "id": "prod-008",
                "name": "Glass & Mirror Cleaner",
                "category": "cleaner",
                "price": 7.99,
                "description": "Crystal clear finish for glass and mirrors. No streaks or residue.",
                "ingredients": ["Water", "Isopropyl Alcohol", "Ammonia-free formula"],
                "size": "24 oz",
                "benefits": ["Streak-free", "Ammonia-free", "Fast drying", "Safe for tinted windows"]
            },
            {
                "id": "prod-009",
                "name": "Dish Soap - Lemon Fresh",
                "category": "soap",
                "price": 4.99,
                "description": "Powerful grease-cutting dish soap with refreshing lemon scent.",
                "ingredients": ["Water", "Sodium Lauryl Sulfate", "Lemon Extract", "Vitamin E"],
                "size": "24 oz",
                "benefits": ["Cuts grease", "Gentle on hands", "Concentrated formula", "Long-lasting"]
            },
            {
                "id": "prod-010",
                "name": "Bathroom Cleaner",
                "category": "cleaner",
                "price": 9.99,
                "description": "Tough on soap scum and mildew. Safe for all bathroom surfaces.",
                "ingredients": ["Water", "Citric Acid", "Hydrogen Peroxide", "Essential oils"],
                "size": "32 oz",
                "benefits": ["Removes soap scum", "Fights mildew", "Non-abrasive", "Fresh scent"]
            },
            {
                "id": "prod-011",
                "name": "Volumizing Conditioner",
                "category": "shampoo",
                "price": 13.99,
                "description": "Lightweight conditioner that adds volume without weighing hair down.",
                "ingredients": ["Water", "Cetyl Alcohol", "Biotin", "Rice Protein", "Panthenol"],
                "size": "16 oz",
                "benefits": ["Adds volume", "Lightweight", "Detangling", "Color-safe"]
            },
            {
                "id": "prod-012",
                "name": "Fabric Softener - Lavender",
                "category": "detergent",
                "price": 12.99,
                "description": "Plant-based fabric softener with calming lavender scent.",
                "ingredients": ["Water", "Plant-based softening agents", "Lavender essential oil"],
                "size": "48 loads",
                "benefits": ["Softens fabrics", "Reduces static", "Calming scent", "Eco-friendly"]
            },
            {
                "id": "prod-013",
                "name": "Stain Remover Spray",
                "category": "detergent",
                "price": 9.99,
                "description": "Powerful pre-treatment spray for tough stains. Works on most fabrics.",
                "ingredients": ["Water", "Enzymes", "Hydrogen Peroxide", "Surfactants"],
                "size": "22 oz",
                "benefits": ["Removes tough stains", "Safe for colors", "Works in cold water", "No scrubbing needed"]
            },
            {
                "id": "prod-014",
                "name": "Floor Cleaner - Hardwood",
                "category": "cleaner",
                "price": 11.99,
                "description": "Specially formulated for hardwood and laminate floors. No residue.",
                "ingredients": ["Water", "Plant-based cleaners", "Coconut oil", "Natural polish"],
                "size": "32 oz",
                "benefits": ["Safe for hardwood", "No residue", "Natural shine", "Pleasant scent"]
            },
            {
                "id": "prod-015",
                "name": "Body Wash - Coconut",
                "category": "soap",
                "price": 10.99,
                "description": "Luxurious body wash with coconut oil and shea butter for silky smooth skin.",
                "ingredients": ["Water", "Coconut Oil", "Shea Butter", "Glycerin", "Vitamin E"],
                "size": "18 oz",
                "benefits": ["Moisturizing", "Tropical scent", "Gentle cleansing", "Paraben-free"]
            },
            {
                "id": "prod-016",
                "name": "Kitchen Degreaser",
                "category": "cleaner",
                "price": 10.99,
                "description": "Heavy-duty degreaser for kitchen surfaces, ovens, and stovetops.",
                "ingredients": ["Water", "D-Limonene", "Sodium Carbonate", "Plant-based surfactants"],
                "size": "24 oz",
                "benefits": ["Cuts through grease", "Food-safe", "Citrus scent", "Non-toxic"]
            },
            {
                "id": "prod-017",
                "name": "Dandruff Control Shampoo",
                "category": "shampoo",
                "price": 14.99,
                "description": "Clinically proven to control dandruff and soothe itchy scalp.",
                "ingredients": ["Water", "Zinc Pyrithione", "Tea Tree Oil", "Menthol", "Aloe Vera"],
                "size": "16 oz",
                "benefits": ["Controls dandruff", "Soothes scalp", "Cooling sensation", "Daily use"]
            },
            {
                "id": "prod-018",
                "name": "Toilet Bowl Cleaner",
                "category": "cleaner",
                "price": 6.99,
                "description": "Powerful toilet cleaner with angled nozzle for under-rim cleaning.",
                "ingredients": ["Water", "Hydrochloric Acid", "Surfactants", "Fragrance"],
                "size": "24 oz",
                "benefits": ["Removes stains", "Kills germs", "Angled nozzle", "Fresh scent"]
            },
            {
                "id": "prod-019",
                "name": "Laundry Pods - Spring Fresh",
                "category": "detergent",
                "price": 24.99,
                "description": "Convenient laundry pods with 3-in-1 cleaning power.",
                "ingredients": ["Surfactants", "Enzymes", "Stain fighters", "Brighteners"],
                "size": "42 pods",
                "benefits": ["No measuring", "3-in-1 formula", "HE compatible", "Dissolves completely"]
            },
            {
                "id": "prod-020",
                "name": "Foaming Hand Soap Refill",
                "category": "soap",
                "price": 8.99,
                "description": "Economical refill for foaming hand soap dispensers. Makes 3 bottles.",
                "ingredients": ["Water", "Coconut-derived surfactants", "Glycerin", "Essential oils"],
                "size": "32 oz",
                "benefits": ["Economical", "Less plastic waste", "Moisturizing", "Various scents"]
            }
        ]
    
    async def _ensure_initialized(self):
        """Initialize search client if not already done."""
        if self._initialized:
            return
        
        if not self.endpoint:
            logger.warning("SEARCH_ENDPOINT not set, using mock data")
            self._initialized = True
            return
        
        try:
            credential = DefaultAzureCredential()
            self.client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=credential
            )
            self._initialized = True
            logger.info("Search service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Search service: {e}")
            self._initialized = True  # Use mock data
    
    async def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        top: int = 5
    ) -> list:
        """Search products by query and optional category."""
        await self._ensure_initialized()
        
        if self.client:
            try:
                filter_str = f"category eq '{category}'" if category and category != "all" else None
                
                results = await self.client.search(
                    search_text=query,
                    filter=filter_str,
                    top=top,
                    include_total_count=True
                )
                
                products = []
                async for result in results:
                    products.append(dict(result))
                
                return products
            except Exception as e:
                logger.error(f"Search error: {e}")
                return self._search_mock_products(query, category, top)
        else:
            return self._search_mock_products(query, category, top)
    
    def _search_mock_products(
        self,
        query: str,
        category: Optional[str] = None,
        top: int = 5
    ) -> list:
        """Search mock products for development."""
        query_lower = query.lower()
        results = []
        
        for product in self._mock_products:
            # Filter by category if specified
            if category and category != "all":
                if product["category"] != category:
                    continue
            
            # Simple text matching
            searchable = f"{product['name']} {product['description']} {' '.join(product.get('ingredients', []))} {' '.join(product.get('benefits', []))}".lower()
            
            if query_lower in searchable or any(word in searchable for word in query_lower.split()):
                results.append(product)
        
        # If no results, return top products from category or all
        if not results:
            if category and category != "all":
                results = [p for p in self._mock_products if p["category"] == category]
            else:
                results = self._mock_products
        
        return results[:top]
    
    async def get_all_products(self) -> list:
        """Get all products from the catalog."""
        await self._ensure_initialized()
        
        if self.client:
            try:
                results = await self.client.search(
                    search_text="*",
                    top=100
                )
                
                products = []
                async for result in results:
                    products.append(dict(result))
                
                return products
            except Exception as e:
                logger.error(f"Error getting all products: {e}")
                return self._mock_products
        else:
            return self._mock_products
    
    async def get_product_by_id(self, product_id: str) -> Optional[dict]:
        """Get a specific product by ID."""
        await self._ensure_initialized()
        
        if self.client:
            try:
                result = await self.client.get_document(key=product_id)
                return dict(result)
            except:
                return None
        else:
            for product in self._mock_products:
                if product["id"] == product_id:
                    return product
            return None
