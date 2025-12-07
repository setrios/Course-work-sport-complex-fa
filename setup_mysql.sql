-- ============================================
-- SQL скрипт для налаштування MySQL
-- База даних інтернет-магазину
-- ============================================

-- 1. Створення бази даних
CREATE DATABASE IF NOT EXISTS `sport-complex-cw` 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- 2. Створення користувача
CREATE USER IF NOT EXISTS 'sport-complex-cw'@'127.0.0.1' 
  IDENTIFIED BY 'sport-complex-cw';

-- 3. Надання прав доступу
GRANT ALL PRIVILEGES ON `sport-complex-cw`.* 
  TO 'sport-complex-cw'@'127.0.0.1';

FLUSH PRIVILEGES;

-- 4. Використання бази
USE `sport-complex-cw`;

-- ============================================
-- Таблиці створюються автоматично через SQLAlchemy
-- при запуску програми (Base.metadata.create_all)
-- ============================================

-- Але для довідки, структура таблиць:

-- Таблиця постачальників
-- CREATE TABLE suppliers (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(100) UNIQUE NOT NULL,
--     city VARCHAR(100),
--     country VARCHAR(100),
--     contact_email VARCHAR(100)
-- );

-- Таблиця категорій
-- CREATE TABLE categories (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(100) UNIQUE NOT NULL
-- );

-- Таблиця товарів
-- CREATE TABLE products (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     article VARCHAR(50) UNIQUE NOT NULL,
--     name VARCHAR(200) NOT NULL,
--     category_id INT,
--     supplier_id INT,
--     price INT NOT NULL,
--     quantity INT DEFAULT 0,
--     min_stock INT DEFAULT 10,
--     delivery_days INT DEFAULT 7,
--     image_doc_id VARCHAR(100),
--     FOREIGN KEY (category_id) REFERENCES categories(id),
--     FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
--     INDEX idx_article (article)
-- );

-- Таблиця замовлень
-- CREATE TABLE orders (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     supplier_id INT,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     status VARCHAR(50) DEFAULT 'pending',
--     FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
-- );

-- Таблиця позицій замовлення
-- CREATE TABLE order_items (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     order_id INT,
--     product_id INT,
--     quantity INT NOT NULL,
--     FOREIGN KEY (order_id) REFERENCES orders(id),
--     FOREIGN KEY (product_id) REFERENCES products(id)
-- );

-- ============================================
-- Корисні запити для адміністрування
-- ============================================

-- Перевірка таблиць
SHOW TABLES;

-- Структура таблиці products
DESCRIBE products;

-- Перелік всіх товарів з інформацією про постачальника
SELECT 
    p.article,
    p.name AS product_name,
    p.quantity,
    p.price / 100.0 AS price_uah,
    s.name AS supplier,
    s.city,
    c.name AS category
FROM products p
LEFT JOIN suppliers s ON p.supplier_id = s.id
LEFT JOIN categories c ON p.category_id = c.id;

-- Товари з низьким запасом
SELECT 
    article,
    name,
    quantity,
    min_stock,
    (min_stock - quantity) AS shortage
FROM products
WHERE quantity < min_stock
ORDER BY shortage DESC;

-- Статистика по постачальникам
SELECT 
    s.name AS supplier,
    s.city,
    COUNT(p.id) AS total_products,
    SUM(p.quantity) AS total_quantity,
    SUM(p.price * p.quantity) / 100.0 AS total_value_uah
FROM suppliers s
LEFT JOIN products p ON s.id = p.supplier_id
GROUP BY s.id, s.name, s.city
ORDER BY total_products DESC;

-- Статистика по категоріях
SELECT 
    c.name AS category,
    COUNT(p.id) AS product_count,
    SUM(p.quantity) AS total_quantity,
    AVG(p.price) / 100.0 AS avg_price_uah
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
GROUP BY c.id, c.name
ORDER BY product_count DESC;

-- Топ-10 найдорожчих товарів
SELECT 
    article,
    name,
    price / 100.0 AS price_uah,
    quantity
FROM products
ORDER BY price DESC
LIMIT 10;

-- Топ-10 товарів з найбільшим запасом
SELECT 
    article,
    name,
    quantity,
    price / 100.0 AS price_uah
FROM products
ORDER BY quantity DESC
LIMIT 10;

-- Очищення таблиць (ОБЕРЕЖНО!)
-- TRUNCATE TABLE order_items;
-- TRUNCATE TABLE orders;
-- TRUNCATE TABLE products;
-- TRUNCATE TABLE categories;
-- TRUNCATE TABLE suppliers;
