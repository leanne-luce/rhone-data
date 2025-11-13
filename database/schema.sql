-- Supabase schema for Rhone product data

-- Drop existing table if it exists (CASCADE will drop dependent views)
DROP TABLE IF EXISTS products CASCADE;

-- Create products table
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    gender TEXT,

    -- Pricing
    price DECIMAL(10, 2),
    sale_price DECIMAL(10, 2),
    on_sale BOOLEAN DEFAULT FALSE,
    currency TEXT DEFAULT 'USD',

    -- Product details
    description TEXT,
    colors JSONB,  -- Array of colors
    sizes JSONB,   -- Array of sizes
    fabrics JSONB, -- Array of fabrics

    -- Ranking
    best_seller_rank INTEGER,
    is_best_seller BOOLEAN DEFAULT FALSE,

    -- Images
    images JSONB,  -- Array of image URLs

    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_homepage_product BOOLEAN DEFAULT FALSE,

    -- Additional fields
    sku TEXT,
    availability TEXT,

    -- Reviews and ratings
    review_rating DECIMAL(3, 2),  -- Average rating (e.g., 4.5)
    review_count INTEGER,         -- Number of reviews

    -- Product badges
    badges JSONB,  -- Array of badges like ["best-seller", "new", "restocked", "sale"]

    -- Brand and competitor analysis
    brand TEXT,    -- Brand name (e.g., "Rhone", "Vuori", "Lululemon")
    competitor_name TEXT,  -- For competitive analysis tracking
    store_url TEXT,
    tags JSONB,    -- Product tags
    vendor TEXT,   -- Vendor/brand name (Shopify-specific)

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_gender ON products(gender);
CREATE INDEX idx_products_best_seller ON products(is_best_seller);
CREATE INDEX idx_products_homepage ON products(is_homepage_product);
CREATE INDEX idx_products_scraped_at ON products(scraped_at DESC);
CREATE INDEX idx_products_review_rating ON products(review_rating DESC);
CREATE INDEX idx_products_review_count ON products(review_count DESC);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_competitor ON products(competitor_name);

-- Create a unique index on the first image URL (to prevent duplicate color variants)
CREATE UNIQUE INDEX idx_products_first_image ON products((images->0));
CREATE INDEX idx_products_product_id ON products(product_id);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create a view for color analysis
CREATE OR REPLACE VIEW color_analysis AS
SELECT
    jsonb_array_elements_text(colors) AS color,
    COUNT(*) AS product_count,
    category,
    gender
FROM products
WHERE colors IS NOT NULL
GROUP BY color, category, gender;

-- Create a view for fabric analysis
CREATE OR REPLACE VIEW fabric_analysis AS
SELECT
    jsonb_array_elements_text(fabrics) AS fabric,
    COUNT(*) AS product_count,
    category,
    gender
FROM products
WHERE fabrics IS NOT NULL
GROUP BY fabric, category, gender;

-- Create a view for best sellers
CREATE OR REPLACE VIEW best_sellers AS
SELECT
    product_id,
    name,
    category,
    gender,
    price,
    sale_price,
    best_seller_rank,
    url
FROM products
WHERE is_best_seller = TRUE
ORDER BY best_seller_rank ASC NULLS LAST, name ASC;

-- Comments
COMMENT ON TABLE products IS 'Stores product data scraped from Rhone.com and competitor sites';
COMMENT ON COLUMN products.colors IS 'JSON array of available color options';
COMMENT ON COLUMN products.sizes IS 'JSON array of available sizes';
COMMENT ON COLUMN products.fabrics IS 'JSON array of fabric materials used';
COMMENT ON COLUMN products.images IS 'JSON array of product image URLs';
COMMENT ON COLUMN products.review_rating IS 'Average customer review rating (0-5 scale)';
COMMENT ON COLUMN products.review_count IS 'Total number of customer reviews';
COMMENT ON COLUMN products.badges IS 'JSON array of product badges (e.g., ["best-seller", "new", "restocked"])';
COMMENT ON COLUMN products.brand IS 'Brand name - primary identifier for filtering (e.g., "Rhone", "Vuori", "Lululemon")';
COMMENT ON COLUMN products.competitor_name IS 'Name of competitor brand (for competitive analysis)';
COMMENT ON COLUMN products.tags IS 'JSON array of product tags from e-commerce platform';
