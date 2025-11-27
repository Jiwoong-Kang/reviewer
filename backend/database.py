import os
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class ProductDatabase:
    """Product database management using Supabase"""
    
    @staticmethod
    async def create_product(
        product_id: str,
        name: str,
        description: str,
        image: Optional[str] = None,
        reviews: List[Dict] = []
    ) -> Dict:
        """Create a new product"""
        try:
            data = {
                "id": product_id,
                "name": name,
                "description": description,
                "image": image,
                "reviews": reviews,
                "created_at": datetime.now().isoformat()
            }
            
            result = supabase.table("products").insert(data).execute()
            return {"status": "success", "data": result.data}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def get_product(product_id: str) -> Optional[Dict]:
        """Get a product by ID"""
        try:
            result = supabase.table("products").select("*").eq("id", product_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error getting product: {e}")
            return None
    
    @staticmethod
    async def get_all_products() -> List[Dict]:
        """Get all products"""
        try:
            result = supabase.table("products").select("id, name, description, created_at, image, reviews").execute()
            return result.data
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    @staticmethod
    async def update_product(
        product_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image: Optional[str] = None,
        reviews: Optional[List[Dict]] = None
    ) -> Dict:
        """Update a product"""
        try:
            update_data = {}
            if name:
                update_data["name"] = name
            if description:
                update_data["description"] = description
            if image:
                update_data["image"] = image
            if reviews is not None:
                update_data["reviews"] = reviews
            
            result = supabase.table("products").update(update_data).eq("id", product_id).execute()
            return {"status": "success", "data": result.data}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def delete_product(product_id: str) -> Dict:
        """Delete a product"""
        try:
            result = supabase.table("products").delete().eq("id", product_id).execute()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def add_review(product_id: str, review: Dict) -> Dict:
        """Add a review to a product"""
        try:
            # Get existing product
            product = await ProductDatabase.get_product(product_id)
            if not product:
                return {"status": "error", "message": "Product not found"}
            
            # Add review
            reviews = product.get("reviews", [])
            reviews.append(review)
            
            # Update product
            result = supabase.table("products").update({"reviews": reviews}).eq("id", product_id).execute()
            return {"status": "success", "data": result.data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

