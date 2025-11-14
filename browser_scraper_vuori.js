// Enhanced Product Extraction Script for Vuori Clothing
// This script extracts detailed product information including colors, prices, and sale status
//
// Usage:
// 1. Open a collection page (e.g., https://vuoriclothing.com/collections/mens-outerwear)
// 2. Open browser console (F12 or Cmd+Option+I)
// 3. Paste this entire script and press Enter
// 4. Wait for extraction to complete
// 5. JSON file will download automatically

(async function() {
    console.log('🚀 Starting Vuori product extraction...');

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

    // Vuori-specific category detection
    if (urlPath.includes('tops')) category = 'Tops';
    else if (urlPath.includes('bottoms') || urlPath.includes('pants') || urlPath.includes('joggers')) category = 'Bottoms';
    else if (urlPath.includes('shorts')) category = 'Shorts';
    else if (urlPath.includes('outerwear') || urlPath.includes('jackets') || urlPath.includes('hoodies')) category = 'Outerwear';
    else if (urlPath.includes('bras') || urlPath.includes('sports-bra')) category = 'Sports Bras';
    else if (urlPath.includes('legging')) category = 'Leggings';
    else if (urlPath.includes('accessories')) category = 'Accessories';

    console.log(`📍 Detected: ${gender || 'Unknown gender'} - ${category || 'Unknown category'}`);

    // Wait for products to load (Vuori uses lazy loading)
    console.log('⏳ Waiting for products to load...');
    console.log('💡 Make sure you\'ve scrolled to the bottom of the page!');

    await delay(2000); // Wait 2 seconds for initial load

    // First, let's debug and find what's actually on the page
    console.log('🔍 Debugging: Looking for product elements...');

    // Try to find product links first (most reliable)
    let allLinks = document.querySelectorAll('a[href*="/products/"]');
    console.log(`📎 Found ${allLinks.length} product links`);

    // If no links found, wait a bit more and try again
    if (allLinks.length === 0) {
        console.log('⏳ No links found yet, waiting 3 more seconds...');
        await delay(3000);
        allLinks = document.querySelectorAll('a[href*="/products/"]');
        console.log(`📎 Found ${allLinks.length} product links after waiting`);
    }

    if (allLinks.length > 0) {
        console.log('Sample link:', allLinks[0].href);
        console.log('Parent element classes:', allLinks[0].parentElement?.className);
    }

    // Try multiple selector strategies for Vuori
    let productCards = document.querySelectorAll('[data-testid*="product"], [data-test*="product"]');
    console.log(`Try 1 (data-testid): ${productCards.length} cards`);

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('article, [role="article"], li[class*="product"], li[class*="item"]');
        console.log(`Try 2 (article/li): ${productCards.length} cards`);
    }

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('.product-card, .product-item, .grid-item, [class*="ProductCard"], [class*="ProductItem"]');
        console.log(`Try 3 (common classes): ${productCards.length} cards`);
    }

    if (productCards.length === 0) {
        // Fallback: Find parent containers of product links
        console.log('Try 4: Using product link parents...');
        const linkParents = new Set();
        allLinks.forEach(link => {
            // Get the closest container that might be a product card
            let parent = link.parentElement;
            let depth = 0;
            while (parent && depth < 5) {
                if (parent.tagName === 'LI' || parent.tagName === 'ARTICLE' ||
                    parent.className.toLowerCase().includes('item') ||
                    parent.className.toLowerCase().includes('card') ||
                    parent.className.toLowerCase().includes('product')) {
                    linkParents.add(parent);
                    break;
                }
                parent = parent.parentElement;
                depth++;
            }
        });
        productCards = Array.from(linkParents);
        console.log(`Found ${productCards.length} product containers from links`);
    }

    console.log(`📦 Final count: ${productCards.length} product cards`);

    if (productCards.length === 0) {
        console.error('❌ No products found! Debugging info:');
        console.error(`   Total links on page: ${allLinks.length}`);
        console.error(`   First 3 links:`, Array.from(allLinks).slice(0, 3).map(l => l.href));
        console.error('\n💡 Tips:');
        console.error('   1. Make sure you\'re on /collections/mens-outerwear');
        console.error('   2. Wait for page to fully load');
        console.error('   3. Scroll down to load lazy-loaded products');
        console.error('   4. Check browser console for errors');
        alert('No products found. Check console for debugging info.');
        return;
    }

    productCards.forEach((card, index) => {
        try {
            const product = {
                brand: 'Vuori',
                scraped_at: new Date().toISOString(),
                is_homepage_product: isHomepage,
                category: category,
                gender: gender,
                currency: 'USD',
                colors: [],
                sizes: [],
                fabrics: []
            };

            // Extract product URL and ID
            // Check if the card itself is a link, or find a link inside it
            let link = null;
            if (card.tagName === 'A' && card.href && card.href.includes('/products/')) {
                link = card;
            } else {
                link = card.querySelector('a[href*="/products/"]');
            }

            if (link) {
                const fullUrl = link.href;
                product.url = fullUrl;

                // Extract product ID from URL
                const match = fullUrl.match(/\/products\/([^/?#]+)/);
                if (match) {
                    product.product_id = match[1] + '/';
                }
            }

            // If still no URL, skip this card
            if (!product.url || !product.product_id) {
                return; // Skip this product
            }

            // Extract product name/title - Vuori-specific selectors
            const titleSelectors = [
                '.product-card__title',
                '.product-title',
                '.product-item__title',
                '[class*="ProductCard"] [class*="Title"]',
                '[class*="product-name"]',
                '[class*="ProductName"]',
                'h2', 'h3', 'h4',
                '.card__heading',
                '[class*="title"]:not([class*="price"])'
            ];

            for (const selector of titleSelectors) {
                const titleEl = card.querySelector(selector);
                if (titleEl && titleEl.textContent.trim()) {
                    product.name = titleEl.textContent.trim();
                    break;
                }
            }

            // Extract pricing information - Vuori-specific
            const priceSelectors = [
                '.price',
                '.product-price',
                '[class*="Price"]',
                '[data-price]',
                '.money',
                '[class*="price-item"]'
            ];

            let priceContainer = null;
            for (const selector of priceSelectors) {
                priceContainer = card.querySelector(selector);
                if (priceContainer) break;
            }

            if (priceContainer) {
                const priceText = priceContainer.textContent;

                // Look for sale price patterns
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
                const saleBadge = card.querySelector('[class*="sale"], [class*="Sale"], .badge--sale, [class*="discount"]');
                if (saleBadge) {
                    product.on_sale = true;
                }
            }

            // Extract color options/swatches - Vuori-specific
            const colors = [];

            // Method 1: Look for any buttons (Vuori uses minimal class names)
            const allButtons = card.querySelectorAll('button');
            allButtons.forEach(button => {
                // Check for aria-label, title, or data attributes
                const colorName = button.getAttribute('aria-label') ||
                                button.getAttribute('title') ||
                                button.getAttribute('data-color') ||
                                button.getAttribute('data-color-name');

                // Also check for color in text content if it's short
                const textContent = button.textContent?.trim();
                if (!colorName && textContent && textContent.length < 30 && textContent.length > 0) {
                    // This might be a color name
                    if (!colors.includes(textContent)) {
                        colors.push(textContent);
                    }
                } else if (colorName && !colors.includes(colorName)) {
                    colors.push(colorName.trim());
                }
            });

            // Method 2: Look for divs that might be color swatches
            const swatchDivs = card.querySelectorAll('[class*="swatch"], [class*="color"], [class*="variant"]');
            swatchDivs.forEach(swatch => {
                const colorName = swatch.getAttribute('data-color') ||
                                swatch.getAttribute('aria-label') ||
                                swatch.getAttribute('title') ||
                                swatch.getAttribute('alt');
                if (colorName && !colors.includes(colorName)) {
                    colors.push(colorName.trim());
                }
            });

            // Method 3: Check all images for color info in alt text
            const allImages = card.querySelectorAll('img');
            allImages.forEach(img => {
                const alt = img.getAttribute('alt');
                // Look for patterns like "Product Name - Color Name"
                if (alt && alt.includes('-')) {
                    const parts = alt.split('-').map(p => p.trim());
                    const potentialColor = parts[parts.length - 1];
                    // Only add if it's a reasonable length for a color name
                    if (potentialColor.length < 30 && potentialColor.length > 2 && !colors.includes(potentialColor)) {
                        colors.push(potentialColor);
                    }
                }
            });

            // Method 4: Check for span/div elements with color-related text
            const spans = card.querySelectorAll('span, div');
            spans.forEach(span => {
                const text = span.textContent?.trim();
                // Look for text like "4 colors" or color count indicators
                if (text && text.match(/^\d+\s*(color|colour)s?$/i)) {
                    // Don't add this as a color, but note that colors exist
                    const match = text.match(/^(\d+)/);
                    if (match && colors.length === 0) {
                        // Indicate that colors exist even if we can't extract names
                        product.has_multiple_colors = true;
                        product.color_count = parseInt(match[1]);
                    }
                }
            });

            product.colors = [...new Set(colors)]; // Remove duplicates

            // Extract product images - Vuori-specific
            const images = [];
            const imgSelectors = [
                'img[class*="product"]',
                'img[class*="ProductCard"]',
                '.product-card__image img',
                '.product-image img',
                'img'
            ];

            for (const selector of imgSelectors) {
                const img = card.querySelector(selector);
                if (img) {
                    const imgSrc = img.src || img.getAttribute('data-src') || img.getAttribute('srcset');
                    if (imgSrc && !imgSrc.includes('placeholder')) {
                        // Take first URL if srcset
                        const cleanSrc = imgSrc.split(',')[0].split(' ')[0].split('?')[0];
                        images.push(cleanSrc);
                        break; // Just get first image
                    }
                }
            }

            product.images = images;

            // Check for badges - Vuori-specific
            const badges = [];
            const badgeSelectors = card.querySelectorAll(
                '.badge, [class*="Badge"], [class*="label"], [class*="tag"], .product-flag'
            );

            badgeSelectors.forEach(badge => {
                const badgeText = badge.textContent.trim().toLowerCase();
                if (badgeText) {
                    if (badgeText.includes('best') && badgeText.includes('seller')) {
                        badges.push('best-seller');
                        product.is_best_seller = true;
                    } else if (badgeText.includes('new')) {
                        badges.push('new');
                    } else if (badgeText.includes('sale') || badgeText.includes('discount')) {
                        badges.push('sale');
                        product.on_sale = true;
                    } else if (badgeText.includes('limited')) {
                        badges.push('limited');
                    } else if (badgeText.includes('exclusive')) {
                        badges.push('exclusive');
                    } else if (badgeText.length < 20) {
                        badges.push(badgeText);
                    }
                }
            });

            product.badges = [...new Set(badges)];

            // Extract reviews/ratings if available
            const ratingElem = card.querySelector(
                '[class*="rating"], [class*="star"], [data-rating], [class*="review"]'
            );
            if (ratingElem) {
                const ariaLabel = ratingElem.getAttribute('aria-label');
                if (ariaLabel) {
                    const ratingMatch = ariaLabel.match(/(\d+\.?\d*)\s*(?:star|out of)/i);
                    if (ratingMatch) {
                        product.review_rating = parseFloat(ratingMatch[1]);
                    }
                }

                const reviewCountElem = card.querySelector('[class*="review-count"], [class*="reviews"]');
                if (reviewCountElem) {
                    const countMatch = reviewCountElem.textContent.match(/\(?(\d+)\)?/);
                    if (countMatch) {
                        product.review_count = parseInt(countMatch[1]);
                    }
                }
            }

            // Extract SKU if available
            const sku = card.getAttribute('data-product-id') ||
                       card.getAttribute('data-sku') ||
                       product.product_id;
            product.sku = sku;

            // Only add if we have at least a product ID
            if (product.product_id) {
                products.push(product);
                console.log(`✓ [${index + 1}/${productCards.length}] ${product.name || 'Unnamed'} - ${product.colors.length} colors - ${product.on_sale ? '🏷️ SALE' : (product.price ? '$' + product.price : 'No price')}`);
            }

        } catch (error) {
            console.warn(`⚠️  Error processing product card ${index}:`, error);
        }
    });

    console.log(`\n✅ Extracted ${products.length} products`);
    console.log(`💰 On sale: ${products.filter(p => p.on_sale).length}`);
    console.log(`🎨 With colors: ${products.filter(p => p.colors && p.colors.length > 0).length}`);
    console.log(`⭐ With ratings: ${products.filter(p => p.review_rating).length}`);

    if (products.length === 0) {
        console.error('❌ No products found! Make sure you\'re on a collection page.');
        alert('No products found. Please make sure you\'re on a collection page like /collections/mens-outerwear');
        return;
    }

    // Generate filename
    const pageSlug = window.location.pathname.replace(/\//g, '_').replace(/^_/, '') || 'homepage';
    const timestamp = Date.now();
    const filename = `vuori_products_${pageSlug}_${timestamp}.json`;

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
    console.log('2. Repeat for other collection pages:');
    console.log('   - Men\'s Tops: https://vuoriclothing.com/collections/mens-tops');
    console.log('   - Men\'s Bottoms: https://vuoriclothing.com/collections/mens-bottoms');
    console.log('   - Women\'s Tops: https://vuoriclothing.com/collections/womens-tops');
    console.log('   - Women\'s Bottoms: https://vuoriclothing.com/collections/womens-bottoms');
    console.log('3. Run: python combine_manual_scrapes.py');
    console.log('4. Run: python database/upload_data.py');

    return products;
})();
