-- Migration: Remove unique constraint on first image URL
-- This allows products with different variant URLs but same image to coexist
-- Run this in your Supabase SQL Editor

-- Drop the unique index on first image
DROP INDEX IF EXISTS idx_products_first_image;

-- Recreate as a non-unique index for performance
CREATE INDEX IF NOT EXISTS idx_products_first_image ON products((images->0));

-- Add a unique constraint on URL instead (more appropriate for variants)
CREATE UNIQUE INDEX IF NOT EXISTS idx_products_url ON products(url);

SELECT 'Migration completed! Unique constraint moved from image to URL' AS status;
