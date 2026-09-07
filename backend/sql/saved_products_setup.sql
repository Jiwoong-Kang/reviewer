-- Saved products + RLS
-- Run this in the Supabase SQL Editor after products table exists.
-- Also enable Email auth in Authentication > Providers (Email).
-- For local testing, consider disabling "Confirm email" under Authentication > Providers > Email.

CREATE TABLE IF NOT EXISTS saved_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  interest_level TEXT NOT NULL CHECK (interest_level IN ('interested', 'maybe', 'not_for_me')),
  personal_note TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (user_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_saved_products_user_id ON saved_products(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_products_product_id ON saved_products(product_id);

CREATE OR REPLACE FUNCTION set_saved_products_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_saved_products_updated_at ON saved_products;
CREATE TRIGGER trg_saved_products_updated_at
  BEFORE UPDATE ON saved_products
  FOR EACH ROW
  EXECUTE PROCEDURE set_saved_products_updated_at();

ALTER TABLE saved_products ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can select own saved products" ON saved_products;
CREATE POLICY "Users can select own saved products"
  ON saved_products FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own saved products" ON saved_products;
CREATE POLICY "Users can insert own saved products"
  ON saved_products FOR INSERT
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own saved products" ON saved_products;
CREATE POLICY "Users can update own saved products"
  ON saved_products FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own saved products" ON saved_products;
CREATE POLICY "Users can delete own saved products"
  ON saved_products FOR DELETE
  USING (auth.uid() = user_id);
