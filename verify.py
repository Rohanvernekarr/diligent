import sqlite3

# This file is for verification of the database created in setup.py

conn = sqlite3.connect('ecommerce.db')
cur = conn.cursor()

print("\n" + "="*60)
print("DATABASE VERIFICATION")
print("="*60)

tables = ['customers', 'products', 'orders', 'order_items', 'reviews']

for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"  {table:15} : {count:5} records")

print("="*60)
print("✓ All tables verified successfully!")
print("="*60)

conn.close()
