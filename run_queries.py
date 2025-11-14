"""
Query Execution Script
Runs the SQL queries and displays results
"""

import sqlite3
import sys

def run_query(conn, query_name, query):
    """Execute a query and display results"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print(f"{query_name}")
    print("="*80 + "\n")
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Print header
        header = " | ".join(f"{col[:18]:18s}" for col in column_names)
        print(header)
        print("-" * len(header))
        
        # Print rows
        if not results:
            print("No results found.")
        else:
            for row in results:
                formatted_row = []
                for val in row:
                    if val is None:
                        formatted_row.append("NULL")
                    elif isinstance(val, float):
                        formatted_row.append(f"{val:.2f}")
                    else:
                        formatted_row.append(str(val)[:18])
                print(" | ".join(f"{val:18s}" for val in formatted_row))
            
            print(f"\nTotal rows: {len(results)}")
    
    except Exception as e:
        print(f"ERROR executing query: {e}")

def main():
    db_file = 'ecommerce.db'
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    
    # Query 1: Customer Purchase Analysis Report
    query1 = """
WITH customer_orders AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.email,
        c.country,
        c.registration_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.total_amount) AS total_spent,
        AVG(o.total_amount) AS average_order_value,
        MAX(o.order_date) AS last_order_date
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.country, c.registration_date
),
customer_categories AS (
    SELECT 
        c.customer_id,
        p.category,
        SUM(oi.quantity) AS category_quantity,
        ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY SUM(oi.quantity) DESC) AS rn
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id, p.category
),
customer_products AS (
    SELECT 
        c.customer_id,
        p.product_name,
        COUNT(*) AS purchase_count,
        ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY COUNT(*) DESC) AS rn
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id, p.product_name
),
customer_items AS (
    SELECT 
        c.customer_id,
        SUM(oi.quantity) AS total_items_purchased
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id
),
customer_ratings AS (
    SELECT 
        customer_id,
        ROUND(AVG(rating), 2) AS average_rating_given
    FROM reviews
    GROUP BY customer_id
)
SELECT 
    co.customer_id,
    co.customer_name,
    co.email,
    co.country,
    co.total_orders,
    ROUND(co.total_spent, 2) AS total_spent,
    ROUND(co.average_order_value, 2) AS average_order_value,
    cc.category AS most_purchased_category,
    cp.product_name AS favorite_product,
    ci.total_items_purchased,
    COALESCE(cr.average_rating_given, 0) AS average_rating_given,
    co.last_order_date,
    CAST(JULIANDAY('2025-11-14') - JULIANDAY(co.registration_date) AS INTEGER) AS customer_lifetime_days
FROM customer_orders co
LEFT JOIN customer_categories cc ON co.customer_id = cc.customer_id AND cc.rn = 1
LEFT JOIN customer_products cp ON co.customer_id = cp.customer_id AND cp.rn = 1
LEFT JOIN customer_items ci ON co.customer_id = ci.customer_id
LEFT JOIN customer_ratings cr ON co.customer_id = cr.customer_id
ORDER BY co.total_spent DESC
LIMIT 20
"""
    
    # Query 2: Product Performance Report
    query2 = """
WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.brand,
        p.price AS current_price,
        COUNT(DISTINCT oi.order_id) AS number_of_orders,
        SUM(oi.quantity) AS total_quantity_sold,
        SUM(oi.subtotal) AS total_revenue
    FROM products p
    INNER JOIN order_items oi ON p.product_id = oi.product_id
    INNER JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY p.product_id, p.product_name, p.category, p.brand, p.price
),
product_reviews AS (
    SELECT 
        product_id,
        COUNT(*) AS total_reviews,
        ROUND(AVG(rating), 2) AS average_rating,
        SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) AS five_star_reviews,
        SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) AS one_star_reviews
    FROM reviews
    GROUP BY product_id
)
SELECT 
    ps.product_id,
    ps.product_name,
    ps.category,
    ps.brand,
    ROUND(ps.current_price, 2) AS current_price,
    ps.number_of_orders,
    ps.total_quantity_sold,
    ROUND(ps.total_revenue, 2) AS total_revenue,
    ROUND(ps.total_revenue / ps.total_quantity_sold, 2) AS avg_revenue_per_unit,
    COALESCE(pr.total_reviews, 0) AS total_reviews,
    COALESCE(pr.average_rating, 0) AS average_rating,
    COALESCE(pr.five_star_reviews, 0) AS five_star_reviews,
    COALESCE(pr.one_star_reviews, 0) AS one_star_reviews,
    CASE 
        WHEN pr.total_reviews > 0 
        THEN ROUND((CAST(pr.five_star_reviews AS REAL) / pr.total_reviews * 100), 1)
        ELSE 0 
    END AS five_star_percentage
FROM product_sales ps
LEFT JOIN product_reviews pr ON ps.product_id = pr.product_id
ORDER BY ps.total_revenue DESC
LIMIT 15
"""
    
    # Query 3: Category Performance
    query3 = """
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) AS total_products,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.subtotal), 2) AS total_revenue,
    ROUND(AVG(oi.unit_price), 2) AS avg_product_price,
    ROUND(AVG(r.rating), 2) AS avg_category_rating,
    COUNT(DISTINCT r.review_id) AS total_reviews
FROM products p
INNER JOIN order_items oi ON p.product_id = oi.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN reviews r ON p.product_id = r.product_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY p.category
ORDER BY total_revenue DESC
"""
    
    try:
        # Run all queries
        run_query(conn, "QUERY 1: Customer Purchase Analysis Report (Top 20)", query1)
        run_query(conn, "QUERY 2: Product Performance Report (Top 15)", query2)
        run_query(conn, "QUERY 3: Category Performance Analysis", query3)
        
        print("\n" + "="*80)
        print("All queries executed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
