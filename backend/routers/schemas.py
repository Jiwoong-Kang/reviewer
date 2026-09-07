from pydantic import BaseModel, Field
from typing import List, Optional


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
