from datetime import datetime
import json
from pathlib import Path


class RhonePipeline:
    """Pipeline for processing scraped Rhone product data"""

    def open_spider(self, spider):
        """Initialize the pipeline when spider opens"""
        self.items = []
        self.output_dir = Path(__file__).parent.parent.parent / "data"
        self.output_dir.mkdir(exist_ok=True)

    def close_spider(self, spider):
        """Save all items to JSON file when spider closes"""
        if self.items:
            output_file = self.output_dir / f"rhone_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
            spider.logger.info(f"Saved {len(self.items)} products to {output_file}")

    def process_item(self, item, spider):
        """Process each scraped item"""
        # Add timestamp if not present
        if "scraped_at" not in item:
            item["scraped_at"] = datetime.now().isoformat()

        # Convert item to dict and store
        item_dict = dict(item)
        self.items.append(item_dict)

        return item
