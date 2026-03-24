-- Seed data for AlloyDB AI Query Agent demo
-- Run this script once against your AlloyDB / PostgreSQL instance.

-- ----------------------------------------------------------------
-- Products table
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id         SERIAL PRIMARY KEY,
    name       TEXT           NOT NULL,
    category   TEXT           NOT NULL,
    price      NUMERIC(10, 2) NOT NULL,
    stock      INT            NOT NULL DEFAULT 0,
    created_at TIMESTAMP      NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------
-- Orders table
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id            SERIAL PRIMARY KEY,
    product_id    INT            NOT NULL REFERENCES products(id),
    quantity      INT            NOT NULL,
    total_price   NUMERIC(10, 2) NOT NULL,
    order_date    TIMESTAMP      NOT NULL DEFAULT NOW(),
    customer_name TEXT           NOT NULL
);

-- ----------------------------------------------------------------
-- Sample products
-- ----------------------------------------------------------------
INSERT INTO products (name, category, price, stock) VALUES
    ('Wireless Headphones',  'Electronics',  79.99,  120),
    ('Mechanical Keyboard',  'Electronics', 129.99,   75),
    ('USB-C Hub',            'Electronics',  45.00,  200),
    ('Laptop Stand',         'Accessories',  35.50,  150),
    ('Webcam HD 1080p',      'Electronics',  69.99,   90),
    ('Desk Lamp LED',        'Accessories',  25.00,  300),
    ('Noise-Cancel Earbuds', 'Electronics',  99.99,   60),
    ('Mouse Pad XL',         'Accessories',  18.99,  400),
    ('Portable SSD 1TB',     'Storage',     109.99,   50),
    ('Smart Notebook',       'Stationery',   24.99,  180)
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------
-- Sample orders
-- ----------------------------------------------------------------
INSERT INTO orders (product_id, quantity, total_price, customer_name, order_date) VALUES
    (1, 2, 159.98, 'Alice Johnson',  NOW() - INTERVAL '10 days'),
    (2, 1, 129.99, 'Bob Smith',      NOW() - INTERVAL '8 days'),
    (3, 3, 135.00, 'Carol White',    NOW() - INTERVAL '7 days'),
    (5, 1,  69.99, 'David Brown',    NOW() - INTERVAL '6 days'),
    (7, 2, 199.98, 'Eva Martinez',   NOW() - INTERVAL '5 days'),
    (9, 1, 109.99, 'Frank Lee',      NOW() - INTERVAL '4 days'),
    (1, 1,  79.99, 'Grace Kim',      NOW() - INTERVAL '3 days'),
    (4, 2,  71.00, 'Hank Wilson',    NOW() - INTERVAL '2 days'),
    (6, 4, 100.00, 'Isla Davis',     NOW() - INTERVAL '1 day'),
    (2, 1, 129.99, 'Jack Taylor',    NOW())
ON CONFLICT DO NOTHING;
