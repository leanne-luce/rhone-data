// Enhanced Product Extraction Script for Rhone.com and Competitors
// Extracts: products, reviews, ratings, badges (best-seller, new, restocked), and brand
//
// Usage:
// 1. Open any product collection page (Rhone, Vuori, Lululemon, etc.)
// 2. Press F12 to open Developer Tools
// 3. Go to the Console tab
// 4. Copy and paste this entire script
// 5. Press Enter
// 6. File will download automatically

(function() {
    console.log('🚀 Starting enhanced product extraction...');

    // Auto-detect brand from URL
    const hostname = window.location.hostname.toLowerCase();
    let detectedBrand = 'Unknown';

    if (hostname.includes('rhone')) {
        detectedBrand = 'Rhone';
    } else if (hostname.includes('vuori')) {
        detectedBrand = 'Vuori';
    } else if (hostname.includes('lululemon')) {
        detectedBrand = 'Lululemon';
    } else if (hostname.includes('gymshark')) {
        detectedBrand = 'Gymshark';
    } else if (hostname.includes('outdoor')) {
        detectedBrand = 'Outdoor Voices';
    } else if (hostname.includes('alo')) {
        detectedBrand = 'Alo Yoga';
    }

    console.log(`🏷️  Detected brand: ${detectedBrand}`);

    const products = [];

    // Find all product links on the page
    const productLinks = document.querySelectorAll('a[href*="/products/"]');
    const uniqueLinks = new Set();

    productLinks.forEach(link => {
        const href = link.href;
        if (href && href.includes('/products/')) {
            uniqueLinks.add(href);
        }
    });

    console.log(`📦 Found ${uniqueLinks.size} unique product links`);

    // Extract product IDs from URLs
    uniqueLinks.forEach(url => {
        const match = url.match(/\/products\/([^?#]+)/);
        if (match) {
            products.push({
                url: url,
                product_id: match[1],
                brand: detectedBrand,
                scraped_at: new Date().toISOString(),
            });
        }
    });

    // Try to get more details from product cards
    const productCards = document.querySelectorAll(
        '[class*="product-card"], [class*="ProductCard"], .product-item, [data-product-id], .product, [class*="grid-product"]'
    );

    console.log(`🔍 Processing ${productCards.length} product cards...`);

    productCards.forEach(card => {
        const link = card.querySelector('a[href*="/products/"]');
        const title = card.querySelector('[class*="title"], [class*="name"], h2, h3, h4, [class*="product-title"]');
        const price = card.querySelector('[class*="price"]');
        const image = card.querySelector('img');

        if (link) {
            const url = link.href;
            const productId = url.match(/\/products\/([^?#]+)/)?.[1];

            const existing = products.find(p => p.product_id === productId);
            if (existing) {
                existing.name = title?.textContent?.trim() || null;

                // Extract pricing - try multiple selectors and patterns
                let priceText = null;
                if (price) {
                    priceText = price.textContent?.trim();
                } else {
                    // Try alternative price selectors
                    const priceAlt = card.querySelector('[class*="Price"], .money, [data-price]');
                    priceText = priceAlt?.textContent?.trim();
                }

                // Parse price and sale_price from text
                if (priceText) {
                    // Look for patterns like "$50 $40" or "Was $50 Now $40"
                    const priceMatches = priceText.match(/\$[\d,]+(?:\.\d{2})?/g);
                    if (priceMatches && priceMatches.length >= 2) {
                        // Multiple prices found - likely original and sale
                        existing.original_price = parseFloat(priceMatches[0].replace(/[$,]/g, ''));
                        existing.sale_price = parseFloat(priceMatches[1].replace(/[$,]/g, ''));
                    } else if (priceMatches && priceMatches.length === 1) {
                        // Single price
                        existing.original_price = parseFloat(priceMatches[0].replace(/[$,]/g, ''));
                    }
                }

                // Extract image URL
                if (image?.src) {
                    existing.image = image.src;
                }

                // Extract color swatches
                const colorSwatches = card.querySelectorAll(
                    '[class*="swatch"], [class*="color-option"], [class*="ColorSwatch"], [data-color], [aria-label*="color"]'
                );

                const colorSet = new Set();
                colorSwatches.forEach(swatch => {
                    // Try multiple methods to extract color name
                    let colorName = null;

                    // Method 1: aria-label (most reliable)
                    const ariaLabel = swatch.getAttribute('aria-label');
                    if (ariaLabel) {
                        colorName = ariaLabel.replace(/color|swatch|:/gi, '').trim();
                    }

                    // Method 2: data-color attribute
                    if (!colorName) {
                        colorName = swatch.getAttribute('data-color');
                    }

                    // Method 3: title attribute
                    if (!colorName) {
                        colorName = swatch.getAttribute('title');
                    }

                    // Method 4: alt text of image inside
                    if (!colorName) {
                        const swatchImg = swatch.querySelector('img');
                        if (swatchImg) {
                            colorName = swatchImg.getAttribute('alt');
                        }
                    }

                    // Only use text content as last resort and skip if it looks like combined colors
                    if (!colorName) {
                        const text = swatch.textContent?.trim();
                        // Check for combined colors pattern (camelCase like "AsphaltBright")
                        if (text && text.length < 30 && text.length > 0) {
                            // Skip if it contains multiple capital letters indicating combined colors
                            const capitalCount = (text.match(/[A-Z]/g) || []).length;
                            if (capitalCount <= 1) {
                                colorName = text;
                            }
                        }
                    }

                    if (colorName && colorName.length > 0) {
                        colorSet.add(colorName);
                    }
                });

                if (colorSet.size > 0) {
                    existing.colors = Array.from(colorSet);
                }

                // Extract review rating - try multiple selectors
                const ratingElem = card.querySelector(
                    '[class*="rating"], [class*="star"], [data-rating], [aria-label*="star"], .yotpo-sr-bottom-line-score, .stamped-product-reviews-badge'
                );
                if (ratingElem) {
                    // Try to get rating from aria-label
                    const ariaLabel = ratingElem.getAttribute('aria-label');
                    if (ariaLabel) {
                        const ratingMatch = ariaLabel.match(/(\d+\.?\d*)\s*(star|out of)/i);
                        if (ratingMatch) {
                            existing.review_rating = parseFloat(ratingMatch[1]);
                        }
                    }
                    // Try data-rating attribute
                    const dataRating = ratingElem.getAttribute('data-rating');
                    if (dataRating && !existing.review_rating) {
                        existing.review_rating = parseFloat(dataRating);
                    }
                    // Try text content
                    const ratingText = ratingElem.textContent;
                    if (ratingText && !existing.review_rating) {
                        const match = ratingText.match(/(\d+\.?\d*)/);
                        if (match) {
                            existing.review_rating = parseFloat(match[1]);
                        }
                    }
                }

                // Extract review count - try multiple selectors
                const reviewCountElem = card.querySelector(
                    '[class*="review-count"], [class*="reviews"], [class*="rating-count"], .yotpo-bottomline, .stamped-badge-caption'
                );
                if (reviewCountElem) {
                    const reviewText = reviewCountElem.textContent;
                    // Match patterns like "(123)", "123 reviews", "123"
                    const countMatch = reviewText.match(/\(?(\d+)\)?(?:\s*review)?/i);
                    if (countMatch) {
                        existing.review_count = parseInt(countMatch[1]);
                    }
                }

                // Extract product badges - try multiple selectors
                const badgeElems = card.querySelectorAll(
                    '[class*="badge"], [class*="label"], [class*="tag"], .product-flag, [class*="ribbon"]'
                );

                const badgeSet = new Set();
                badgeElems.forEach(badge => {
                    const badgeText = badge.textContent.trim().toLowerCase();
                    if (badgeText) {
                        // Check for specific badges
                        if (badgeText.includes('best') && badgeText.includes('seller')) {
                            badgeSet.add('best-seller');
                            existing.is_best_seller = true;
                        } else if (badgeText.includes('new')) {
                            badgeSet.add('new');
                        } else if (badgeText.includes('restock')) {
                            badgeSet.add('restocked');
                        } else if (badgeText.includes('sale') || badgeText.includes('discount')) {
                            badgeSet.add('sale');
                        } else if (badgeText.includes('limited')) {
                            badgeSet.add('limited');
                        } else {
                            // Add any other badges
                            badgeSet.add(badgeText);
                        }
                    }
                });

                if (badgeSet.size > 0) {
                    existing.badges = Array.from(badgeSet);
                }

                // Try to determine category and gender from URL
                const urlLower = window.location.pathname.toLowerCase();
                if (urlLower.includes('mens') || urlLower.includes('/men')) {
                    existing.gender = 'Men';
                } else if (urlLower.includes('womens') || urlLower.includes('/women')) {
                    existing.gender = 'Women';
                }

                if (urlLower.includes('tops')) existing.category = 'Tops';
                else if (urlLower.includes('bottoms')) existing.category = 'Bottoms';
                else if (urlLower.includes('shorts')) existing.category = 'Shorts';
                else if (urlLower.includes('outerwear')) existing.category = 'Outerwear';
            }
        }
    });

    console.log(`✅ Extracted ${products.length} products`);

    // Log summary of what was found
    const withRatings = products.filter(p => p.review_rating).length;
    const withReviewCount = products.filter(p => p.review_count).length;
    const withBadges = products.filter(p => p.badges && p.badges.length > 0).length;
    const bestSellers = products.filter(p => p.is_best_seller).length;

    console.log(`📊 Data Summary:`);
    console.log(`  ⭐ ${withRatings} products with ratings`);
    console.log(`  💬 ${withReviewCount} products with review counts`);
    console.log(`  🏷️  ${withBadges} products with badges`);
    console.log(`  🔥 ${bestSellers} best-seller products`);

    // Download as JSON
    const dataStr = JSON.stringify(products, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${detectedBrand.toLowerCase()}_products_${window.location.pathname.replace(/\//g, '_')}_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log('⬇️  Download started!');
    console.log(`📁 File: ${detectedBrand.toLowerCase()}_products_${window.location.pathname.replace(/\//g, '_')}_${Date.now()}.json`);

    return products;
})();
