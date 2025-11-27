import os
from typing import List, Optional
from openai import OpenAI
from vector_store import search_similar_content, get_all_reviews_summary

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))

def generate_response(
    product_id: str,
    user_message: str,
    conversation_history: Optional[List[dict]] = None
) -> str:
    """
    Generate responses using RAG (Retrieval-Augmented Generation) pattern.
    1. Search for relevant reviews/descriptions related to user's question
    2. Pass retrieved content as context to LLM
    3. Generate natural responses
    """
    
    if conversation_history is None:
        conversation_history = []
    
    # 1. Search for relevant reviews and descriptions
    search_results = search_similar_content(product_id, user_message, top_k=5)
    
    # Debug logging
    print(f"[DEBUG] Search results for '{user_message}':")
    print(f"  - Found {len(search_results['documents'])} documents")
    if search_results['documents']:
        print(f"  - First result type: {search_results['metadatas'][0].get('type', 'unknown')}")
    else:
        print(f"  - WARNING: No documents found! Check embeddings.")
    
    # 2. Build context
    context_parts = []
    
    for doc, meta in zip(search_results['documents'], search_results['metadatas']):
        if meta['type'] == 'description':
            context_parts.append(f"[Product Description]\n{doc}\n")
        elif meta['type'] == 'review':
            rating = meta.get('rating', 'N/A')
            context_parts.append(f"[Review - Rating: {rating}]\n{doc}\n")
    
    context = "\n".join(context_parts)
    
    # Debug: Check if context is empty
    if not context.strip():
        print(f"[WARNING] Empty context for product {product_id}!")
        print(f"[WARNING] This means embeddings might not be created properly.")
    
    # 3. Build prompt
    system_prompt = f"""You are a product review expert assistant.
When users ask about a product, provide accurate and helpful answers based on the provided product descriptions and actual user reviews.

Follow these rules:
1. Answer only based on the provided context (product descriptions and reviews)
2. Present pros and cons mentioned in reviews in a balanced way
3. Respond in friendly and natural language that users can easily understand
4. If information is uncertain, don't guess - say "The reviews lack information on this aspect"
5. Emphasize points commonly mentioned across multiple reviews

Product Information:
{context}
"""
    
    # 4. Build conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add previous conversations (last 5 only)
    for msg in conversation_history[-5:]:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    
    # Add current question
    messages.append({"role": "user", "content": user_message})
    
    # 5. Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo"
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        return answer
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"Sorry, an error occurred while generating the response: {str(e)}"

def generate_product_summary(product_id: str) -> str:
    """Summarize all reviews for a product."""
    
    summary_data = get_all_reviews_summary(product_id)
    
    if summary_data['total_reviews'] == 0:
        return "No reviews available yet."
    
    prompt = f"""Here is a description and {summary_data['total_reviews']} actual user reviews for a product.

Product Description:
{summary_data['description']}

Reviews:
"""
    
    for idx, review in enumerate(summary_data['reviews'][:20], 1):
        prompt += f"\nReview {idx} (Rating: {review['rating']}): {review['content']}\n"
    
    prompt += """

Please write a comprehensive summary including:
1. Main advantages (what users are most satisfied with)
2. Main disadvantages (what users are least satisfied with)
3. Overall evaluation
4. Who should buy this product

Please write in a friendly and easy-to-understand manner."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a product review analysis expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"An error occurred while generating summary: {str(e)}"

