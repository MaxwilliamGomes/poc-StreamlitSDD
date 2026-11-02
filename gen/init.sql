-- ShopAgent Dashboard: schema final (customers, products, orders, reviews)
-- Executado por src/prepare_data.py e pelos testes de integração.

CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    city        VARCHAR(100),
    state       CHAR(2) NOT NULL,
    segment     VARCHAR(20) NOT NULL CHECK (segment IN ('premium', 'standard', 'basic'))
);

CREATE TABLE IF NOT EXISTS products (
    product_id     UUID PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    category       VARCHAR(100) NOT NULL,
    macro_category VARCHAR(50) NOT NULL,
    price          DECIMAL(10,2) NOT NULL CHECK (price > 0),
    brand          VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id    UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    product_id  UUID NOT NULL REFERENCES products(product_id),
    qty         INTEGER NOT NULL CHECK (qty BETWEEN 1 AND 10),
    total       DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    status      VARCHAR(20) NOT NULL CHECK (status IN ('delivered', 'shipped', 'processing', 'cancelled')),
    payment     VARCHAR(20) NOT NULL CHECK (payment IN ('pix', 'credit_card', 'boleto')),
    created_at  TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id UUID PRIMARY KEY,
    order_id  UUID NOT NULL UNIQUE REFERENCES orders(order_id),
    rating    SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment   TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('positive', 'neutral', 'negative'))
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product_id  ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_status      ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at  ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_customers_state    ON customers(state);
CREATE INDEX IF NOT EXISTS idx_products_macro     ON products(macro_category);
