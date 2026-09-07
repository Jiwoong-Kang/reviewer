-- Supabase Table Setup
-- Run this SQL in your Supabase SQL Editor

-- Create products table
CREATE TABLE products (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  image TEXT,
  reviews JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_name ON products(name);

-- Enable Row Level Security (RLS)
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for development)
-- WARNING: In production, create more restrictive policies
CREATE POLICY "Allow all operations on products" ON products
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Optional: Create a function to count reviews
CREATE OR REPLACE FUNCTION count_reviews(product_row products)
RETURNS INTEGER AS $$
BEGIN
  RETURN jsonb_array_length(product_row.reviews);
END;
$$ LANGUAGE plpgsql STABLE;

-- Example query to test
-- SELECT id, name, count_reviews(products.*) as review_count FROM products;

