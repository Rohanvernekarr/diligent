import csv
import random
from datetime import datetime, timedelta

# Read existing data
customers = []
with open('data/customers.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    customers = list(reader)

products = []
with open('data/products.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    products = list(reader)

orders = []
with open('data/orders.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    orders = list(reader)

# Generate order_items
order_items = []
order_item_id = 5001

for order in orders:
    if order['order_status'] == 'Cancelled':
        num_items = random.randint(1, 3)
    else:
        num_items = random.randint(1, 5)
    
    selected_products = random.sample(products, num_items)
    total = 0
    
    for product in selected_products:
        quantity = random.randint(1, 3)
        unit_price = float(product['price'])
        subtotal = quantity * unit_price
        total += subtotal
        
        order_items.append({
            'order_item_id': order_item_id,
            'order_id': order['order_id'],
            'product_id': product['product_id'],
            'quantity': quantity,
            'unit_price': f"{unit_price:.2f}",
            'subtotal': f"{subtotal:.2f}"
        })
        order_item_id += 1
    
    # Update order total in our list (we'll verify this matches)
    order['calculated_total'] = f"{total:.2f}"

# Write order_items
with open('data/order_items.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['order_item_id', 'order_id', 'product_id', 'quantity', 'unit_price', 'subtotal']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(order_items)

print(f"Generated {len(order_items)} order items")

# Update orders.csv with matching totals
with open('data/orders.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['order_id', 'customer_id', 'order_date', 'order_status', 'total_amount', 'shipping_address', 'payment_method']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for order in orders:
        writer.writerow({
            'order_id': order['order_id'],
            'customer_id': order['customer_id'],
            'order_date': order['order_date'],
            'order_status': order['order_status'],
            'total_amount': order['calculated_total'],
            'shipping_address': order['shipping_address'],
            'payment_method': order['payment_method']
        })

print(f"Updated {len(orders)} orders with matching totals")

# Generate reviews (only for delivered/shipped orders)
reviews = []
review_id = 6001

# Create a mapping of customer orders to products they purchased
customer_product_map = {}
for item in order_items:
    order = next((o for o in orders if o['order_id'] == item['order_id']), None)
    if order and order['order_status'] in ['Delivered', 'Shipped']:
        customer_id = order['customer_id']
        if customer_id not in customer_product_map:
            customer_product_map[customer_id] = []
        customer_product_map[customer_id].append({
            'product_id': item['product_id'],
            'order_date': order['order_date']
        })

review_texts = {
    5: ["Excellent product! Exceeded my expectations.", "Perfect! Exactly what I needed.", "Outstanding quality and fast delivery.", "Absolutely love it! Highly recommend.", "Best purchase ever! Five stars!"],
    4: ["Very good product, happy with purchase.", "Good quality, works as expected.", "Great product, minor issues but overall satisfied.", "Solid product, would buy again.", "Nice item, good value for money."],
    3: ["Decent product, meets basic needs.", "Average quality, nothing special.", "It's okay, works fine but not amazing.", "Fair product for the price.", "Acceptable, does what it says."],
    2: ["Disappointed, expected better quality.", "Not great, has some issues.", "Below expectations, wouldn't recommend.", "Poor quality, not worth the price.", "Unsatisfied, had problems with it."],
    1: ["Terrible product, waste of money.", "Very disappointed, does not work.", "Awful quality, returned immediately.", "Complete disaster, do not buy.", "Worst purchase, totally unusable."]
}

# Generate 200 reviews
review_count = 0
for customer_id, product_orders in customer_product_map.items():
    if review_count >= 200:
        break
    
    # Each customer reviews 20-40% of their purchased products
    num_reviews = max(1, int(len(product_orders) * random.uniform(0.2, 0.4)))
    reviewed_products = random.sample(product_orders, min(num_reviews, len(product_orders)))
    
    for product_order in reviewed_products:
        if review_count >= 200:
            break
        
        rating = random.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]
        review_text = random.choice(review_texts[rating])
        
        # Review date is 1-30 days after order date
        order_date = datetime.strptime(product_order['order_date'], '%Y-%m-%d')
        review_date = order_date + timedelta(days=random.randint(1, 30))
        
        reviews.append({
            'review_id': review_id,
            'product_id': product_order['product_id'],
            'customer_id': customer_id,
            'rating': rating,
            'review_text': review_text,
            'review_date': review_date.strftime('%Y-%m-%d')
        })
        review_id += 1
        review_count += 1

# Write reviews
with open('data/reviews.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['review_id', 'product_id', 'customer_id', 'rating', 'review_text', 'review_date']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(reviews)

print(f"Generated {len(reviews)} reviews")
print("\nData generation complete!")
