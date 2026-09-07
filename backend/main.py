from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database
from database import ProductDatabase, AuthService, SavedProductDatabase, ChatHistoryDatabase

app = FastAPI(title="Product Review Chat API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Review(BaseModel):
    review_id: str
    content: str
    rating: Optional[float] = None
    date: Optional[str] = None

class Product(BaseModel):
    product_id: str
    name: str
    description: str
    image: Optional[str] = None
    reviews: List[Review] = []

class ChatMessage(BaseModel):
    product_id: str
    message: str
    conversation_history: Optional[List[dict]] = []

class ProductUpload(BaseModel):
    product_id: str
    name: str
    description: str
    image: Optional[str] = None
    reviews: List[Review]

class AuthSignUp(BaseModel):
    name: str
    username: str
    password: str = Field(min_length=6)

class AuthSignIn(BaseModel):
    username: str
    password: str = Field(min_length=6)

class SavedProductPayload(BaseModel):
    product_id: str
    interest_level: str
    personal_note: Optional[str] = ""


def _bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")
    return token


def _optional_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    if not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    return token or None


@app.get("/")
def root():
    return {"message": "Product Review Chat API", "version": "2.0.0", "database": "Supabase"}


@app.post("/api/auth/signup")
async def signup(creds: AuthSignUp):
    result = AuthService.sign_up(creds.name, creds.username, creds.password)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/api/auth/signin")
async def signin(creds: AuthSignIn):
    result = AuthService.sign_in(creds.username, creds.password)
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@app.post("/api/auth/signout")
async def signout(authorization: Optional[str] = Header(None)):
    token = _bearer_token(authorization)
    result = AuthService.sign_out(token)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/api/auth/me")
async def me(authorization: Optional[str] = Header(None)):
    token = _bearer_token(authorization)
    user = AuthService.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return {"status": "success", "user": user}


@app.get("/api/chat/history/{product_id}")
async def get_chat_history(product_id: str, authorization: Optional[str] = Header(None)):
    token = _bearer_token(authorization)
    result = ChatHistoryDatabase.list_messages(token, product_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/api/saved-products")
async def list_saved_products(authorization: Optional[str] = Header(None)):
    token = _bearer_token(authorization)
    result = SavedProductDatabase.list_saved(token)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/api/saved-products/{product_id}")
async def get_saved_product(product_id: str, authorization: Optional[str] = Header(None)):
    token = _bearer_token(authorization)
    result = SavedProductDatabase.get_saved_for_product(token, product_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/api/saved-products")
async def save_product(payload: SavedProductPayload, authorization: Optional[str] = Header(None)):
    token = _bearer_token(authorization)
    result = SavedProductDatabase.upsert_saved(
        token,
        payload.product_id,
        payload.interest_level,
        payload.personal_note or "",
    )
    if result["status"] == "error":
        status = 404 if result["message"] == "Product not found" else 400
        if result["message"] == "Unauthorized":
            status = 401
        raise HTTPException(status_code=status, detail=result["message"])
    return result


@app.delete("/api/saved-products/{product_id}")
async def unsave_product(product_id: str, authorization: Optional[str] = Header(None)):
    token = _bearer_token(authorization)
    result = SavedProductDatabase.delete_saved(token, product_id)
    if result["status"] == "error":
        status = 401 if result["message"] == "Unauthorized" else 400
        raise HTTPException(status_code=status, detail=result["message"])
    return result


@app.post("/api/products/upload")
async def upload_product(product: ProductUpload):
    """Upload product information and reviews."""
    try:
        # Save product to Supabase
        result = await ProductDatabase.create_product(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            image=product.image,
            reviews=[r.dict() for r in product.reviews]
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        # Create vector embeddings (handled in separate function)
        from vector_store import create_embeddings
        reviews_dict = [r.dict() for r in product.reviews]
        create_embeddings(product.product_id, product.description, reviews_dict)
        
        return {
            "status": "success",
            "product_id": product.product_id,
            "reviews_count": len(product.reviews)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get product information."""
    product = await ProductDatabase.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/products")
async def list_products():
    """Get all products list."""
    products = await ProductDatabase.get_all_products()
    return {
        "products": [
            {
                "product_id": p["id"],
                "name": p["name"],
                "image": p.get("image"),
                "created_at": p.get("created_at"),
                "reviews_count": len(p.get("reviews", []))
            }
            for p in products
        ]
    }

@app.post("/api/chat")
async def chat(message: ChatMessage, authorization: Optional[str] = Header(None)):
    """Answer questions about the product."""
    try:
        # Check if product exists
        product = await ProductDatabase.get_product(message.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Generate response using RAG pattern
        from chat_engine import generate_response
        result = generate_response(
            message.product_id,
            message.message,
            message.conversation_history
        )

        # Persist Q&A for the logged-in user (best-effort)
        token = _optional_bearer(authorization)
        if token:
            ChatHistoryDatabase.add_message(
                token, message.product_id, "user", message.message
            )
            ChatHistoryDatabase.add_message(
                token,
                message.product_id,
                "assistant",
                result["answer"],
                sources=result.get("sources") or [],
                insufficient_evidence=bool(result.get("insufficient_evidence")),
            )
        
        return {
            "status": "success",
            "response": result["answer"],
            "sources": result["sources"],
            "insufficient_evidence": result["insufficient_evidence"],
            "product_id": message.product_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product."""
    product = await ProductDatabase.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete vector embeddings
    from vector_store import delete_embeddings
    delete_embeddings(product_id)
    
    # Delete product from database
    result = await ProductDatabase.delete_product(product_id)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return {"status": "success", "message": "Product deleted"}

@app.post("/api/products/{product_id}/reviews")
async def add_review(product_id: str, review: Review):
    """Add a review to a product."""
    result = await ProductDatabase.add_review(product_id, review.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    # Update vector embeddings
    from vector_store import create_embeddings
    product = await ProductDatabase.get_product(product_id)
    create_embeddings(product_id, product["description"], product.get("reviews", []))
    
    return {"status": "success", "message": "Review added"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
