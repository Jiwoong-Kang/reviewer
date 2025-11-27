import os
import json
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Disable tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize ChromaDB client
chroma_client = chromadb.Client(Settings(
    persist_directory="./chroma_db",
    anonymized_telemetry=False
))

# Load embedding model (Korean language support)
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

def get_collection(product_id: str):
    """Get or create a collection for each product."""
    collection_name = f"product_{product_id}"
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except:
        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"description": f"Reviews and description for product {product_id}"}
        )
    return collection

def create_embeddings(product_id: str, description: str, reviews: List[dict]):
    """Create embeddings for product description and reviews, then store in vector DB."""
    collection = get_collection(product_id)
    
    documents = []
    metadatas = []
    ids = []
    
    # Add product description
    documents.append(description)
    metadatas.append({
        "type": "description",
        "product_id": product_id
    })
    ids.append(f"{product_id}_description")
    
    # Add reviews
    for idx, review in enumerate(reviews):
        documents.append(review.get('content', ''))
        metadatas.append({
            "type": "review",
            "product_id": product_id,
            "review_id": review.get('review_id', f"review_{idx}"),
            "rating": str(review.get('rating', 'N/A'))
        })
        ids.append(f"{product_id}_review_{idx}")
    
    # Save to ChromaDB
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✓ Created embeddings for product {product_id}: {len(documents)} documents")
    print(f"  - Description: 1")
    print(f"  - Reviews: {len(reviews)}")
    
    # Verify embeddings were saved
    try:
        test_results = collection.query(query_texts=["test"], n_results=1)
        if test_results['documents']:
            print(f"  - Verification: Embeddings successfully saved ✓")
        else:
            print(f"  - WARNING: Verification failed - no embeddings found!")
    except Exception as e:
        print(f"  - WARNING: Could not verify embeddings: {e}")

def search_similar_content(product_id: str, query: str, top_k: int = 5):
    """Search for reviews/descriptions similar to the query."""
    try:
        collection = get_collection(product_id)
        
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        return {
            "documents": results['documents'][0] if results['documents'] else [],
            "metadatas": results['metadatas'][0] if results['metadatas'] else [],
            "distances": results['distances'][0] if results['distances'] else []
        }
    except Exception as e:
        print(f"Error searching: {e}")
        return {"documents": [], "metadatas": [], "distances": []}

def delete_embeddings(product_id: str):
    """Delete embeddings for a product."""
    try:
        collection_name = f"product_{product_id}"
        chroma_client.delete_collection(name=collection_name)
        print(f"✓ Deleted embeddings for product {product_id}")
    except Exception as e:
        print(f"Error deleting embeddings: {e}")

def get_all_reviews_summary(product_id: str):
    """Get summary of all reviews for a product."""
    try:
        collection = get_collection(product_id)
        results = collection.get()
        
        reviews = []
        description = ""
        
        for doc, meta in zip(results['documents'], results['metadatas']):
            if meta['type'] == 'description':
                description = doc
            elif meta['type'] == 'review':
                reviews.append({
                    "content": doc,
                    "rating": meta.get('rating', 'N/A')
                })
        
        return {
            "description": description,
            "reviews": reviews,
            "total_reviews": len(reviews)
        }
    except Exception as e:
        print(f"Error getting summary: {e}")
        return {"description": "", "reviews": [], "total_reviews": 0}

