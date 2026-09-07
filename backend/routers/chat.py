from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from database import ProductDatabase, ChatHistoryDatabase
from routers.schemas import ChatMessage
from routers.deps import bearer_token, optional_bearer

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/history/{product_id}")
async def get_chat_history(product_id: str, token: str = Depends(bearer_token)):
    result = ChatHistoryDatabase.list_messages(token, product_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("")
async def chat(
    message: ChatMessage,
    token: Optional[str] = Depends(optional_bearer),
):
    """Answer questions about the product."""
    try:
        product = await ProductDatabase.get_product(message.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        from chat_engine import generate_response
        result = generate_response(
            message.product_id,
            message.message,
            message.conversation_history,
        )

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
            "product_id": message.product_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
