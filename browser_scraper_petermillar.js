// Enhanced Product Extraction Script for Peter Millar
// This script extracts detailed product information including colors, prices, and sale status
//
// Usage:
// 1. Open a collection page (e.g., https://www.petermillar.com/c/women/tops)
// 2. Open browser console (F12 or Cmd+Option+I)
// 3. Paste this entire script and press Enter
// 4. Wait for extraction to complete
// 5. JSON file will download automatically

(async function() {
    console.log('🚀 Starting Peter Millar product extraction...');

    const products = [];
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

    // Determine current page type and category info
    const isHomepage = window.location.pathname === '/';
    const urlPath = window.location.pathname.toLowerCase();

    console.log(`🔍 Current URL: ${window.location.href}`);
    console.log(`📍 Path: ${urlPath}`);

    let category = null;
    let gender = null;

    // Gender detection - Peter Millar uses /c/women, /c/men
    if (urlPath.includes('/women')) {
        gender = 'Women';
    } else if (urlPath.includes('/men')) {
        gender = 'Men';
    }

    // Peter Millar-specific category detection
    if (urlPath.includes('tops') || urlPath.includes('shirts') || urlPath.includes('tees') || urlPath.includes('polos')) {
        category = 'Tops';
    } else if (urlPath.includes('pants') || urlPath.includes('trousers') || urlPath.includes('joggers')) {
        category = 'Bottoms';
    } else if (urlPath.includes('shorts')) {
        category = 'Shorts';
    } else if (urlPath.includes('outerwear') || urlPath.includes('jackets') || urlPath.includes('vests') || urlPath.includes('sweaters')) {
        category = 'Outerwear';
    } else if (urlPath.includes('skirts') || urlPath.includes('skorts')) {
        category = 'Skirts';
    } else if (urlPath.includes('dresses')) {
        category = 'Dresses';
    } else if (urlPath.includes('accessories')) {
        category = 'Accessories';
    } else if (urlPath.includes('bags')) {
        category = 'Bags';
    }

    console.log(`📍 Detected: ${gender || 'Unknown gender'} - ${category || 'Unknown category'}`);

    // Wait for products to load (Peter Millar uses lazy loading)
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

        // Debug: Show parent hierarchy for first link
        console.log('\n🔍 Debugging first product link parent structure:');
        let debugParent = allLinks[0].parentElement;
        let debugDepth = 0;
        while (debugParent && debugDepth < 8) {
            console.log(`  Level ${debugDepth}: <${debugParent.tagName.toLowerCase()}${debugParent.className ? ' class="' + debugParent.className + '"' : ''}${debugParent.hasAttribute('data-itemid') ? ' data-itemid' : ''}>`);
            debugParent = debugParent.parentElement;
            debugDepth++;
        }
        console.log('');
    }

    // Try multiple selector strategies for Peter Millar
    let productCards = document.querySelectorAll('[data-testid*="product"], [data-test*="product"]');
    console.log(`Try 1 (data-testid): ${productCards.length} cards`);

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('[class*="ProductCard"], [class*="productCard"], [class*="product-card"], [class*="ProductTile"]');
        console.log(`Try 2 (product card classes): ${productCards.length} cards`);
    }

    if (productCards.length === 0) {
        productCards = document.querySelectorAll('article, [role="article"], li[class*="product"], li[class*="item"], li[class*="grid"]');
        console.log(`Try 3 (article/li): ${productCards.length} cards`);
    }

    // Peter Millar specific: Look for the grid items that contain products
    if (productCards.length === 0) {
        console.log('Try 4: Looking for grid items with dwmarker...');
        productCards = document.querySelectorAll('.grid-tile, [class*="grid-tile"], [data-itemid]');
        console.log(`Found ${productCards.length} grid-tile cards`);
    }

    if (productCards.length === 0) {
        // Fallback: Find parent containers of product links (go deeper)
        console.log('Try 5: Using product link parents...');
        const linkParents = new Set();
        allLinks.forEach(link => {
            // Get the closest container that might be a product card
            let parent = link.parentElement;
            let depth = 0;
            while (parent && depth < 8) {
                const className = parent.className ? parent.className.toLowerCase() : '';
                if (parent.tagName === 'LI' || parent.tagName === 'ARTICLE' ||
                    className.includes('item') ||
                    className.includes('card') ||
                    className.includes('product') ||
                    className.includes('tile') ||
                    className.includes('grid') ||
                    parent.hasAttribute('data-itemid')) {
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
        console.error('   1. Make sure you\'re on a collection page like /c/women/tops');
        console.error('   2. Wait for page to fully load');
        console.error('   3. Scroll down to load lazy-loaded products');
        console.error('   4. Check browser console for errors');
        alert('No products found. Check console for debugging info.');
        return;
    }

    productCards.forEach((card, index) => {
        try {
            // Debug first card to understand structure
            if (index === 0) {
                console.log('\n🔍 Debugging first product card:');
                console.log('  Card tag:', card.tagName);
                console.log('  Card class:', card.className);
                console.log('  Has data-itemid:', card.hasAttribute('data-itemid'));
                console.log('  Card HTML preview:', card.innerHTML.substring(0, 200));
            }

            const product = {
                brand: 'Peter Millar',
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

                // Extract product ID from URL
                const match = fullUrl.match(/\/p\/([^/?#]+)/);
                if (match) {
                    product.product_id = match[1] + '/';
                }
            }

            // If still no URL, skip this card
            if (!product.url || !product.product_id) {
                return; // Skip this product
            }

            // Extract product name/title - Peter Millar-specific selectors
            const titleSelectors = [
                '.product-card__title',
                '.product-title',
                '.product-item__title',
                '[class*="ProductCard"] [class*="Title"]',
                '[class*="ProductTile"] [class*="Title"]',
                '[class*="product-name"]',
                '[class*="ProductName"]',
                'h2', 'h3', 'h4',
                '.card__heading',
                '[class*="title"]:not([class*="price"])',
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

            // Extract pricing information - Peter Millar specific
            const allPrices = [];

            // Method 1: Peter Millar uses class="price" for price container
            let priceDiv = card.querySelector('.price');

            // Method 2: Look for any div with price-related classes
            if (!priceDiv) {
                priceDiv = card.querySelector('[class*="price"]');
            }

            // Method 3: Look for common price patterns in divs/spans
            if (!priceDiv) {
                const allDivs = card.querySelectorAll('div, span, p');
                for (const div of allDivs) {
                    const text = div.textContent.trim();
                    // Check if this element directly contains a price (and not nested deep)
                    if (text.match(/^\s*\$\s*\d+/) && div.children.length === 0) {
                        priceDiv = div;
                        break;
                    }
                }
            }

            if (priceDiv) {
                const priceText = priceDiv.textContent.trim();
                console.log(`Price text found: "${priceText}"`);

                // Match patterns like "$0", "$125", "$98.50", "$ 125", etc.
                const priceMatches = priceText.match(/\$\s*(\d+(?:\.\d{2})?)/g);

                if (priceMatches) {
                    priceMatches.forEach(match => {
                        const price = parseFloat(match.replace(/\$\s*/, ''));
                        // Allow $0 prices for debugging, we'll see them in output
                        if (price >= 0 && !allPrices.includes(price)) {
                            allPrices.push(price);
                        }
                    });
                }
            }

            // Fallback: scan entire card for dollar amounts if no prices found
            if (allPrices.length === 0) {
                console.log(`No price div found, scanning card text...`);
                const cardText = card.textContent;
                const priceMatches = cardText.match(/\$\s*(\d+(?:\.\d{2})?)/g);
                if (priceMatches) {
                    console.log(`Found price matches in card text:`, priceMatches);
                    priceMatches.forEach(match => {
                        const price = parseFloat(match.replace(/\$\s*/, ''));
                        if (price > 0 && price < 2000 && !allPrices.includes(price)) {
                            allPrices.push(price);
                        }
                    });
                }
            }

            // Set prices based on what we found
            if (allPrices.length > 1) {
                // Multiple prices found - likely on sale
                allPrices.sort((a, b) => a - b); // Sort ascending
                product.sale_price = allPrices[0]; // Lowest is sale price
                product.price = allPrices[allPrices.length - 1]; // Highest is original price
                product.on_sale = true;
            } else if (allPrices.length === 1) {
                // Single price - regular price
                product.price = allPrices[0];
                product.sale_price = null;
                product.on_sale = false;
            }

            // Check for sale badge or indicator
            const saleBadge = card.querySelector('[class*="sale"], [class*="Sale"], .badge--sale, [class*="discount"], [class*="Discount"], [class*="markdown"]');
            if (saleBadge) {
                product.on_sale = true;
            }

            // Extract color options/swatches - Peter Millar specific
            const colors = [];

            // Peter Millar uses class="color-swatches" with label elements containing aria-label
            const swatchContainer = card.querySelector('.color-swatches, [class*="color-swatches"]');
            if (swatchContainer) {
                // Look for all labels with aria-label attributes
                const colorLabels = swatchContainer.querySelectorAll('label[aria-label]');
                colorLabels.forEach(label => {
                    const ariaLabel = label.getAttribute('aria-label');
                    if (ariaLabel) {
                        // Parse aria-label like "Selected Color: Black" or "Color: Navy"
                        let colorName = ariaLabel;

                        // Remove "Selected Color:" or "Color:" prefix
                        colorName = colorName.replace(/^Selected Color:\s*/i, '');
                        colorName = colorName.replace(/^Color:\s*/i, '');

                        // Also check for color in span inside label
                        const colorSpan = label.querySelector('span');
                        if (colorSpan && colorSpan.textContent.trim()) {
                            colorName = colorSpan.textContent.trim();
                        }

                        if (colorName && colorName.length > 0 && !colors.includes(colorName)) {
                            colors.push(colorName.trim());
                        }
                    }
                });

                // Also check spans with class containing "color" inside swatch container
                const colorSpans = swatchContainer.querySelectorAll('span');
                colorSpans.forEach(span => {
                    const text = span.textContent?.trim();
                    // Avoid adding generic text like "Selected Color:" or empty strings
                    if (text && text.length > 0 && text.length < 50 &&
                        !text.match(/^selected color:?$/i) &&
                        !text.match(/^color:?$/i) &&
                        !colors.includes(text)) {
                        colors.push(text);
                    }
                });
            }

            // Fallback Method 1: Look for color swatch buttons with aria-label
            if (colors.length === 0) {
                const colorButtons = card.querySelectorAll('button[class*="swatch"], button[class*="color"], button[data-color]');
                colorButtons.forEach(button => {
                    const colorName = button.getAttribute('aria-label') ||
                                    button.getAttribute('title') ||
                                    button.getAttribute('data-color') ||
                                    button.getAttribute('data-color-name');

                    if (colorName && !colors.includes(colorName)) {
                        colors.push(colorName.trim());
                    }
                });
            }

            // Fallback Method 2: Look for input elements with color data
            if (colors.length === 0) {
                const colorInputs = card.querySelectorAll('input[class*="color"], input[name*="color"]');
                colorInputs.forEach(input => {
                    const inputId = input.getAttribute('id');
                    if (inputId) {
                        // Find the associated label
                        const associatedLabel = card.querySelector(`label[for="${inputId}"]`);
                        if (associatedLabel) {
                            const ariaLabel = associatedLabel.getAttribute('aria-label');
                            if (ariaLabel) {
                                let colorName = ariaLabel.replace(/^Selected Color:\s*/i, '').replace(/^Color:\s*/i, '');
                                if (colorName && !colors.includes(colorName)) {
                                    colors.push(colorName.trim());
                                }
                            }
                        }
                    }
                });
            }

            // Fallback Method 3: Check for color count indicator
            if (colors.length === 0) {
                const spans = card.querySelectorAll('span, div');
                spans.forEach(span => {
                    const text = span.textContent?.trim();
                    // Look for text like "4 colors" or color count indicators
                    if (text && text.match(/^\d+\s*(color|colour)s?$/i)) {
                        const match = text.match(/^(\d+)/);
                        if (match) {
                            product.has_multiple_colors = true;
                            product.color_count = parseInt(match[1]);
                        }
                    }
                });
            }

            product.colors = [...new Set(colors)]; // Remove duplicates

            // Extract product images
            const images = [];
            const imgSelectors = [
                'img[class*="product"]',
                'img[class*="Product"]',
                'img[class*="tile"]',
                '.product-card__image img',
                '.product-image img',
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

            // Check for badges
            const badges = [];
            const badgeSelectors = card.querySelectorAll(
                '.badge, [class*="Badge"], [class*="label"], [class*="tag"], .product-flag, [class*="flag"]'
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
        alert('No products found. Please make sure you\'re on a collection page like /c/women/tops');
        return;
    }

    // Generate filename
    const pageSlug = window.location.pathname.replace(/\//g, '_').replace(/^_/, '') || 'homepage';
    const timestamp = Date.now();
    const filename = `petermillar_products_${pageSlug}_${timestamp}.json`;

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
    console.log('1. Save the file to the data/petermillar-data/ directory');
    console.log('2. Repeat for other collection pages:');
    console.log('   - Women\'s Tops: https://www.petermillar.com/c/women/tops');
    console.log('   - Women\'s Bottoms: https://www.petermillar.com/c/women/bottoms');
    console.log('   - Women\'s Dresses: https://www.petermillar.com/c/women/dresses');
    console.log('   - Men\'s Tops: https://www.petermillar.com/c/men/tops');
    console.log('   - Men\'s Bottoms: https://www.petermillar.com/c/men/bottoms');
    console.log('3. Run: python combine_manual_scrapes.py');
    console.log('4. Run: python database/upload_data.py');

    return products;
})();
