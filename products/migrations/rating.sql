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