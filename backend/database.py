import os
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime

# Initialize Supabase client (server-side only; never ship service_role to the browser)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


def _user_client(access_token: str) -> Client:
    """Supabase client scoped to a user JWT so RLS sees auth.uid()."""
    client = create_client(supabase_url, supabase_key)
    client.postgrest.auth(access_token)
    return client


class AuthService:
    """Email/password auth via Supabase Auth."""

    @staticmethod
    def sign_up(email: str, password: str) -> Dict:
        try:
            result = supabase.auth.sign_up({"email": email, "password": password})
            session = result.session
            user = result.user
            if not user:
                return {"status": "error", "message": "Sign up failed"}
            if not session:
                return {
                    "status": "success",
                    "needs_email_confirmation": True,
                    "message": "Check your email to confirm your account before signing in.",
                    "user": {"id": user.id, "email": user.email},
                }
            return {
                "status": "success",
                "needs_email_confirmation": False,
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "user": {"id": user.id, "email": user.email},
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def sign_in(email: str, password: str) -> Dict:
        try:
            result = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            session = result.session
            user = result.user
            if not session or not user:
                return {"status": "error", "message": "Invalid email or password"}
            return {
                "status": "success",
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "user": {"id": user.id, "email": user.email},
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def sign_out(access_token: str) -> Dict:
        try:
            client = _user_client(access_token)
            client.auth.sign_out()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def get_user(access_token: str) -> Optional[Dict]:
        try:
            result = supabase.auth.get_user(access_token)
            user = result.user
            if not user:
                return None
            return {"id": user.id, "email": user.email}
        except Exception as e:
            print(f"Error getting user: {e}")
            return None


class SavedProductDatabase:
    """Per-user saved products; all reads/writes go through the user JWT (RLS)."""

    VALID_LEVELS = {"interested", "maybe", "not_for_me"}

    @staticmethod
    def list_saved(access_token: str) -> Dict:
        try:
            client = _user_client(access_token)
            result = (
                client.table("saved_products")
                .select("*")
                .order("updated_at", desc=True)
                .execute()
            )
            rows = result.data or []
            enriched = []
            for row in rows:
                product = None
                try:
                    prod_result = (
                        supabase.table("products")
                        .select("id, name, image")
                        .eq("id", row["product_id"])
                        .execute()
                    )
                    if prod_result.data:
                        product = prod_result.data[0]
                except Exception:
                    product = None
                enriched.append({
                    **row,
                    "product_name": product["name"] if product else row["product_id"],
                    "product_image": product.get("image") if product else None,
                })
            return {"status": "success", "items": enriched}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def get_saved_for_product(access_token: str, product_id: str) -> Dict:
        try:
            user = AuthService.get_user(access_token)
            if not user:
                return {"status": "error", "message": "Unauthorized"}
            client = _user_client(access_token)
            result = (
                client.table("saved_products")
                .select("*")
                .eq("product_id", product_id)
                .limit(1)
                .execute()
            )
            item = result.data[0] if result.data else None
            return {"status": "success", "item": item}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def upsert_saved(
        access_token: str,
        product_id: str,
        interest_level: str,
        personal_note: str = "",
    ) -> Dict:
        try:
            if interest_level not in SavedProductDatabase.VALID_LEVELS:
                return {
                    "status": "error",
                    "message": "interest_level must be interested, maybe, or not_for_me",
                }
            user = AuthService.get_user(access_token)
            if not user:
                return {"status": "error", "message": "Unauthorized"}

            product = supabase.table("products").select("id").eq("id", product_id).execute()
            if not product.data:
                return {"status": "error", "message": "Product not found"}

            client = _user_client(access_token)
            payload = {
                "user_id": user["id"],
                "product_id": product_id,
                "interest_level": interest_level,
                "personal_note": personal_note or "",
                "updated_at": datetime.now().isoformat(),
            }
            result = (
                client.table("saved_products")
                .upsert(payload, on_conflict="user_id,product_id")
                .execute()
            )
            return {"status": "success", "item": result.data[0] if result.data else payload}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def delete_saved(access_token: str, product_id: str) -> Dict:
        try:
            user = AuthService.get_user(access_token)
            if not user:
                return {"status": "error", "message": "Unauthorized"}
            client = _user_client(access_token)
            client.table("saved_products").delete().eq("product_id", product_id).execute()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

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

