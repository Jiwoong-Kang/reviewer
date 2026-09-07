-- User chat history (run in Supabase SQL Editor)
-- Requires: products table, Auth users
-- Also run saved_products_setup.sql if you have not already.

CREATE TABLE IF NOT EXISTS chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  sources JSONB NOT NULL DEFAULT '[]'::jsonb,
  insufficient_evidence BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_user_product
  ON chat_messages(user_id, product_id, created_at);

ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can select own chat messages" ON chat_messages;
CREATE POLICY "Users can select own chat messages"
  ON chat_messages FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own chat messages" ON chat_messages;
CREATE POLICY "Users can insert own chat messages"
  ON chat_messages FOR INSERT
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own chat messages" ON chat_messages;
CREATE POLICY "Users can delete own chat messages"
  ON chat_messages FOR DELETE
  USING (auth.uid() = user_id);
