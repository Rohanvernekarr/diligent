"""
E-Commerce Database Ingestion Script
This script creates a SQLite database and imports CSV data with proper schema and constraints.
"""

import sqlite3
import csv
import os
from pathlib import Path

def create_database_schema(conn):
    """Create all database tables with proper constraints"""
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    print("Dropping existing tables if they exist...")
    cursor.execute("DROP TABLE IF EXISTS reviews")
    cursor.execute("DROP TABLE IF EXISTS order_items")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS customers")
    
    # Create customers table
    print("Creating customers table...")
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            registration_date DATE NOT NULL,
            country TEXT,
            city TEXT,
            postal_code TEXT
        )
    """)
    
    # Create products table
    print("Creating products table...")
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT,
            price DECIMAL(10, 2) NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            supplier_id INTEGER
        )
    """)
    
    # Create orders table
    print("Creating orders table...")
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            order_status TEXT CHECK(order_status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')),
            total_amount DECIMAL(10, 2) NOT NULL,
            shipping_address TEXT,
            payment_method TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    # Create order_items table
    print("Creating order_items table...")
    cursor.execute("""
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price DECIMAL(10, 2) NOT NULL,
            subtotal DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    
    # Create reviews table
    print("Creating reviews table...")
    cursor.execute("""
        CREATE TABLE reviews (
            review_id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            review_text TEXT,
            review_date DATE NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    conn.commit()
    print("Database schema created successfully!\n")

def create_indexes(conn):
    """Create indexes on foreign key columns for better query performance"""
    cursor = conn.cursor()
    
    print("Creating indexes...")
    cursor.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
    cursor.execute("CREATE INDEX idx_order_items_order ON order_items(order_id)")
    cursor.execute("CREATE INDEX idx_order_items_product ON order_items(product_id)")
    cursor.execute("CREATE INDEX idx_reviews_product ON reviews(product_id)")
    cursor.execute("CREATE INDEX idx_reviews_customer ON reviews(customer_id)")
    cursor.execute("CREATE INDEX idx_orders_status ON orders(order_status)")
    cursor.execute("CREATE INDEX idx_products_category ON products(category)")
    
    conn.commit()
    print("Indexes created successfully!\n")

def import_csv_data(conn, table_name, csv_file):
    """Import data from CSV file into specified table"""
    cursor = conn.cursor()
    
    if not os.path.exists(csv_file):
        print(f"ERROR: File {csv_file} not found!")
        return 0
    
    print(f"Importing data from {csv_file} into {table_name}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        if not rows:
            print(f"WARNING: No data found in {csv_file}")
            return 0
        
        # Get column names from the first row
        columns = list(rows[0].keys())
        placeholders = ','.join(['?' for _ in columns])
        column_names = ','.join(columns)
        
        # Insert data
        insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        for row in rows:
            values = [row[col] for col in columns]
            cursor.execute(insert_query, values)
        
        conn.commit()
        row_count = len(rows)
        print(f"  → Imported {row_count} rows into {table_name}")
        return row_count

def verify_data(conn):
    """Verify the imported data and show statistics"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("DATA VERIFICATION")
    print("="*60 + "\n")
    
    # Count rows in each table
    tables = ['customers', 'products', 'orders', 'order_items', 'reviews']
    
    print("Row counts:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:15s}: {count:5d} rows")
    
    # Show sample data from each table
    print("\n" + "-"*60)
    print("Sample data (first 3 rows from each table):")
    print("-"*60 + "\n")
    
    for table in tables:
        print(f"\n{table.upper()}:")
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Print header
        print("  " + " | ".join(f"{col[:15]:15s}" for col in columns))
        print("  " + "-" * (len(columns) * 18))
        
        # Print rows
        for row in rows:
            formatted_row = [str(val)[:15] if val is not None else 'NULL' for val in row]
            print("  " + " | ".join(f"{val:15s}" for val in formatted_row))
    
    # Verify foreign key constraints
    print("\n" + "-"*60)
    print("Foreign Key Verification:")
    print("-"*60 + "\n")
    
    # Check if all order customer_ids exist in customers
    cursor.execute("""
        SELECT COUNT(*) FROM orders o
        WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.customer_id = o.customer_id)
    """)
    invalid_orders = cursor.fetchone()[0]
    print(f"  Invalid customer_ids in orders: {invalid_orders}")
    
    # Check if all order_items order_ids exist in orders
    cursor.execute("""
        SELECT COUNT(*) FROM order_items oi
        WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.order_id = oi.order_id)
    """)
    invalid_order_items_orders = cursor.fetchone()[0]
    print(f"  Invalid order_ids in order_items: {invalid_order_items_orders}")
    
    # Check if all order_items product_ids exist in products
    cursor.execute("""
        SELECT COUNT(*) FROM order_items oi
        WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.product_id = oi.product_id)
    """)
    invalid_order_items_products = cursor.fetchone()[0]
    print(f"  Invalid product_ids in order_items: {invalid_order_items_products}")
    
    # Check if all reviews product_ids exist in products
    cursor.execute("""
        SELECT COUNT(*) FROM reviews r
        WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.product_id = r.product_id)
    """)
    invalid_reviews_products = cursor.fetchone()[0]
    print(f"  Invalid product_ids in reviews: {invalid_reviews_products}")
    
    # Check if all reviews customer_ids exist in customers
    cursor.execute("""
        SELECT COUNT(*) FROM reviews r
        WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.customer_id = r.customer_id)
    """)
    invalid_reviews_customers = cursor.fetchone()[0]
    print(f"  Invalid customer_ids in reviews: {invalid_reviews_customers}")
    
    if (invalid_orders == 0 and invalid_order_items_orders == 0 and 
        invalid_order_items_products == 0 and invalid_reviews_products == 0 and 
        invalid_reviews_customers == 0):
        print("\n  ✓ All foreign key constraints are satisfied!")
    else:
        print("\n  ✗ Some foreign key constraints are violated!")
    
    # Show some business statistics
    print("\n" + "-"*60)
    print("Business Statistics:")
    print("-"*60 + "\n")
    
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
    active_customers = cursor.fetchone()[0]
    print(f"  Active customers (placed orders): {active_customers}")
    
    cursor.execute("SELECT AVG(total_amount) FROM orders WHERE order_status != 'Cancelled'")
    avg_order_value = cursor.fetchone()[0]
    print(f"  Average order value: ${avg_order_value:.2f}")
    
    cursor.execute("SELECT SUM(total_amount) FROM orders WHERE order_status = 'Delivered'")
    total_revenue = cursor.fetchone()[0]
    print(f"  Total revenue (delivered orders): ${total_revenue:.2f}")
    
    cursor.execute("SELECT AVG(rating) FROM reviews")
    avg_rating = cursor.fetchone()[0]
    print(f"  Average product rating: {avg_rating:.2f} / 5.0")
    
    cursor.execute("SELECT category, COUNT(*) as cnt FROM products GROUP BY category ORDER BY cnt DESC LIMIT 1")
    top_category = cursor.fetchone()
    print(f"  Most common product category: {top_category[0]} ({top_category[1]} products)")
    
    print("\n" + "="*60)
    print("Data import and verification completed successfully!")
    print("="*60)

def main():
    """Main function to orchestrate the database creation and data import"""
    print("\n" + "="*60)
    print("E-COMMERCE DATABASE INGESTION")
    print("="*60 + "\n")
    
    # Database file path
    db_file = 'ecommerce.db'
    data_dir = 'data'
    
    # Remove existing database
    if os.path.exists(db_file):
        print(f"Removing existing database: {db_file}")
        os.remove(db_file)
    
    # Connect to database (creates new file)
    print(f"Creating new database: {db_file}\n")
    conn = sqlite3.connect(db_file)
    
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Create schema
        create_database_schema(conn)
        
        # Import data in correct order (respecting foreign key dependencies)
        import_csv_data(conn, 'customers', os.path.join(data_dir, 'customers.csv'))
        import_csv_data(conn, 'products', os.path.join(data_dir, 'products.csv'))
        import_csv_data(conn, 'orders', os.path.join(data_dir, 'orders.csv'))
        import_csv_data(conn, 'order_items', os.path.join(data_dir, 'order_items.csv'))
        import_csv_data(conn, 'reviews', os.path.join(data_dir, 'reviews.csv'))
        
        # Create indexes for performance
        create_indexes(conn)
        
        # Verify data
        verify_data(conn)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
        print(f"\nDatabase connection closed.")
        print(f"Database file created: {db_file}")

if __name__ == "__main__":
    main()
