# E-Commerce Database Project

**Diligent Company Assignment**

### Step 1  
python generate_data.py

### Step 2  
python ingest_data.py

### Step 3  
python run_queries.py

### Step 4  
python verify.py


A complete synthetic e-commerce database system with SQLite, featuring realistic data, proper schema design, and comprehensive analytical queries.

---

1. PROMPT: Generate Synthetic E-commerce Data (5 files)
Location: PROMPTS.md - Lines 7-150

What it specifies:

5 CSV files (customers, products, orders, order_items, reviews)
Field specifications with data types and ranges
Data consistency rules (IDs must match across files)
No real PII - only synthetic data
IMPLEMENTED:

✓ customers.csv - 100 records
✓ products.csv - 150 records
✓ orders.csv - 250 records
✓ order_items.csv - 733 records
✓ reviews.csv - 179 records
Script: generate_data.py (generates order_items and reviews with proper consistency)

2. PROMPT: Ingest Data into SQLite Database
Location: PROMPTS.md - Lines 152-271

What it specifies:

Create SQLite database schema with constraints
Import all 5 CSV files
Create foreign key relationships
Add performance indexes
Verify data integrity
IMPLEMENTED:

✓ Database created: ecommerce.db (164 KB)
✓ 5 tables with proper schema
✓ Foreign key constraints enforced
✓ 7 performance indexes created
✓ All 1,412 records imported successfully

3. PROMPT: Multi-Table Join Query with Output
Location: PROMPTS.md - Lines 273-350 AND queries.sql

What it specifies:

SQL query joining multiple tables (4-5 tables)
Complex aggregations and calculations
Generate meaningful business output
Include WHERE, GROUP BY, ORDER BY clauses

## 📁 Project Structure

```
diligent-task/
├── data/                      # CSV data files
│   ├── customers.csv          # 100 customer records
│   ├── products.csv           # 150 product records
│   ├── orders.csv             # 250 order records
│   ├── order_items.csv        # 733 order item records
│   └── reviews.csv            # 179 review records
├── ecommerce.db               # SQLite database (generated)
├── generate_data.py           # Script to generate order_items and reviews
├── ingest_data.py             # Database creation and data ingestion
├── run_queries.py             # Execute and display query results
├── queries.sql                # SQL queries for analysis
├── PROMPTS.md                 # Original assignment prompts
└── README.md                  # This file
```

---

## 📊 Dataset Overview

### 1. Customers (100 records)
- **Fields:** customer_id, first_name, last_name, email, phone, registration_date, country, city, postal_code
- **Features:** International customers from USA, UK, Canada, Australia, Germany, France
- **Date Range:** Registrations from March 2023 to November 2025

### 2. Products (150 records)
- **Fields:** product_id, product_name, category, brand, price, stock_quantity, supplier_id
- **Categories:** Electronics (30), Fashion (28), Home (30), Sports (19), Beauty (20), Books (20)
- **Price Range:** $5.99 to $1,999.99

### 3. Orders (250 records)
- **Fields:** order_id, customer_id, order_date, order_status, total_amount, shipping_address, payment_method
- **Statuses:** Delivered, Shipped, Processing, Cancelled
- **Date Range:** January 2024 to November 2025
- **Payment Methods:** Credit Card, PayPal, Debit Card, Bank Transfer

### 4. Order Items (733 records)
- **Fields:** order_item_id, order_id, product_id, quantity, unit_price, subtotal
- **Features:** 1-5 items per order, quantities 1-3, totals match order amounts

### 5. Reviews (179 records)
- **Fields:** review_id, product_id, customer_id, rating, review_text, review_date
- **Ratings:** 1-5 stars, realistic distribution
- **Constraint:** Only for purchased products

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- No additional packages required (uses built-in `sqlite3` and `csv` modules)

### Step 1: Generate Complete Dataset
```powershell
python generate_data.py
```
This script:
- Reads customers.csv, products.csv, and orders.csv
- Generates order_items.csv with consistent data
- Generates reviews.csv with realistic ratings
- Updates orders.csv with matching totals

### Step 2: Create Database and Import Data
```powershell
python ingest_data.py
```
This script:
- Creates `ecommerce.db` SQLite database
- Creates tables with proper schema and constraints
- Imports all CSV files into the database
- Creates indexes for query optimization
- Verifies data integrity and foreign key constraints
- Displays summary statistics

**Expected Output:**
```
============================================================
E-COMMERCE DATABASE INGESTION
============================================================

Creating new database: ecommerce.db
...
Row counts:
  customers      :   100 rows
  products       :   150 rows
  orders         :   250 rows
  order_items    :   733 rows
  reviews        :   179 rows

✓ All foreign key constraints are satisfied!
```

### Step 3: Run Analytical Queries
```powershell
python run_queries.py
```
This script executes three main queries:
1. **Customer Purchase Analysis** - Top 20 customers by spending
2. **Product Performance Report** - Top 15 products by revenue
3. **Category Performance Analysis** - All categories

---

## 📝 Database Schema

### Entity Relationship Diagram

```
customers (1) ──< (M) orders (1) ──< (M) order_items (M) >── (1) products
    │                                                              │
    │                                                              │
    └──────────────< (M) reviews (M) >────────────────────────────┘
```

### Table Definitions

#### customers
```sql
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
);
```

#### products
```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    supplier_id INTEGER
);
```

#### orders
```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    order_status TEXT CHECK(order_status IN 
        ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')),
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address TEXT,
    payment_method TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

#### order_items
```sql
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

#### reviews
```sql
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

### Indexes
- `idx_orders_customer` ON orders(customer_id)
- `idx_order_items_order` ON order_items(order_id)
- `idx_order_items_product` ON order_items(product_id)
- `idx_reviews_product` ON reviews(product_id)
- `idx_reviews_customer` ON reviews(customer_id)
- `idx_orders_status` ON orders(order_status)
- `idx_products_category` ON products(category)

---

## 🔍 SQL Queries

### Query 1: Customer Purchase Analysis Report

**Purpose:** Identify top customers and their purchasing patterns

**Joins:** customers → orders → order_items → products, reviews

**Output Columns:**
- customer_id, customer_name, email, country
- total_orders, total_spent, average_order_value
- most_purchased_category, favorite_product
- total_items_purchased, average_rating_given
- last_order_date, customer_lifetime_days

**Business Use:**
- VIP customer identification
- Personalized marketing campaigns
- Customer segmentation
- Loyalty program targeting

### Query 2: Product Performance Report

**Purpose:** Analyze product sales and customer satisfaction

**Joins:** products → order_items → orders, reviews

**Output Columns:**
- product_id, product_name, category, brand, current_price
- number_of_orders, total_quantity_sold, total_revenue
- avg_revenue_per_unit, total_reviews, average_rating
- five_star_reviews, one_star_reviews, five_star_percentage

**Business Use:**
- Inventory planning
- Pricing strategy
- Product quality monitoring
- Sales forecasting

### Query 3: Category Performance Analysis

**Purpose:** Compare performance across product categories

**Joins:** products → order_items → orders, reviews

**Output Columns:**
- category, total_products, total_orders
- total_units_sold, total_revenue
- avg_product_price, avg_category_rating, total_reviews

**Business Use:**
- Marketing budget allocation
- Category expansion decisions
- Seasonal planning
- Supplier negotiations

### Additional Queries (in queries.sql)
4. **Monthly Sales Trend** - Time series analysis
5. **Customer Segments** - Behavior-based segmentation

---

## 📈 Sample Query Results

### Top Customer (Query 1)
```
Lucas Moore
- Total Spent: $3,584.84
- Orders: 3
- Favorite Category: Electronics
- Most Purchased: Monitor 27-inch 4K
- Avg Rating Given: 3.00
```

### Top Product (Query 2)
```
Exercise Bike Stationary
- Revenue: $11,599.71
- Units Sold: 29
- Orders: 15
- Avg Rating: 4.00 (3 reviews)
```

### Top Category (Query 3)
```
Sports
- Revenue: $55,607.38
- Products: 19
- Units Sold: 362
- Avg Rating: 3.69
```

---

## 🛠️ Running Custom Queries

### Using Python
```python
import sqlite3

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Your query here
cursor.execute("""
    SELECT customer_id, SUM(total_amount) 
    FROM orders 
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
    LIMIT 10
""")

results = cursor.fetchall()
for row in results:
    print(row)

conn.close()
```

### Using SQLite CLI
```powershell
sqlite3 ecommerce.db
```
```sql
-- Interactive SQL prompt
SELECT * FROM customers LIMIT 5;
.quit
```

---

## ✅ Data Integrity Features

### Foreign Key Constraints
- ✓ All `customer_id` in orders reference valid customers
- ✓ All `order_id` in order_items reference valid orders
- ✓ All `product_id` in order_items reference valid products
- ✓ All `product_id` in reviews reference valid products
- ✓ All `customer_id` in reviews reference valid customers

### Data Consistency
- ✓ Order totals match sum of order item subtotals
- ✓ Reviews only for products customers actually purchased
- ✓ Review dates after order dates
- ✓ Registration dates before order dates
- ✓ No real PII data (all synthetic)

### Data Quality
- ✓ Realistic names, emails, addresses
- ✓ Proper price formatting (2 decimal places)
- ✓ Valid date formats (YYYY-MM-DD)
- ✓ Logical relationships between entities

---

## 📊 Business Statistics

**From the current dataset:**
- Active Customers: 100 (all have placed orders)
- Average Order Value: $458.22
- Total Revenue (Delivered): $88,358.35
- Average Product Rating: 3.65 / 5.0
- Most Popular Category: Electronics (30 products)

---

## 🔒 Privacy & Compliance

✓ **No Real PII:** All data is synthetic
- Names: Common first/last name combinations
- Emails: Fake domains (example.com, testmail.net, fakemail.com)
- Phones: Synthetic number patterns
- Addresses: Generic street addresses

✓ **Safe for Development/Testing**
✓ **GDPR-Compliant** (no real personal data)
✓ **Ready for Demonstrations**

---

## 🎯 Assignment Completion Checklist

- ✅ Generated 5 CSV files with synthetic data
- ✅ Maintained data consistency (IDs match across files)
- ✅ Created SQLite database with proper schema
- ✅ Implemented foreign key constraints
- ✅ Imported all data successfully
- ✅ Created performance indexes
- ✅ Wrote complex multi-table join queries
- ✅ Verified data integrity
- ✅ Provided comprehensive documentation
- ✅ No real PII included

---

## 📚 Files Explained

### `generate_data.py`
Generates order_items.csv and reviews.csv with proper relationships:
- Ensures order totals match item subtotals
- Creates reviews only for purchased products
- Uses realistic rating distribution (more 5s, fewer 1s)
- Maintains referential integrity

### `ingest_data.py`
Complete database setup script:
- Creates all tables with constraints
- Imports CSV data in correct order
- Creates indexes for performance
- Verifies foreign keys
- Shows verification statistics

### `run_queries.py`
Query execution and display:
- Runs all analytical queries
- Formats output in readable tables
- Handles NULL values gracefully
- Shows row counts

### `queries.sql`
SQL query library:
- 5 comprehensive business queries
- Detailed comments explaining logic
- Performance optimization notes
- Expected output documentation

---

## 🔧 Troubleshooting

### Issue: "File not found" error
**Solution:** Ensure you're in the project directory
```powershell
cd d:\Pablo\diligent-task
```

### Issue: Database is locked
**Solution:** Close any open database connections
```powershell
# Delete the database and regenerate
Remove-Item ecommerce.db
python ingest_data.py
```

### Issue: Import errors
**Solution:** Verify CSV files exist
```powershell
dir data\*.csv
```

---

## 📞 Support

For questions or issues with this assignment:
1. Check the PROMPTS.md file for original requirements
2. Verify all CSV files are present in the data/ directory
3. Ensure Python 3.7+ is installed
4. Review error messages in the console output

---

## 📄 License

This is an educational project for the Diligent Company assignment.
All data is synthetic and for demonstration purposes only.

---

**Project Completed:** November 14, 2025  
**Database Version:** 1.0  
**Total Records:** 1,412 (across 5 tables)
