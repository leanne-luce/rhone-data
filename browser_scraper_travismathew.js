// Enhanced Product Extraction Script for Travis Mathew
// This script extracts detailed product information including colors, prices, and sale status
//
// Usage:
// 1. Open a collection page (e.g., https://travismathew.com/collections/womens-bottoms)
// 2. Open browser console (F12 or Cmd+Option+I)
// 3. Paste this entire script and press Enter
// 4. Wait for extraction to complete
// 5. JSON file will download automatically

(async function() {
    console.log('🚀 Starting Travis Mathew product extraction...');

    const products = [];
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

    // Determine current page type and category info
    const isHomepage = window.location.pathname === '/';
    const urlPath = window.location.pathname.toLowerCase();

    console.log(`🔍 Current URL: ${window.location.href}`);
    console.log(`📍 Path: ${urlPath}`);

    let category = null;
    let gender = null;

    // Gender detection - check for womens/women or mens/men in URL path
    // Travis Mathew uses patterns like: /collections/mens-tops, /collections/womens-bottoms
    // IMPORTANT: Check for "womens" BEFORE "mens" to avoid matching "mens" in "womens"
    if (urlPath.includes('womens') || urlPath.includes('-women-') || urlPath.includes('/women/') || urlPath.includes('/women-')) {
        gender = 'Women';
    } else if (urlPath.includes('mens') || urlPath.includes('-men-') || urlPath.includes('/men/') || urlPath.includes('/men-')) {
        gender = 'Men';
    }

    // Travis Mathew-specific category detection
    if (urlPath.includes('tops') || urlPath.includes('shirts') || urlPath.includes('polos') || urlPath.includes('tees')) {
        category = 'Tops';
    } else if (urlPath.includes('pants') || urlPath.includes('joggers') || urlPath.includes('trousers')) {
        category = 'Pants';
    } else if (urlPath.includes('bottoms')) {
        category = 'Bottoms';
    } else if (urlPath.includes('shorts')) {
        category = 'Shorts';
    } else if (urlPath.includes('outerwear') || urlPath.includes('jackets') || urlPath.includes('hoodies') || urlPath.includes('sweaters') || urlPath.includes('vests')) {
        category = 'Outerwear';
    } else if (urlPath.includes('skirt')) {
        category = 'Skirts';
    } else if (urlPath.includes('dress')) {
        category = 'Dresses';
    } else if (urlPath.includes('accessories')) {
        category = 'Accessories';
    } else if (urlPath.includes('hats') || urlPath.includes('headwear')) {
        category = 'Hats';
    } else if (urlPath.includes('bags')) {
        category = 'Bags';
    }

    console.log(`📍 Detected: ${gender || 'Unknown gender'} - ${category || 'Unknown category'}`);

    // Wait for products to load (Travis Mathew uses lazy loading)
    console.log('⏳ Waiting for products to load...');
    console.log('🔄 Auto-scrolling to load all products...');

    // Auto-scroll to load all lazy-loaded products
    let lastHeight = document.documentElement.scrollHeight;
    let scrollAttempts = 0;
    const maxScrollAttempts = 20;

    while (scrollAttempts < maxScrollAttempts) {
        // Scroll to bottom
        window.scrollTo(0, document.documentElement.scrollHeight);

        // Wait for new content to load
        await delay(1500);

        // Check if new content was loaded
        const newHeight = document.documentElement.scrollHeight;
        if (newHeight === lastHeight) {
            // No new content loaded, try one more time to be sure
            if (scrollAttempts > 2) {
                console.log('✓ Reached end of page');
                break;
            }
        } else {
            console.log(`📜 Loaded more content... (scroll ${scrollAttempts + 1})`);
        }

        lastHeight = newHeight;
        scrollAttempts++;
    }

    // Scroll back to top to see results
    window.scrollTo(0, 0);

    // Wait a bit more for any final lazy loading
    await delay(1000);

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

    // Try multiple selector strategies for Travis Mathew
    // First, try to find the main product grid container (Travis Mathew specific)
    let productCards = [];
    const mainGrid = document.querySelector('.ss__results');

    if (mainGrid) {
        console.log('✓ Found Travis Mathew product grid (.ss__results)');
        // Get all direct children that contain product links
        const gridChildren = mainGrid.querySelectorAll(':scope > *');
        console.log(`Try 1 (ss__results children): ${gridChildren.length} potential cards`);

        // Filter to only elements that have product links
        productCards = Array.from(gridChildren).filter(child => {
            return child.querySelector('a[href*="/products/"]') !== null;
        });
        console.log(`Filtered to ${productCards.length} actual product cards`);
    }

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('[data-testid*="product"], [data-test*="product"]');
        console.log(`Try 2 (data-testid): ${productCards.length} cards`);
    }

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('article, [role="article"], li[class*="product"], li[class*="item"], li[class*="grid"]');
        console.log(`Try 3 (article/li): ${productCards.length} cards`);
    }

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('.product-card, .product-item, .grid-item, .grid__item, [class*="ProductCard"], [class*="ProductItem"], [class*="product-grid-item"]');
        console.log(`Try 4 (common classes): ${productCards.length} cards`);
    }

    if (productCards.length === 0) {
        // Try looking for div containers with links
        productCards = document.querySelectorAll('div:has(> a[href*="/products/"])');
        console.log(`Try 4 (div with product links): ${productCards.length} cards`);
    }

    if (productCards.length === 0) {
        // Fallback: Find parent containers of product links
        console.log('Try 5: Using product link parents...');
        const linkParents = new Set();
        allLinks.forEach(link => {
            // Get the closest container that might be a product card
            let parent = link.parentElement;
            let depth = 0;
            while (parent && depth < 6) {
                const tagName = parent.tagName;
                const className = parent.className?.toLowerCase() || '';

                // Look for containers that seem like product cards
                if (tagName === 'LI' ||
                    tagName === 'ARTICLE' ||
                    className.includes('item') ||
                    className.includes('card') ||
                    className.includes('product') ||
                    className.includes('grid') ||
                    // Check if this container has both image and price (likely a product card)
                    (parent.querySelector('img') && parent.querySelector('[class*="price"]'))) {
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

    // If still no cards found, try one more aggressive approach
    if (productCards.length === 0 && allLinks.length > 0) {
        console.log('Try 6: Using immediate parent of each product link...');
        const uniqueParents = new Set();
        allLinks.forEach(link => {
            // Go up 2-3 levels to find the product container
            let container = link.parentElement?.parentElement;
            if (container && container.querySelector('img')) {
                uniqueParents.add(container);
            }
        });
        productCards = Array.from(uniqueParents);
        console.log(`Found ${productCards.length} product containers (aggressive)`);
    }

    console.log(`📦 Final count: ${productCards.length} product cards`);

    if (productCards.length === 0) {
        console.error('❌ No products found! Debugging info:');
        console.error(`   Total links on page: ${allLinks.length}`);
        console.error(`   First 3 links:`, Array.from(allLinks).slice(0, 3).map(l => l.href));

        if (allLinks.length > 0) {
            // Show detailed debugging for the first link
            const firstLink = allLinks[0];
            console.error('\n🔍 Analyzing first product link structure:');
            console.error('   Link href:', firstLink.href);
            console.error('   Link text:', firstLink.textContent?.trim());

            let parent = firstLink;
            let level = 0;
            console.error('\n   Parent hierarchy:');
            while (parent && level < 8) {
                const classes = parent.className || '(no class)';
                const id = parent.id ? `#${parent.id}` : '';
                console.error(`   Level ${level}: <${parent.tagName.toLowerCase()}> class="${classes}" ${id}`);
                parent = parent.parentElement;
                level++;
            }
        }

        console.error('\n💡 Tips:');
        console.error('   1. Make sure you\'re on a collection page like /collections/womens-bottoms');
        console.error('   2. Wait for page to fully load');
        console.error('   3. Scroll down to load lazy-loaded products');
        console.error('   4. Check browser console for errors');
        console.error('\n💡 Manual debugging:');
        console.error('   Run this in console to see link parents:');
        console.error('   document.querySelectorAll(\'a[href*="/products/"]\')[0].parentElement.parentElement');

        alert('No products found. Check console for detailed debugging info.');
        return;
    }

    productCards.forEach((card, index) => {
        try {
            const product = {
                brand: 'Travis Mathew',
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

            // Extract product name/title - Travis Mathew-specific selectors
            const titleSelectors = [
                '.product-card__title',
                '.product-title',
                '.product-item__title',
                '[class*="ProductCard"] [class*="Title"]',
                '[class*="product-name"]',
                '[class*="ProductName"]',
                '[class*="card__title"]',
                '[class*="grid-product__title"]',
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

            // If no name found in card, try getting from link aria-label or title
            if (!product.name && link) {
                product.name = link.getAttribute('aria-label') || link.getAttribute('title');
            }

            // Extract pricing information - Travis Mathew-specific
            const priceSelectors = [
                '[class*="price"]',
                '[class*="Price"]',
                '[data-testid*="price"]',
                '.product-card__price',
                '.product-price',
                '.grid-product__price'
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

                // Check for sale/markdown badge
                const saleBadge = card.querySelector('[class*="sale"], [class*="Sale"], [class*="markdown"], [class*="Markdown"], .badge--sale, [class*="discount"], [class*="Discount"]');
                if (saleBadge) {
                    product.on_sale = true;
                }
            }

            // Extract color options/swatches - Travis Mathew-specific
            const colors = [];

            // Filter function to exclude junk text
            const isValidColor = (text) => {
                if (!text || text.length < 2 || text.length > 60) return false;

                // Exclude common UI text patterns
                const excludePatterns = [
                    /^slide\s+\d+\s+of\s+\d+$/i,
                    /^previous\s+slide$/i,
                    /^next\s+slide$/i,
                    /^add\s+to\s+(cart|bag|wishlist)/i,
                    /^quick\s+(add|view|shop)/i,
                    /^(size|color)$/i,
                ];

                return !excludePatterns.some(pattern => pattern.test(text));
            };

            // Method 1: Travis Mathew specific - look for ss__variant elements
            const tmVariants = card.querySelectorAll('.ss__variant, [class*="ss__variant"]');
            tmVariants.forEach(variant => {
                // Check for title attribute on the variant or its parent
                const colorName = variant.getAttribute('title') ||
                                variant.parentElement?.getAttribute('title');

                if (colorName && isValidColor(colorName) && !colors.includes(colorName)) {
                    colors.push(colorName.trim());
                }

                // Also check for radio inputs with color values
                const radioInput = variant.querySelector('input[type="radio"][name="Color"]');
                if (radioInput) {
                    const colorValue = radioInput.getAttribute('value') ||
                                     radioInput.getAttribute('data-product-title');
                    if (colorValue && isValidColor(colorValue) && !colors.includes(colorValue)) {
                        colors.push(colorValue.trim());
                    }
                }
            });

            // Method 2: Look for color swatch buttons
            if (colors.length === 0) {
                const swatchButtons = card.querySelectorAll('button[class*="swatch"], button[class*="color"], [class*="color-swatch"]');
                swatchButtons.forEach(button => {
                    const colorName = button.getAttribute('aria-label') ||
                                    button.getAttribute('title') ||
                                    button.getAttribute('data-color') ||
                                    button.getAttribute('data-color-name');

                    if (colorName && isValidColor(colorName) && !colors.includes(colorName)) {
                        colors.push(colorName.trim());
                    }
                });
            }

            // Method 3: Look for color swatches with data attributes
            if (colors.length === 0) {
                const colorSwatches = card.querySelectorAll('[class*="color-swatch"], [class*="ColorSwatch"], [class*="swatch"], [data-color]');
                colorSwatches.forEach(swatch => {
                    const colorName = swatch.getAttribute('data-color') ||
                                    swatch.getAttribute('aria-label') ||
                                    swatch.getAttribute('title') ||
                                    swatch.getAttribute('alt');
                    if (colorName && isValidColor(colorName) && !colors.includes(colorName)) {
                        colors.push(colorName.trim());
                    }

                    // Also check for images within swatches
                    const swatchImg = swatch.querySelector('img');
                    if (swatchImg) {
                        const alt = swatchImg.getAttribute('alt');
                        if (alt && isValidColor(alt) && !colors.includes(alt)) {
                            colors.push(alt.trim());
                        }
                    }
                });
            }

            // Method 3: Check the main product image for color in alt text
            const mainImage = card.querySelector('img[class*="product"], img[class*="Product"], img[class*="grid"], img[class*="card"]');
            if (mainImage && colors.length === 0) {
                const alt = mainImage.getAttribute('alt');
                if (alt) {
                    // Try different patterns
                    if (alt.includes('/')) {
                        const parts = alt.split('/').map(p => p.trim());
                        const potentialColor = parts[parts.length - 1];
                        if (isValidColor(potentialColor) && !colors.includes(potentialColor)) {
                            colors.push(potentialColor);
                        }
                    } else if (alt.includes(' - ')) {
                        const parts = alt.split(' - ').map(p => p.trim());
                        const potentialColor = parts[parts.length - 1];
                        if (isValidColor(potentialColor) && !colors.includes(potentialColor)) {
                            colors.push(potentialColor);
                        }
                    }
                }
            }

            // Method 4: Check for all images in card for color info
            if (colors.length === 0) {
                const allImages = card.querySelectorAll('img');
                allImages.forEach(img => {
                    const alt = img.getAttribute('alt');
                    // Look for patterns like "Product Name - Color Name"
                    if (alt && alt.includes('-')) {
                        const parts = alt.split('-').map(p => p.trim());
                        const potentialColor = parts[parts.length - 1];
                        // Only add if it's a reasonable length for a color name
                        if (isValidColor(potentialColor) && !colors.includes(potentialColor)) {
                            colors.push(potentialColor);
                        }
                    }
                });
            }

            // Method 5: Check for color count indicator
            if (colors.length === 0) {
                const colorCountElements = card.querySelectorAll('span, div, p');
                for (const elem of colorCountElements) {
                    const text = elem.textContent?.trim();
                    if (text && text.match(/^\d+\s*(color|colour)s?$/i)) {
                        const match = text.match(/^(\d+)/);
                        if (match) {
                            product.has_multiple_colors = true;
                            product.color_count = parseInt(match[1]);
                            break;
                        }
                    }
                }
            }

            product.colors = [...new Set(colors)]; // Remove duplicates

            // Cap at reasonable number (if more than 15, likely an error)
            if (product.colors.length > 15) {
                console.warn(`⚠️  Product ${product.name} has ${product.colors.length} colors - likely scraping error, keeping first 15`);
                product.colors = product.colors.slice(0, 15);
            }

            // Extract product images - Travis Mathew-specific
            const images = [];
            const imgSelectors = [
                'img[class*="product"]',
                'img[class*="Product"]',
                'img[class*="grid"]',
                'img[class*="card"]',
                'img'
            ];

            for (const selector of imgSelectors) {
                const img = card.querySelector(selector);
                if (img) {
                    const imgSrc = img.src || img.getAttribute('data-src') || img.getAttribute('srcset');
                    if (imgSrc && !imgSrc.includes('placeholder') && !imgSrc.includes('data:image')) {
                        // Take first URL if srcset
                        const cleanSrc = imgSrc.split(',')[0].split(' ')[0].split('?')[0];
                        images.push(cleanSrc);
                        break; // Just get first image
                    }
                }
            }

            product.images = images;

            // Check for badges - Travis Mathew-specific
            const badges = [];
            const badgeSelectors = card.querySelectorAll(
                '.badge, [class*="Badge"], [class*="label"], [class*="tag"], [class*="flag"], .product-flag'
            );

            badgeSelectors.forEach(badge => {
                const badgeText = badge.textContent.trim().toLowerCase();
                if (badgeText) {
                    if (badgeText.includes('best') && badgeText.includes('seller')) {
                        badges.push('best-seller');
                        product.is_best_seller = true;
                    } else if (badgeText.includes('new')) {
                        badges.push('new');
                    } else if (badgeText.includes('sale') || badgeText.includes('markdown') || badgeText.includes('discount')) {
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
        alert('No products found. Please make sure you\'re on a collection page like /collections/womens-bottoms');
        return;
    }

    // Generate filename
    const pageSlug = window.location.pathname.replace(/\//g, '_').replace(/^_/, '') || 'homepage';
    const timestamp = Date.now();
    const filename = `travismathew_products_${pageSlug}_${timestamp}.json`;

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
    console.log('1. Save the file to the data/travismathew-data/ directory');
    console.log('2. Repeat for other collection pages:');
    console.log('   - Men\'s Tops: https://travismathew.com/collections/mens-tops');
    console.log('   - Men\'s Bottoms: https://travismathew.com/collections/mens-bottoms');
    console.log('   - Women\'s Tops: https://travismathew.com/collections/womens-tops');
    console.log('   - Women\'s Bottoms: https://travismathew.com/collections/womens-bottoms');
    console.log('3. Run: python combine_manual_scrapes.py data/travismathew-data');
    console.log('4. Run: python database/upload_data.py');

    return products;
})();
