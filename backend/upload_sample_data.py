#!/usr/bin/env python3
"""
Upload sample products from sample_products.json to the database via API
"""

import json
import requests
import sys
from pathlib import Path

# API endpoint
API_BASE = "http://localhost:8000"

def load_sample_data():
    """Load sample products from JSON file"""
    json_path = Path(__file__).parent.parent / "sample_products.json"
    
    if not json_path.exists():
        print(f"❌ Error: {json_path} not found")
        sys.exit(1)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('products', [])

def delete_product(product_id):
    """Delete a product if it exists"""
    url = f"{API_BASE}/api/products/{product_id}"
    
    try:
        response = requests.delete(url)
        if response.status_code == 200:
            print(f"   🗑️  Deleted existing product: {product_id}")
            return True
        elif response.status_code == 404:
            # Product doesn't exist, that's fine
            return True
        else:
            print(f"   ⚠️  Warning: Could not delete product: {product_id}")
            return False
    except Exception as e:
        print(f"   ⚠️  Warning: Error deleting product: {e}")
        return False

def upload_product(product_data, auto_delete=True):
    """Upload a single product to the API"""
    url = f"{API_BASE}/api/products/upload"
    
    try:
        response = requests.post(url, json=product_data)
        response.raise_for_status()
        
        result = response.json()
        if result.get('status') == 'success':
            print(f"✅ Successfully uploaded: {product_data['name']}")
            print(f"   Product ID: {product_data['product_id']}")
            print(f"   Reviews: {len(product_data['reviews'])}")
            return True
        else:
            print(f"❌ Failed to upload: {product_data['name']}")
            print(f"   Error: {result}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to API at {API_BASE}")
        print("   Make sure the backend server is running:")
        print("   cd backend && python main.py")
        return False
    except requests.exceptions.HTTPError as e:
        error_text = e.response.text
        
        # Check if it's a duplicate key error
        if "duplicate key" in error_text.lower() and auto_delete:
            print(f"⚠️  Product already exists: {product_data['name']}")
            print(f"   Attempting to delete and re-upload...")
            
            if delete_product(product_data['product_id']):
                # Try uploading again
                print(f"   Retrying upload...")
                return upload_product(product_data, auto_delete=False)
            else:
                print(f"❌ Could not delete existing product")
                return False
        else:
            print(f"❌ HTTP Error: {e}")
            print(f"   Response: {error_text}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("=" * 60)
    print("📦 Product Review Chatbot - Sample Data Uploader")
    print("=" * 60)
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/")
        server_info = response.json()
        print(f"✅ Connected to: {server_info.get('message', 'API Server')}")
        print(f"   Version: {server_info.get('version', 'Unknown')}")
        print(f"   Database: {server_info.get('database', 'Unknown')}")
        print()
    except:
        print(f"❌ Cannot connect to API server at {API_BASE}")
        print()
        print("Please start the backend server first:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  python main.py")
        print()
        sys.exit(1)
    
    # Load sample data
    print("📂 Loading sample products...")
    products = load_sample_data()
    print(f"   Found {len(products)} products to upload")
    print()
    
    # Upload each product
    success_count = 0
    fail_count = 0
    
    for i, product in enumerate(products, 1):
        print(f"[{i}/{len(products)}] Uploading: {product['name']}")
        
        if upload_product(product):
            success_count += 1
        else:
            fail_count += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Upload Summary")
    print("=" * 60)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📦 Total: {len(products)}")
    print()
    
    if success_count > 0:
        print("🎉 Products uploaded successfully!")
        print(f"   Visit http://localhost:3000 to see them in action")
    
    if fail_count > 0:
        print("⚠️  Some uploads failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

