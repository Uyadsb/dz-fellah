-- ============================================
-- PRODUCTS SCHEMA - PostgreSQL
-- DZ-Fellah Marketplace
-- ============================================

DROP TABLE IF EXISTS products CASCADE;

-- ============================================
-- PRODUCTS TABLE
-- ============================================

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    producer_id INTEGER NOT NULL REFERENCES producers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    photo_url VARCHAR(500),
    sale_type VARCHAR(20) NOT NULL CHECK (sale_type IN ('unit', 'weight')),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock NUMERIC(10, 2) NOT NULL CHECK (stock >= 0),
    product_type VARCHAR(20) NOT NULL CHECK (product_type IN ('fresh', 'processed', 'other')),
    harvest_date DATE,
    is_anti_gaspi BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_products_producer_id ON products(producer_id);
CREATE INDEX idx_products_sale_type ON products(sale_type);
CREATE INDEX idx_products_product_type ON products(product_type);
CREATE INDEX idx_products_is_anti_gaspi ON products(is_anti_gaspi);
CREATE INDEX idx_products_harvest_date ON products(harvest_date) WHERE product_type = 'fresh' AND harvest_date IS NOT NULL;
CREATE INDEX idx_products_type_anti_gaspi ON products(product_type, is_anti_gaspi);

-- ============================================
-- TRIGGER FOR UPDATED_AT
-- ============================================

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SEASONAL BASKETS TABLE
-- ============================================
CREATE TABLE seasonal_baskets (
    id SERIAL PRIMARY KEY,
    producer_id INTEGER NOT NULL REFERENCES producers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    photo_url TEXT,
    discount_percentage NUMERIC(5, 2) NOT NULL CHECK (discount_percentage >= 0 AND discount_percentage <= 100),
    original_price NUMERIC(10, 2) NOT NULL CHECK (original_price >= 0),
    discounted_price NUMERIC(10, 2) NOT NULL CHECK (discounted_price >= 0),
    delivery_frequency VARCHAR(20) NOT NULL DEFAULT 'weekly' CHECK (delivery_frequency IN ('weekly', 'biweekly', 'monthly')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_seasonal_baskets_producer_id ON seasonal_baskets(producer_id);
CREATE INDEX idx_seasonal_baskets_is_active ON seasonal_baskets(is_active);

-- ============================================
-- BASKET PRODUCTS (Many-to-Many)
-- ============================================
CREATE TABLE basket_products (
    id SERIAL PRIMARY KEY,
    basket_id INTEGER NOT NULL REFERENCES seasonal_baskets(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity NUMERIC(10, 2) NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(basket_id, product_id)
);

CREATE INDEX idx_basket_products_basket_id ON basket_products(basket_id);
CREATE INDEX idx_basket_products_product_id ON basket_products(product_id);

-- ============================================
-- CLIENT SUBSCRIPTIONS TABLE
-- ============================================
CREATE TABLE client_subscriptions (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    basket_id INTEGER NOT NULL REFERENCES seasonal_baskets(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'cancelled')),
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    next_delivery_date DATE,
    delivery_method VARCHAR(50) NOT NULL CHECK (delivery_method IN ('pickup_producer', 'pickup_point')),
    delivery_address TEXT,
    pickup_point_id VARCHAR(100),
    total_deliveries INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cancelled_at TIMESTAMP,
    UNIQUE(client_id, basket_id, status) -- Client can only have one active subscription per basket
);

CREATE INDEX idx_client_subscriptions_client_id ON client_subscriptions(client_id);
CREATE INDEX idx_client_subscriptions_basket_id ON client_subscriptions(basket_id);
CREATE INDEX idx_client_subscriptions_status ON client_subscriptions(status);
CREATE INDEX idx_client_subscriptions_next_delivery ON client_subscriptions(next_delivery_date);

-- ============================================
-- SUBSCRIPTION DELIVERIES (Tracking)
-- ============================================
CREATE TABLE subscription_deliveries (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES client_subscriptions(id) ON DELETE CASCADE,
    delivery_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'ready', 'picked_up', 'missed')),
    picked_up_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_subscription_deliveries_subscription_id ON subscription_deliveries(subscription_id);
CREATE INDEX idx_subscription_deliveries_status ON subscription_deliveries(status);
CREATE INDEX idx_subscription_deliveries_delivery_date ON subscription_deliveries(delivery_date);

-- rating tables

-- Product Ratings Table (using user_id instead of client_id)
CREATE TABLE product_ratings (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one rating per user per product
    CONSTRAINT unique_user_product_rating UNIQUE(product_id, user_id)
);

-- Indexes for performance
CREATE INDEX idx_product_ratings_product ON product_ratings(product_id);
CREATE INDEX idx_product_ratings_user ON product_ratings(user_id);

-- Product rating summary view
CREATE OR REPLACE VIEW product_rating_summary AS
SELECT 
    p.id AS product_id,
    p.name AS product_name,
    p.producer_id,
    COUNT(pr.id) AS total_ratings,
    COALESCE(ROUND(AVG(pr.rating), 1), 0) AS average_rating,
    COUNT(CASE WHEN pr.rating = 5 THEN 1 END) AS five_star_count,
    COUNT(CASE WHEN pr.rating = 4 THEN 1 END) AS four_star_count,
    COUNT(CASE WHEN pr.rating = 3 THEN 1 END) AS three_star_count,
    COUNT(CASE WHEN pr.rating = 2 THEN 1 END) AS two_star_count,
    COUNT(CASE WHEN pr.rating = 1 THEN 1 END) AS one_star_count
FROM products p
LEFT JOIN product_ratings pr ON p.id = pr.product_id
GROUP BY p.id, p.name, p.producer_id;

-- Producer rating summary view
CREATE OR REPLACE VIEW producer_rating_summary AS
SELECT 
    u.id AS producer_id,
    u.first_name || ' ' || u.last_name AS producer_name,
    COUNT(DISTINCT p.id) AS total_products,
    COUNT(pr.id) AS total_ratings,
    COALESCE(ROUND(AVG(pr.rating), 1), 0) AS average_rating
FROM users u
INNER JOIN products p ON u.id = p.producer_id
LEFT JOIN product_ratings pr ON p.id = pr.product_id
WHERE u.user_type = 'producer'
GROUP BY u.id, u.first_name, u.last_name;

--
