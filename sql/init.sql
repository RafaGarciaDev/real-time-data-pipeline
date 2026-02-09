-- Criação do schema do banco de dados

-- Tabela de eventos
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de transações
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    event_id VARCHAR(100) REFERENCES events(event_id),
    product_id VARCHAR(100) REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de métricas agregadas
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 2) NOT NULL,
    metric_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_name, metric_date)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_product_id ON transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(metric_date);

-- View para análise de vendas por categoria
CREATE OR REPLACE VIEW sales_by_category AS
SELECT 
    p.category,
    COUNT(t.id) as total_transactions,
    SUM(t.quantity) as total_quantity,
    SUM(t.total_amount) as total_revenue,
    AVG(t.total_amount) as avg_transaction_value
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.category;

-- View para produtos mais vendidos
CREATE OR REPLACE VIEW top_products AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    COUNT(t.id) as total_sales,
    SUM(t.quantity) as total_quantity,
    SUM(t.total_amount) as total_revenue
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- View para métricas do dia
CREATE OR REPLACE VIEW daily_metrics AS
SELECT 
    DATE(timestamp) as date,
    COUNT(DISTINCT event_id) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as total_sessions,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as total_purchases
FROM events
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Função para calcular métricas agregadas
CREATE OR REPLACE FUNCTION update_daily_metrics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO metrics (metric_name, metric_value, metric_date)
    VALUES ('total_events', 1, CURRENT_DATE)
    ON CONFLICT (metric_name, metric_date)
    DO UPDATE SET metric_value = metrics.metric_value + 1;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar métricas automaticamente
DROP TRIGGER IF EXISTS trigger_update_metrics ON events;
CREATE TRIGGER trigger_update_metrics
AFTER INSERT ON events
FOR EACH ROW
EXECUTE FUNCTION update_daily_metrics();

-- Inserir dados de exemplo para produtos comuns
INSERT INTO products (product_id, product_name, category, price) VALUES
('PROD001', 'Laptop Dell XPS 15', 'Electronics', 1299.99),
('PROD002', 'iPhone 15 Pro', 'Electronics', 999.99),
('PROD003', 'Sony WH-1000XM5', 'Electronics', 399.99),
('PROD004', 'Kindle Paperwhite', 'Electronics', 139.99),
('PROD005', 'Nike Air Max', 'Fashion', 129.99),
('PROD006', 'Levi''s 501 Jeans', 'Fashion', 89.99),
('PROD007', 'The Great Gatsby Book', 'Books', 14.99),
('PROD008', 'Yoga Mat Premium', 'Sports', 49.99),
('PROD009', 'Coffee Maker Deluxe', 'Home', 79.99),
('PROD010', 'Gaming Chair RGB', 'Furniture', 299.99)
ON CONFLICT (product_id) DO NOTHING;

-- Comentários nas tabelas
COMMENT ON TABLE events IS 'Armazena todos os eventos capturados do pipeline';
COMMENT ON TABLE products IS 'Catálogo de produtos disponíveis';
COMMENT ON TABLE transactions IS 'Registro de todas as transações de compra';
COMMENT ON TABLE metrics IS 'Métricas agregadas para análise';
