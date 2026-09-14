"""
mock_data.py

Fictional "ShopEase" e-commerce data used by the tool functions in tools.py.
None of this is real customer or company data — it exists purely so the
agent has something concrete to look up during a demo.
"""

# --- Orders -----------------------------------------------------------
# Keyed by order ID (uppercase, no spaces).
ORDERS = {
    "ORD1001": {
        "order_id": "ORD1001",
        "product": "Wireless Headphones",
        "status": "Shipped",
        "order_date": "2026-08-22",
        "estimated_delivery": "2026-08-30",
        "amount": 59.99,
        "currency": "USD",
    },
    "ORD1002": {
        "order_id": "ORD1002",
        "product": "Laptop Stand",
        "status": "Processing",
        "order_date": "2026-08-28",
        "estimated_delivery": "2026-09-02",
        "amount": 34.50,
        "currency": "USD",
    },
    "ORD1003": {
        "order_id": "ORD1003",
        "product": "USB-C Hub",
        "status": "Delivered",
        "order_date": "2026-08-10",
        "estimated_delivery": "2026-08-15",
        "amount": 22.00,
        "currency": "USD",
    },
    "ORD1004": {
        "order_id": "ORD1004",
        "product": "Mechanical Keyboard",
        "status": "Cancelled",
        "order_date": "2026-08-05",
        "estimated_delivery": None,
        "amount": 89.99,
        "currency": "USD",
    },
}

# --- Refunds ------------------------------------------------------------
# Keyed by order ID. Not every order has a refund on file.
REFUNDS = {
    "ORD1004": {
        "order_id": "ORD1004",
        "refund_status": "Completed",
        "refund_amount": 89.99,
        "currency": "USD",
        "requested_date": "2026-08-06",
        "completed_date": "2026-08-11",
        "reason": "Customer changed their mind before shipping.",
    },
    "ORD1003": {
        "order_id": "ORD1003",
        "refund_status": "Under Review",
        "refund_amount": 22.00,
        "currency": "USD",
        "requested_date": "2026-09-01",
        "completed_date": None,
        "reason": "Item arrived with a scratched casing.",
    },
}

# --- Product catalog ------------------------------------------------------
PRODUCTS = {
    "wireless headphones": {
        "name": "Wireless Headphones",
        "price": 59.99,
        "currency": "USD",
        "in_stock": True,
        "stock_count": 142,
        "description": "Over-ear Bluetooth 5.3 headphones, 30-hour battery life.",
    },
    "laptop stand": {
        "name": "Laptop Stand",
        "price": 34.50,
        "currency": "USD",
        "in_stock": True,
        "stock_count": 58,
        "description": "Adjustable aluminium stand, fits 11-17 inch laptops.",
    },
    "usb-c hub": {
        "name": "USB-C Hub",
        "price": 22.00,
        "currency": "USD",
        "in_stock": False,
        "stock_count": 0,
        "description": "7-in-1 hub with HDMI, USB-A x3, SD card reader.",
    },
    "mechanical keyboard": {
        "name": "Mechanical Keyboard",
        "price": 89.99,
        "currency": "USD",
        "in_stock": True,
        "stock_count": 21,
        "description": "Hot-swappable mechanical keyboard with brown switches.",
    },
}
