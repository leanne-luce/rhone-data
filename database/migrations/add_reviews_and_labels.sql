-- Migration: Add review ratings, review counts, and labels to products table
-- Run this in your Supabase SQL Editor if you have an existing products table

-- Add new columns for reviews and ratings
ALTER TABLE products ADD COLUMN IF NOT EXISTS review_rating DECIMAL(3, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER;

-- Add new column for product badges
ALTER TABLE products ADD COLUMN IF NOT EXISTS badges JSONB;

-- Add new columns for brand and competitor analysis (if not already present)
ALTER TABLE products ADD COLUMN IF NOT EXISTS brand TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS competitor_name TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS store_url TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tags JSONB;
ALTER TABLE products ADD COLUMN IF NOT EXISTS vendor TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS original_price DECIMAL(10, 2);

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_products_review_rating ON products(review_rating DESC);
CREATE INDEX IF NOT EXISTS idx_products_review_count ON products(review_count DESC);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_competitor ON products(competitor_name);

-- Add comments
COMMENT ON COLUMN products.review_rating IS 'Average customer review rating (0-5 scale)';
COMMENT ON COLUMN products.review_count IS 'Total number of customer reviews';
COMMENT ON COLUMN products.badges IS 'JSON array of product badges (e.g., ["best-seller", "new", "restocked"])';
COMMENT ON COLUMN products.brand IS 'Brand name - primary identifier for filtering (e.g., "Rhone", "Vuori", "Lululemon")';
COMMENT ON COLUMN products.competitor_name IS 'Name of competitor brand (for competitive analysis)';
COMMENT ON COLUMN products.tags IS 'JSON array of product tags from e-commerce platform';
COMMENT ON COLUMN products.original_price IS 'Original price before sale/discount';

-- Update table comment
COMMENT ON TABLE products IS 'Stores product data scraped from Rhone.com and competitor sites';

-- Optional: Set best_seller flag based on badges
UPDATE products
SET is_best_seller = TRUE
WHERE badges ? 'best-seller' AND (is_best_seller IS NULL OR is_best_seller = FALSE);

SELECT 'Migration completed successfully!' AS status;
