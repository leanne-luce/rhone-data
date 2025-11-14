// Enhanced Product Extraction Script for Lululemon
// This script extracts detailed product information including colors, prices, and sale status
//
// Usage:
// 1. Open a collection page (e.g., https://shop.lululemon.com/c/men-button-down-shirts)
// 2. Open browser console (F12 or Cmd+Option+I)
// 3. Paste this entire script and press Enter
// 4. Wait for extraction to complete
// 5. JSON file will download automatically

(async function() {
    console.log('🚀 Starting Lululemon product extraction...');

    const products = [];
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

    // Determine current page type and category info
    const isHomepage = window.location.pathname === '/';
    const urlPath = window.location.pathname.toLowerCase();

    let category = null;
    let gender = null;

    // Lululemon URL structure: /c/men-tops or /c/women-leggings
    if (urlPath.includes('/men') || urlPath.includes('men-')) {
        gender = 'Men';
    } else if (urlPath.includes('/women') || urlPath.includes('women-')) {
        gender = 'Women';
    }

    // Lululemon-specific category detection
    if (urlPath.includes('tops') || urlPath.includes('shirts') || urlPath.includes('tees') || urlPath.includes('tanks')) {
        category = 'Tops';
    } else if (urlPath.includes('pants') || urlPath.includes('joggers') || urlPath.includes('trousers')) {
        category = 'Bottoms';
    } else if (urlPath.includes('shorts')) {
        category = 'Shorts';
    } else if (urlPath.includes('jackets') || urlPath.includes('hoodies') || urlPath.includes('outerwear') || urlPath.includes('sweaters')) {
        category = 'Outerwear';
    } else if (urlPath.includes('bras') || urlPath.includes('sports-bra')) {
        category = 'Sports Bras';
    } else if (urlPath.includes('leggings') || urlPath.includes('tights')) {
        category = 'Leggings';
    } else if (urlPath.includes('accessories') || urlPath.includes('bags') || urlPath.includes('hats')) {
        category = 'Accessories';
    }

    console.log(`📍 Detected: ${gender || 'Unknown gender'} - ${category || 'Unknown category'}`);

    // Wait for products to load (Lululemon uses lazy loading)
    console.log('⏳ Waiting for products to load...');
    console.log('💡 Make sure you\'ve scrolled to the bottom of the page!');

    await delay(2000); // Wait 2 seconds for initial load

    // First, let's debug and find what's actually on the page
    console.log('🔍 Debugging: Looking for product elements...');

    // Try to find product links first (most reliable)
    let allLinks = document.querySelectorAll('a[href*="/p/"]');
    console.log(`📎 Found ${allLinks.length} product links`);

    // If no links found, wait a bit more and try again
    if (allLinks.length === 0) {
        console.log('⏳ No links found yet, waiting 3 more seconds...');
        await delay(3000);
        allLinks = document.querySelectorAll('a[href*="/p/"]');
        console.log(`📎 Found ${allLinks.length} product links after waiting`);
    }

    if (allLinks.length > 0) {
        console.log('Sample link:', allLinks[0].href);
        console.log('Parent element classes:', allLinks[0].parentElement?.className);
    }

    // Try multiple selector strategies for Lululemon
    let productCards = document.querySelectorAll('[data-testid*="product"], [data-test*="product"]');
    console.log(`Try 1 (data-testid): ${productCards.length} cards`);

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('[class*="ProductCard"], [class*="productCard"], [class*="product-card"]');
        console.log(`Try 2 (product card classes): ${productCards.length} cards`);
    }

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('article, [role="article"], [class*="product"], [class*="Product"]');
        console.log(`Try 3 (article/product): ${productCards.length} cards`);
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
                if (parent.tagName === 'LI' || parent.tagName === 'ARTICLE' || parent.tagName === 'DIV') {
                    // Check if this looks like a product container
                    const className = parent.className.toLowerCase();
                    if (className.includes('item') ||
                        className.includes('card') ||
                        className.includes('product') ||
                        parent.querySelectorAll('img').length > 0) {
                        linkParents.add(parent);
                        break;
                    }
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
        console.error('   1. Make sure you\'re on a collection page like /c/men-button-down-shirts');
        console.error('   2. Wait for page to fully load');
        console.error('   3. Scroll down to load lazy-loaded products');
        console.error('   4. Check browser console for errors');
        alert('No products found. Check console for debugging info.');
        return;
    }

    productCards.forEach((card, index) => {
        try {
            const product = {
                brand: 'Lululemon',
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
            if (card.tagName === 'A' && card.href && card.href.includes('/p/')) {
                link = card;
            } else {
                link = card.querySelector('a[href*="/p/"]');
            }

            if (link) {
                const fullUrl = link.href;
                product.url = fullUrl;

                // Extract product ID from URL (Lululemon uses /p/product-name/_/prod12345)
                const match = fullUrl.match(/\/p\/([^/?#]+)/);
                if (match) {
                    product.product_id = match[1] + '/';
                }
            }

            // If still no URL, skip this card
            if (!product.url || !product.product_id) {
                return; // Skip this product
            }

            // Extract product name/title - Lululemon-specific selectors
            const titleSelectors = [
                '[class*="productName"]',
                '[class*="ProductName"]',
                '[class*="product-name"]',
                '[class*="title"]',
                '[class*="Title"]',
                'h2', 'h3', 'h4',
                '[data-testid*="name"]',
                '[data-testid*="title"]'
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

            // Extract pricing information - Lululemon-specific
            const priceSelectors = [
                '[class*="price"]',
                '[class*="Price"]',
                '[data-testid*="price"]',
                '[class*="ProductPrice"]'
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
                const saleBadge = card.querySelector('[class*="sale"], [class*="Sale"], [class*="markdown"], [class*="Markdown"], .badge--sale, [class*="discount"]');
                if (saleBadge) {
                    product.on_sale = true;
                }
            }

            // Extract color options/swatches - Lululemon-specific
            const colors = [];

            // Filter function to exclude junk text
            const isValidColor = (text) => {
                if (!text || text.length < 2 || text.length > 60) return false;

                // Exclude common UI text patterns (more specific)
                const excludePatterns = [
                    /^slide\s+\d+\s+of\s+\d+$/i,  // "Slide 1 of 14"
                    /^previous\s+slide$/i,
                    /^next\s+slide$/i,
                    /^add\s+to\s+(cart|bag|wishlist)/i,
                    /^quick\s+(add|view|shop)/i,
                    /^(size|color)$/i,  // Just the word "size" or "color" alone
                ];

                return !excludePatterns.some(pattern => pattern.test(text));
            };

            // Method 1: Look for swatch carousel (Lululemon's actual structure)
            const swatchCarousel = card.querySelector('[class*="swatch-carousel"]');
            if (swatchCarousel) {
                // Get all carousel slides/items with images
                const carouselSlides = swatchCarousel.querySelectorAll('[class*="carousel__slide"], [class*="swatch"]');
                carouselSlides.forEach(slide => {
                    // Look for image alt text in carousel slides
                    const img = slide.querySelector('img');
                    if (img) {
                        const alt = img.getAttribute('alt');
                        if (alt && isValidColor(alt) && !colors.includes(alt)) {
                            colors.push(alt.trim());
                        }
                    }
                });
            }

            // Method 2: Look for color swatch spans/divs with specific color classes
            const colorSwatches = card.querySelectorAll('[class*="color-swatch"], [class*="colorSwatch"], span[class*="swatch"]');
            colorSwatches.forEach(swatch => {
                // Check data attributes first
                const colorName = swatch.getAttribute('data-color') ||
                                swatch.getAttribute('aria-label') ||
                                swatch.getAttribute('title');
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

            // Method 3: Check the main product image for color in alt text
            const mainImage = card.querySelector('img[class*="product"], img[class*="Product"], img[class*="tile"]');
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
                    } else if (alt.includes(' - ') && !alt.match(/slide\s+\d+/i)) {
                        const parts = alt.split(' - ').map(p => p.trim());
                        const potentialColor = parts[parts.length - 1];
                        if (isValidColor(potentialColor) && !colors.includes(potentialColor)) {
                            colors.push(potentialColor);
                        }
                    }
                }
            }

            // Method 4: Check for color count indicator (as fallback if no colors found)
            if (colors.length === 0) {
                const colorCountElements = card.querySelectorAll('span, div, p');
                for (const elem of colorCountElements) {
                    const text = elem.textContent?.trim();
                    if (text && text.match(/^\d+\s*(color|colour)s?$/i)) {
                        const match = text.match(/^(\d+)/);
                        if (match) {
                            product.has_multiple_colors = true;
                            product.color_count = parseInt(match[1]);
                            break; // Only need one color count
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

            // Extract product images - Lululemon-specific
            const images = [];
            const imgSelectors = [
                'img[class*="product"]',
                'img[class*="Product"]',
                'img[class*="tile"]',
                'img[class*="Tile"]',
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

            // Check for badges - Lululemon-specific
            const badges = [];
            const badgeSelectors = card.querySelectorAll(
                '.badge, [class*="Badge"], [class*="label"], [class*="tag"], [class*="flag"]'
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
                    } else if (badgeText.includes('we made too much')) {
                        badges.push('wmtm'); // Lululemon's sale section
                        product.on_sale = true;
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
                console.log(`✓ [${index + 1}/${productCards.length}] ${product.name || 'Unnamed'} - ${product.colors.length} colors - ${product.on_sale ? '🏷️ SALE' : (product.price ? '$' + product.price : 'No price')}`);;
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
        alert('No products found. Please make sure you\'re on a collection page like /c/men-button-down-shirts');
        return;
    }

    // Generate filename
    const pageSlug = window.location.pathname.replace(/\//g, '_').replace(/^_/, '') || 'homepage';
    const timestamp = Date.now();
    const filename = `lululemon_products_${pageSlug}_${timestamp}.json`;

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
    console.log('1. Save the file to the data/lululemon-data/ directory');
    console.log('2. Repeat for other collection pages:');
    console.log('   - Men\'s Tops: https://shop.lululemon.com/c/men-tops');
    console.log('   - Men\'s Bottoms: https://shop.lululemon.com/c/men-pants');
    console.log('   - Women\'s Tops: https://shop.lululemon.com/c/women-tops');
    console.log('   - Women\'s Bottoms: https://shop.lululemon.com/c/women-pants');
    console.log('3. Run: python combine_manual_scrapes.py data/lululemon-data');
    console.log('4. Run: python database/upload_data.py');

    return products;
})();
