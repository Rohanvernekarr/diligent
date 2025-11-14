-- ============================================================
-- E-COMMERCE DATABASE QUERIES
-- Multi-Table Join Queries for Business Intelligence
-- ============================================================

-- ------------------------------------------------------------
-- QUERY 1: Customer Purchase Analysis Report
-- ------------------------------------------------------------
-- This query provides a comprehensive view of customer purchasing behavior
-- by joining customers, orders, order_items, products, and reviews tables.
-- It calculates various metrics including total spending, order counts,
-- favorite categories, and average ratings.

WITH customer_orders AS (
    -- Get order totals for each customer (excluding cancelled orders)
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
    -- Find most purchased category for each customer
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
    -- Find most frequently purchased product for each customer
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
    -- Calculate total items purchased
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
    -- Calculate average rating given by customer
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
LIMIT 20;

-- Expected Output Columns:
-- 1. customer_id: Unique customer identifier
-- 2. customer_name: Full name of the customer
-- 3. email: Customer email address
-- 4. country: Customer's country
-- 5. total_orders: Number of orders placed (delivered/shipped only)
-- 6. total_spent: Total amount spent on all orders
-- 7. average_order_value: Average value per order
-- 8. most_purchased_category: Category with highest quantity purchased
-- 9. favorite_product: Most frequently purchased product
-- 10. total_items_purchased: Total number of items (quantity sum)
-- 11. average_rating_given: Average rating the customer gives in reviews
-- 12. last_order_date: Date of most recent order
-- 13. customer_lifetime_days: Days since customer registration

-- Business Insights:
-- - Identifies top spending customers for VIP programs
-- - Shows customer preferences (categories and products) for personalized marketing
-- - Reveals customer engagement through ratings and purchase frequency
-- - Helps segment customers by spending patterns and lifetime value


-- ------------------------------------------------------------
-- QUERY 2: Product Performance Report
-- ------------------------------------------------------------
-- This query analyzes product performance by combining sales data
-- from order_items with customer feedback from reviews.
-- It provides insights into revenue, popularity, and customer satisfaction.

WITH product_sales AS (
    -- Calculate sales metrics for each product
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
    -- Calculate review metrics for each product
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
LIMIT 15;

-- Expected Output Columns:
-- 1. product_id: Unique product identifier
-- 2. product_name: Name of the product
-- 3. category: Product category
-- 4. brand: Product brand
-- 5. current_price: Current selling price
-- 6. number_of_orders: Number of orders containing this product
-- 7. total_quantity_sold: Total units sold
-- 8. total_revenue: Total revenue generated (quantity × price)
-- 9. avg_revenue_per_unit: Average revenue per unit sold
-- 10. total_reviews: Number of customer reviews
-- 11. average_rating: Average customer rating (1-5)
-- 12. five_star_reviews: Count of 5-star reviews
-- 13. one_star_reviews: Count of 1-star reviews
-- 14. five_star_percentage: Percentage of reviews that are 5-star

-- Business Insights:
-- - Identifies best-selling products by revenue and quantity
-- - Correlates sales performance with customer satisfaction (ratings)
-- - Highlights products that need attention (low ratings despite high sales)
-- - Helps with inventory planning based on popularity
-- - Supports pricing strategy by showing revenue per unit


-- ------------------------------------------------------------
-- QUERY 3: Category Performance Analysis
-- ------------------------------------------------------------
-- This query provides insights into how different product categories
-- are performing in terms of sales, revenue, and customer satisfaction.

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
ORDER BY total_revenue DESC;

-- Business Insights:
-- - Shows which categories generate the most revenue
-- - Identifies categories with best customer satisfaction
-- - Helps allocate marketing budget by category performance
-- - Reveals pricing patterns across categories


-- ------------------------------------------------------------
-- QUERY 4: Monthly Sales Trend
-- ------------------------------------------------------------
-- This query shows sales trends over time to identify seasonality
-- and growth patterns.

SELECT 
    STRFTIME('%Y-%m', o.order_date) AS month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    SUM(oi.quantity) AS total_items_sold,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY STRFTIME('%Y-%m', o.order_date)
ORDER BY month DESC
LIMIT 12;

-- Business Insights:
-- - Identifies peak sales months for inventory planning
-- - Shows growth or decline trends over time
-- - Helps plan promotional campaigns based on historical patterns


-- ------------------------------------------------------------
-- QUERY 5: Customer Segments by Purchase Behavior
-- ------------------------------------------------------------
-- This query segments customers based on their purchase frequency
-- and spending patterns for targeted marketing.

WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(o.total_amount) AS total_spent,
        MAX(o.order_date) AS last_order_date,
        CAST(JULIANDAY('2025-11-14') - JULIANDAY(MAX(o.order_date)) AS INTEGER) AS days_since_last_order
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id, c.first_name, c.last_name
)
SELECT 
    customer_id,
    customer_name,
    order_count,
    ROUND(total_spent, 2) AS total_spent,
    last_order_date,
    days_since_last_order,
    CASE 
        WHEN order_count >= 5 AND total_spent >= 1000 THEN 'VIP'
        WHEN order_count >= 3 AND total_spent >= 500 THEN 'Loyal'
        WHEN days_since_last_order <= 30 THEN 'Active'
        WHEN days_since_last_order > 90 THEN 'At Risk'
        ELSE 'Regular'
    END AS customer_segment
FROM customer_metrics
ORDER BY total_spent DESC
LIMIT 50;

-- Business Insights:
-- - Segments customers for personalized marketing campaigns
-- - Identifies at-risk customers who haven't ordered recently
-- - Highlights VIP customers for special treatment
-- - Helps plan retention strategies


-- ------------------------------------------------------------
-- PERFORMANCE OPTIMIZATION RECOMMENDATIONS
-- ------------------------------------------------------------

-- The following indexes have been created to optimize query performance:
-- 1. idx_orders_customer ON orders(customer_id)
-- 2. idx_order_items_order ON order_items(order_id)
-- 3. idx_order_items_product ON order_items(product_id)
-- 4. idx_reviews_product ON reviews(product_id)
-- 5. idx_reviews_customer ON reviews(customer_id)
-- 6. idx_orders_status ON orders(order_status)
-- 7. idx_products_category ON products(category)

-- Additional indexes to consider for specific queries:
-- CREATE INDEX idx_orders_date ON orders(order_date);
-- CREATE INDEX idx_reviews_rating ON reviews(rating);
-- CREATE INDEX idx_products_price ON products(price);

-- Query optimization tips:
-- 1. Use EXPLAIN QUERY PLAN before complex queries to check index usage
-- 2. Filter by order_status early to reduce dataset size
-- 3. Use CTEs (Common Table Expressions) for readability and maintainability
-- 4. Consider materialized views for frequently-run analytical queries
-- 5. Use LIMIT to restrict result sets when appropriate

-- ============================================================
-- END OF QUERIES
-- ============================================================
