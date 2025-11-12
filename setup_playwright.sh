#!/bin/bash
# Setup script to install Playwright browsers

echo "Installing Playwright browsers..."
echo "This may take a few minutes as it downloads Chromium."
echo ""

playwright install chromium

echo ""
echo "Playwright setup complete!"
echo "You can now run: python run.py scrape"
