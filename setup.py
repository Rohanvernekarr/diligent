"""
Complete E-Commerce Database Setup
Run this script to set up everything from scratch
"""

import subprocess
import sys
import os

def run_command(description, command):
    """Run a command and display results"""
    print("\n" + "="*80)
    print(f"STEP: {description}")
    print("="*80)
    print(f"Running: {command}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✓ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error in {description}: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║         E-COMMERCE DATABASE PROJECT - COMPLETE SETUP               ║
    ║         Diligent Company Assignment                                ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if database already exists
    if os.path.exists('ecommerce.db'):
        response = input("\nDatabase 'ecommerce.db' already exists. Recreate? (y/n): ")
        if response.lower() != 'y':
            print("\nSetup cancelled. Using existing database.")
            print("Run 'python run_queries.py' to execute queries.")
            return
        os.remove('ecommerce.db')
        print("Removed existing database.")
    
    # Step 1: Generate order items and reviews
    if not run_command(
        "Generate Order Items and Reviews CSV Files",
        "python generate_data.py"
    ):
        print("\n❌ Setup failed at data generation step.")
        sys.exit(1)
    
    # Step 2: Create database and import data
    if not run_command(
        "Create SQLite Database and Import All Data",
        "python ingest_data.py"
    ):
        print("\n❌ Setup failed at database ingestion step.")
        sys.exit(1)
    
    # Step 3: Run queries
    print("\n" + "="*80)
    print("Would you like to run the analytical queries now? (y/n): ", end="")
    response = input()
    
    if response.lower() == 'y':
        run_command(
            "Execute Analytical Queries",
            "python run_queries.py"
        )
    
    # Summary
    print("\n" + "="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print("\n📁 Project Files Created:")
    print("   ├── data/")
    print("   │   ├── customers.csv      (100 records)")
    print("   │   ├── products.csv       (150 records)")
    print("   │   ├── orders.csv         (250 records)")
    print("   │   ├── order_items.csv    (733 records)")
    print("   │   └── reviews.csv        (179 records)")
    print("   └── ecommerce.db           (SQLite database)")
    
    print("\n🚀 Next Steps:")
    print("   1. View README.md for complete documentation")
    print("   2. Run queries: python run_queries.py")
    print("   3. Open database: sqlite3 ecommerce.db")
    print("   4. View SQL queries: queries.sql")
    
    print("\n💡 Quick Commands:")
    print("   • Python queries:  python run_queries.py")
    print("   • SQLite shell:    sqlite3 ecommerce.db")
    print("   • List tables:     .tables (in SQLite shell)")
    print("   • View schema:     .schema customers (in SQLite shell)")
    
    print("\n" + "="*80)
    print("Thank you for using the E-Commerce Database Setup!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
