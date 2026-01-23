-- ============================================
-- SEASONAL BASKETS TABLE
-- ============================================
CREATE TABLE seasonal_baskets (
    id SERIAL PRIMARY KEY,
    producer_id INTEGER NOT NULL REFERENCES producers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
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
    cancelled_at TIMESTAMP
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