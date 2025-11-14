# Diligent Company Assignment - E-Commerce Dataset Prompts

## Prompt 1: Generate Synthetic E-Commerce Dataset

**Objective:** Create a complete synthetic e-commerce dataset with 5 CSV files containing realistic, consistent data.

**Instructions:**

Generate 5 CSV files for an e-commerce system with the following specifications:

### 1. customers.csv
- **Fields:** customer_id, first_name, last_name, email, phone, registration_date, country, city, postal_code
- **Requirements:**
  - customer_id: Integer, unique, starting from 1001
  - first_name, last_name: Realistic synthetic names (diverse, international)
  - email: Format firstname.lastname@domain.com (use fake domains like example.com, testmail.net)
  - phone: Format +XX-XXX-XXX-XXXX (synthetic numbers)
  - registration_date: Between 2023-01-01 and 2025-11-14 (YYYY-MM-DD format)
  - country: Mix of countries (USA, UK, Canada, Australia, Germany, France, etc.)
  - city: Realistic city names matching the country
  - postal_code: Realistic format for each country
- **Records:** Generate 100 customers

### 2. products.csv
- **Fields:** product_id, product_name, category, brand, price, stock_quantity, supplier_id
- **Requirements:**
  - product_id: Integer, unique, starting from 2001
  - product_name: Realistic product names (Electronics, Clothing, Home & Garden, etc.)
  - category: Main categories (Electronics, Fashion, Home, Sports, Beauty, Books)
  - brand: Mix of synthetic brand names (TechPro, StyleMax, HomeComfort, etc.)
  - price: Decimal with 2 places, range $5.99 to $1999.99
  - stock_quantity: Integer, range 0 to 500
  - supplier_id: Integer, range 3001-3020
- **Records:** Generate 150 products

### 3. orders.csv
- **Fields:** order_id, customer_id, order_date, order_status, total_amount, shipping_address, payment_method
- **Requirements:**
  - order_id: Integer, unique, starting from 4001
  - customer_id: Must match existing customer_ids from customers.csv
  - order_date: Between 2024-01-01 and 2025-11-14 (YYYY-MM-DD format)
  - order_status: One of (Pending, Processing, Shipped, Delivered, Cancelled)
  - total_amount: Decimal with 2 places (will be sum of order items)
  - shipping_address: Format "Street, City, Postal Code, Country"
  - payment_method: One of (Credit Card, PayPal, Debit Card, Bank Transfer)
- **Records:** Generate 250 orders

### 4. order_items.csv
- **Fields:** order_item_id, order_id, product_id, quantity, unit_price, subtotal
- **Requirements:**
  - order_item_id: Integer, unique, starting from 5001
  - order_id: Must match existing order_ids from orders.csv
  - product_id: Must match existing product_ids from products.csv
  - quantity: Integer, range 1 to 5
  - unit_price: Must match the price from products.csv
  - subtotal: quantity * unit_price (calculated)
- **Records:** Generate 400-600 order items (each order can have 1-5 items)
- **Note:** Ensure total_amount in orders.csv equals sum of subtotals for all items in that order

### 5. reviews.csv
- **Fields:** review_id, product_id, customer_id, rating, review_text, review_date
- **Requirements:**
  - review_id: Integer, unique, starting from 6001
  - product_id: Must match existing product_ids from products.csv
  - customer_id: Must match existing customer_ids from customers.csv
  - rating: Integer, range 1 to 5
  - review_text: Synthetic review comments (50-200 characters)
  - review_date: Between 2024-01-01 and 2025-11-14 (YYYY-MM-DD format)
- **Records:** Generate 200 reviews

### Data Consistency Rules:
1. All IDs must be consistent across files (foreign keys must reference existing primary keys)
2. Dates must be logical (order_date before review_date, registration_date before order_date)
3. Each order must have at least 1 order_item
4. Reviews should only be for products that have been ordered by that customer
5. Use proper CSV formatting with headers and quoted strings where necessary

### Output Format:
- 5 separate CSV files with names exactly as specified above
- UTF-8 encoding
- Comma-separated values
- First row contains column headers
- No personally identifiable real data

---

## Prompt 2: Ingest Data into SQLite Database

**Objective:** Create a SQLite database schema and import all CSV files with proper relationships.

**Instructions:**

Create a Python script that performs the following operations:

### 1. Database Schema Creation
Create a SQLite database named `ecommerce.db` with the following tables and constraints:

#### customers table:
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

#### products table:
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

#### orders table:
```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    order_status TEXT CHECK(order_status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')),
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address TEXT,
    payment_method TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

#### order_items table:
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

#### reviews table:
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

### 2. Data Import Process
- Read each CSV file and import data into corresponding tables
- Use transactions for data integrity
- Handle errors gracefully with appropriate error messages
- Create indexes on foreign key columns for query performance:
  - `orders.customer_id`
  - `order_items.order_id`
  - `order_items.product_id`
  - `reviews.product_id`
  - `reviews.customer_id`

### 3. Verification
After import, print:
- Row count for each table
- Sample of 5 records from each table
- Verification that foreign key constraints are satisfied

### 4. Script Requirements:
- Use Python with sqlite3 module
- Use pandas for CSV reading (or csv module as alternative)
- Include proper error handling
- Add comments explaining each step
- Make the script reusable (drop tables if they exist before creating)

---

## Prompt 3: Generate Multi-Table Join Query

**Objective:** Write a SQL query that joins multiple tables to produce a comprehensive business insight report.

**Instructions:**

Create a SQL query that generates a **Customer Purchase Analysis Report** with the following requirements:

### Query Specifications:

**Output Columns:**
1. customer_id
2. customer_name (first_name + last_name concatenated)
3. email
4. country
5. total_orders (count of orders per customer)
6. total_spent (sum of all order amounts)
7. average_order_value (average of order amounts)
8. most_purchased_category (category with highest quantity purchased)
9. favorite_product (most frequently purchased product)
10. total_items_purchased (sum of quantities from all orders)
11. average_rating_given (average of all ratings given by customer)
12. last_order_date (most recent order date)
13. customer_lifetime_days (days since registration)

### Join Requirements:
- Join customers with orders
- Join orders with order_items
- Join order_items with products
- Join customers with reviews

### Filtering Criteria:
- Only include customers who have placed at least 1 order
- Only include orders with status 'Delivered' or 'Shipped'
- Order results by total_spent in descending order
- Limit to top 20 customers

### Additional Requirements:
1. Use appropriate JOIN types (INNER JOIN, LEFT JOIN as needed)
2. Use GROUP BY for aggregations
3. Use window functions or subqueries where necessary for complex calculations
4. Handle NULL values appropriately
5. Format decimal values to 2 decimal places
6. Include comments in the SQL explaining complex logic

### Bonus Challenge:
Also create a second query that shows:
- **Product Performance Report:** Products with their total sales, number of orders, average rating, and total reviews
- Join products, order_items, and reviews
- Calculate revenue per product (quantity * unit_price)
- Show top 15 products by revenue

### Output Format:
- Provide the complete SQL query
- Include expected column headers
- Add a brief explanation of the business insights this query provides
- Suggest potential indexes that would improve query performance

---

## Expected Deliverables

For this assignment, you should provide:

1. **5 CSV files** with synthetic e-commerce data (from Prompt 1)
2. **Python script** (`ingest_data.py`) that creates the database and imports data (from Prompt 2)
3. **SQL queries** in a file (`queries.sql`) with both the Customer Purchase Analysis and Product Performance reports (from Prompt 3)
4. **README.md** with:
   - Instructions to run the Python script
   - Instructions to execute the SQL queries
   - Brief description of the dataset structure
   - Sample output from the queries

---

## Testing Checklist

- [ ] All 5 CSV files generated with correct headers
- [ ] Data consistency verified (IDs match across files)
- [ ] No real PII data included
- [ ] Database schema created successfully
- [ ] All CSV data imported without errors
- [ ] Foreign key constraints working
- [ ] Multi-table join query executes without errors
- [ ] Query results make business sense
- [ ] Documentation is clear and complete
