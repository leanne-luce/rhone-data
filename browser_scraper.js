// Enhanced Product Extraction Script for Rhone.com
// This script extracts detailed product information including colors, prices, and sale status
//
// Usage:
// 1. Open a collection page (e.g., https://www.rhone.com/collections/mens-tops)
// 2. Open browser console (F12 or Cmd+Option+I)
// 3. Paste this entire script and press Enter
// 4. Wait for extraction to complete
// 5. JSON file will download automatically

(async function() {
    console.log('🚀 Starting enhanced product extraction...');

    const products = [];
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

    // Determine current page type and category info
    const isHomepage = window.location.pathname === '/';
    const urlPath = window.location.pathname.toLowerCase();

    let category = null;
    let gender = null;

    if (urlPath.includes('mens') || urlPath.includes('/men')) {
        gender = 'Men';
    } else if (urlPath.includes('womens') || urlPath.includes('/women')) {
        gender = 'Women';
    }

    if (urlPath.includes('tops')) category = 'Tops';
    else if (urlPath.includes('bottoms')) category = 'Bottoms';
    else if (urlPath.includes('shorts')) category = 'Shorts';
    else if (urlPath.includes('outerwear')) category = 'Outerwear';
    else if (urlPath.includes('sports-bra')) category = 'Sports Bras';
    else if (urlPath.includes('legging')) category = 'Leggings';

    console.log(`📍 Detected: ${gender || 'Unknown gender'} - ${category || 'Unknown category'}`);

    // Find all product cards
    const productCards = document.querySelectorAll(
        '.product-card, .product-item, [class*="ProductCard"], [class*="product-grid-item"], [data-product-id], .grid-item'
    );

    console.log(`📦 Found ${productCards.length} product cards`);

    productCards.forEach((card, index) => {
        try {
            const product = {
                scraped_at: new Date().toISOString(),
                is_homepage_product: isHomepage,
                category: category,
                gender: gender,
                currency: 'USD'
            };

            // Extract product URL and ID
            const link = card.querySelector('a[href*="/products/"]');
            if (link) {
                product.url = link.href.split('?')[0]; // Remove query params
                const match = product.url.match(/\/products\/([^/?#]+)/);
                if (match) {
                    product.product_id = match[1];
                }
            }

            // Extract product name/title
            const titleSelectors = [
                '.product-card__title',
                '.product-title',
                '[class*="ProductTitle"]',
                '[class*="product-name"]',
                'h2', 'h3', 'h4',
                '.card__heading',
                '[class*="title"]'
            ];

            for (const selector of titleSelectors) {
                const titleEl = card.querySelector(selector);
                if (titleEl && titleEl.textContent.trim()) {
                    product.name = titleEl.textContent.trim();
                    break;
                }
            }

            // Extract pricing information
            const priceContainer = card.querySelector('[class*="price"]');
            if (priceContainer) {
                const priceText = priceContainer.textContent;

                // Look for sale price (usually shown as "Was $XX Now $YY" or "$YY $XX")
                const priceMatches = priceText.match(/\$(\d+(?:\.\d{2})?)/g);

                if (priceMatches && priceMatches.length > 1) {
                    // Multiple prices found - likely on sale
                    const prices = priceMatches.map(p => parseFloat(p.replace('$', '')));
                    product.sale_price = Math.min(...prices);
                    product.price = Math.max(...prices);
                    product.on_sale = true;
                } else if (priceMatches && priceMatches.length === 1) {
                    // Single price - regular price
                    product.price = parseFloat(priceMatches[0].replace('$', ''));
                    product.sale_price = null;
                    product.on_sale = false;
                }

                // Check for sale badge or indicator
                const saleBadge = card.querySelector('[class*="sale"], [class*="Sale"], .badge--sale');
                if (saleBadge) {
                    product.on_sale = true;
                }
            }

            // Extract color options/swatches
            const colors = [];

            // Method 1: Swatch option buttons (like swatch-option--color)
            const swatchButtons = card.querySelectorAll('button[class*="swatch-option"][class*="color"]');
            swatchButtons.forEach(button => {
                const colorName = button.getAttribute('title') ||
                                button.getAttribute('aria-label');
                if (colorName && !colors.includes(colorName)) {
                    colors.push(colorName.trim());
                }
            });

            // Method 2: Color swatches with data attributes
            const colorSwatches = card.querySelectorAll('[class*="color-swatch"], [class*="ColorSwatch"], [data-color], .swatch');
            colorSwatches.forEach(swatch => {
                const colorName = swatch.getAttribute('data-color') ||
                                swatch.getAttribute('title') ||
                                swatch.getAttribute('aria-label');
                if (colorName && !colors.includes(colorName)) {
                    colors.push(colorName.trim());
                }
            });

            // Method 3: Color dropdown or list
            const colorOptions = card.querySelectorAll('option[value*="color"], [class*="variant"] option');
            colorOptions.forEach(option => {
                const colorName = option.textContent.trim();
                if (colorName && colorName.length > 0 && colorName.length < 30 && !colors.includes(colorName)) {
                    colors.push(colorName);
                }
            });

            // Method 4: Check for color in product name (fallback)
            if (colors.length === 0 && product.name) {
                const colorKeywords = [
                    'black', 'white', 'blue', 'red', 'green', 'navy', 'grey', 'gray',
                    'charcoal', 'heather', 'tan', 'khaki', 'olive', 'burgundy',
                    'slate', 'steel', 'forest', 'crimson', 'sage', 'sand'
                ];

                const nameLower = product.name.toLowerCase();
                colorKeywords.forEach(color => {
                    if (nameLower.includes(color)) {
                        colors.push(color.charAt(0).toUpperCase() + color.slice(1));
                    }
                });
            }

            product.colors = [...new Set(colors)]; // Remove duplicates

            // Extract product image
            const img = card.querySelector('img');
            if (img) {
                const imgSrc = img.src || img.getAttribute('data-src') || img.getAttribute('srcset');
                if (imgSrc) {
                    product.images = [imgSrc.split('?')[0]]; // Remove query params
                }
            }

            // Check for best seller badge
            const bestSellerBadge = card.querySelector(
                '[class*="bestseller"], [class*="best-seller"], .badge--bestseller'
            );
            product.is_best_seller = !!bestSellerBadge;

            // Extract SKU if available
            const sku = card.getAttribute('data-product-id') ||
                       card.getAttribute('data-sku') ||
                       product.product_id;
            product.sku = sku;

            // Only add if we have at least a product ID
            if (product.product_id) {
                products.push(product);
                console.log(`✓ [${index + 1}/${productCards.length}] ${product.name || 'Unnamed'} - ${product.colors.length} colors - ${product.on_sale ? '🏷️ ON SALE' : '$' + product.price}`);
            }

        } catch (error) {
            console.warn(`⚠️  Error processing product card ${index}:`, error);
        }
    });

    console.log(`\n✅ Extracted ${products.length} products`);
    console.log(`💰 On sale: ${products.filter(p => p.on_sale).length}`);
    console.log(`🎨 With colors: ${products.filter(p => p.colors && p.colors.length > 0).length}`);

    if (products.length === 0) {
        console.error('❌ No products found! Make sure you\'re on a collection page.');
        alert('No products found. Please make sure you\'re on a collection page like /collections/mens-tops');
        return;
    }

    // Generate filename
    const pageSlug = window.location.pathname.replace(/\//g, '_').replace(/^_/, '') || 'homepage';
    const timestamp = Date.now();
    const filename = `rhone_products_${pageSlug}_${timestamp}.json`;

    // Download as JSON
    const dataStr = JSON.stringify(products, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log(`\n📥 Downloaded: ${filename}`);
    console.log('\n📋 Next steps:');
    console.log('1. Save the file to the data/ directory');
    console.log('2. Repeat for other collection pages');
    console.log('3. Run: python combine_manual_scrapes.py');
    console.log('4. Run: python database/upload_data.py');

    return products;
})();
