from typing import Dict
from datetime import datetime

from .supabase_client import supabase, user_client
from .auth_service import AuthService


class SavedProductDatabase:
    """Per-user saved products; all reads/writes go through the user JWT (RLS)."""

    VALID_LEVELS = {"interested", "maybe", "not_for_me"}

    @staticmethod
    def list_saved(access_token: str) -> Dict:
        try:
            client = user_client(access_token)
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
            client = user_client(access_token)
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

            client = user_client(access_token)
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
            client = user_client(access_token)
            client.table("saved_products").delete().eq("product_id", product_id).execute()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
