// Travis Mathew Diagnostic Script
// Run this FIRST to understand the page structure before running the main scraper
// This will help identify the correct selectors to use

(function() {
    console.log('🔍 Travis Mathew Page Structure Diagnostic');
    console.log('==========================================\n');

    // 1. Check for product links
    const productLinks = document.querySelectorAll('a[href*="/products/"]');
    console.log(`1. PRODUCT LINKS: Found ${productLinks.length} links`);

    if (productLinks.length > 0) {
        console.log('\nFirst 3 product links:');
        Array.from(productLinks).slice(0, 3).forEach((link, i) => {
            console.log(`  ${i + 1}. ${link.href}`);
        });

        // 2. Analyze the structure of the first product link
        console.log('\n2. STRUCTURE ANALYSIS (First Product):');
        const firstLink = productLinks[0];

        console.log('\nClimbing up the DOM tree from first product link:');
        let parent = firstLink;
        let level = 0;

        while (parent && level < 10) {
            const tag = parent.tagName;
            const classes = parent.className || '(no classes)';
            const id = parent.id ? `#${parent.id}` : '';
            const hasImage = parent.querySelector('img') ? '✓ has img' : '';
            const hasPrice = parent.querySelector('[class*="price"]') ? '✓ has price' : '';

            console.log(`  Level ${level}: <${tag}> ${id}`);
            console.log(`    Classes: ${classes}`);
            if (hasImage || hasPrice) {
                console.log(`    Contains: ${hasImage} ${hasPrice}`);
            }
            console.log('');

            parent = parent.parentElement;
            level++;
        }

        // 3. Try to identify the product card container
        console.log('3. FINDING PRODUCT CARD CONTAINER:');

        const firstProductLink = productLinks[0];
        let container = firstProductLink;
        let foundContainer = null;

        for (let i = 0; i < 8; i++) {
            container = container.parentElement;
            if (!container) break;

            const hasImg = container.querySelector('img');
            const hasPrice = container.querySelector('[class*="price"]');
            const childLinks = container.querySelectorAll('a[href*="/products/"]');

            if (hasImg && hasPrice && childLinks.length === 1) {
                foundContainer = container;
                console.log(`✓ Potential product card found at level ${i + 1}:`);
                console.log(`  Tag: ${container.tagName}`);
                console.log(`  Classes: ${container.className}`);
                console.log(`  Has image: ${!!hasImg}`);
                console.log(`  Has price: ${!!hasPrice}`);
                console.log(`  Product links: ${childLinks.length}`);
                break;
            }
        }

        if (foundContainer) {
            console.log('\n4. TESTING SELECTOR:');
            const selector = `.${foundContainer.className.split(' ')[0]}`;
            console.log(`Suggested selector: "${selector}"`);
            const testCards = document.querySelectorAll(selector);
            console.log(`This selector finds: ${testCards.length} elements`);

            // Alternative: try finding all siblings
            const parent = foundContainer.parentElement;
            if (parent) {
                const siblings = parent.children;
                console.log(`\nAlternative: Parent has ${siblings.length} children (likely all product cards)`);
                console.log(`Parent tag: ${parent.tagName}`);
                console.log(`Parent classes: ${parent.className}`);
            }
        } else {
            console.log('⚠️ Could not automatically identify product card container');
            console.log('You may need to manually inspect the page structure');
        }

        // 5. Look for common grid containers
        console.log('\n5. COMMON GRID PATTERNS:');
        const gridPatterns = [
            'div[class*="grid"]',
            'ul[class*="grid"]',
            'div[class*="product"]',
            'ul[class*="product"]',
            '.grid',
            '.products',
            '.product-grid',
            '[class*="collection"]'
        ];

        gridPatterns.forEach(pattern => {
            const elements = document.querySelectorAll(pattern);
            if (elements.length > 0) {
                console.log(`  ${pattern}: ${elements.length} found`);
                elements.forEach((el, i) => {
                    const productLinksInside = el.querySelectorAll('a[href*="/products/"]').length;
                    if (productLinksInside > 5) {
                        console.log(`    → Element ${i} contains ${productLinksInside} product links (likely the main grid!)`);
                        console.log(`      Classes: ${el.className}`);
                    }
                });
            }
        });

        // 6. Sample a product card's HTML
        if (foundContainer) {
            console.log('\n6. SAMPLE PRODUCT CARD HTML:');
            console.log('First 500 characters of product card HTML:');
            console.log(foundContainer.outerHTML.substring(0, 500) + '...');
        }

    } else {
        console.log('❌ No product links found on this page!');
        console.log('Make sure you are on a collection page like:');
        console.log('  https://travismathew.com/collections/womens-bottoms');
        console.log('\nOr the page may still be loading. Wait a few seconds and try again.');
    }

    console.log('\n==========================================');
    console.log('✅ Diagnostic complete!');
    console.log('\nNext steps:');
    console.log('1. Review the output above');
    console.log('2. Look for the "Suggested selector" or identified parent classes');
    console.log('3. Update browser_scraper_travismathew.js with the correct selector');
})();
