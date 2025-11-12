#!/usr/bin/env python3
"""
Convenience script to run common tasks
"""

import sys
import subprocess
from pathlib import Path


def print_help():
    """Print help message"""
    print("""
Rhone Data Analytics - Task Runner

Usage: python run.py <command>

Commands:
    scrape      Run the Scrapy spider to scrape Rhone.com
    upload      Upload scraped data to Supabase
    dashboard   Run the Streamlit dashboard
    install     Install all required dependencies
    setup       Complete setup wizard
    help        Show this help message

Examples:
    python run.py scrape
    python run.py upload
    python run.py dashboard
    """)


def run_scraper():
    """Run the Scrapy spider"""
    print("Starting Rhone scraper...")
    print("This may take several minutes depending on the number of products.\n")

    scraper_dir = Path(__file__).parent / "scraper"

    try:
        subprocess.run(
            ["scrapy", "crawl", "rhone"],
            cwd=scraper_dir,
            check=True
        )
        print("\nScraping complete! Data saved to data/ directory")
        print("Next step: python run.py upload")
    except subprocess.CalledProcessError as e:
        print(f"Error running scraper: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Scrapy not found. Please install dependencies first:")
        print("  pip install -r requirements.txt")
        sys.exit(1)


def upload_data():
    """Upload scraped data to Supabase"""
    print("Uploading data to Supabase...")

    upload_script = Path(__file__).parent / "database" / "upload_data.py"

    try:
        subprocess.run(
            [sys.executable, str(upload_script)],
            check=True
        )
        print("\nUpload complete!")
        print("Next step: python run.py dashboard")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading data: {e}")
        sys.exit(1)


def run_dashboard():
    """Run the Streamlit dashboard"""
    print("Starting Streamlit dashboard...")

    app_file = Path(__file__).parent / "streamlit_app.py"

    try:
        subprocess.run(
            ["streamlit", "run", str(app_file)],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running dashboard: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install dependencies first:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDashboard stopped.")


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")

    requirements_file = Path(__file__).parent / "requirements.txt"

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        print("\nDependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)


def setup_wizard():
    """Run setup wizard"""
    print("=== Rhone Data Analytics Setup Wizard ===\n")

    # Check if .env exists
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"

    if not env_file.exists():
        print("Creating .env file...")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print(f"Created .env file. Please edit it and add your Supabase credentials:")
            print(f"  {env_file}\n")
        else:
            print("Warning: .env.example not found")

    # Install dependencies
    print("Step 1: Installing dependencies...")
    install_dependencies()

    print("\n=== Setup Complete! ===")
    print("\nNext steps:")
    print("1. Edit .env file with your Supabase credentials")
    print("2. Run the database schema in Supabase SQL Editor (database/schema.sql)")
    print("3. Run: python run.py scrape")
    print("4. Run: python run.py upload")
    print("5. Run: python run.py dashboard")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "scrape":
        run_scraper()
    elif command == "upload":
        upload_data()
    elif command == "dashboard":
        run_dashboard()
    elif command == "install":
        install_dependencies()
    elif command == "setup":
        setup_wizard()
    elif command == "help":
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
