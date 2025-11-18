-- schema.sql
-- Schema for Online Bookstore project

-- Create database (run once; skip if you already created it manually)
CREATE DATABASE IF NOT EXISTS online_bookstore
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE online_bookstore;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;

-- =========================
-- 1. Users
-- =========================

CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('customer','manager') NOT NULL DEFAULT 'customer',
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- 2. Books
-- =========================

CREATE TABLE books (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    author      VARCHAR(255) NOT NULL,
    price_buy   DECIMAL(8,2) NOT NULL,
    price_rent  DECIMAL(8,2) NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- Simple index to speed up searches by title/author
    INDEX idx_books_title_author (title, author)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- 3. Orders
-- =========================

CREATE TABLE orders (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id        INT UNSIGNED NOT NULL,
    total_price    DECIMAL(10,2) NOT NULL,
    payment_status ENUM('Pending','Paid') NOT NULL DEFAULT 'Pending',
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_user
      FOREIGN KEY (user_id) REFERENCES users(id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,

    INDEX idx_orders_user (user_id),
    INDEX idx_orders_status (payment_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- 4. Order Items
-- =========================

CREATE TABLE order_items (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id   INT UNSIGNED NOT NULL,
    book_id    INT UNSIGNED NOT NULL,
    type       ENUM('buy','rent') NOT NULL,
    price      DECIMAL(8,2) NOT NULL,  -- price at time of order
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_order_items_order
      FOREIGN KEY (order_id) REFERENCES orders(id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,

    CONSTRAINT fk_order_items_book
      FOREIGN KEY (book_id) REFERENCES books(id)
      ON DELETE RESTRICT
      ON UPDATE CASCADE,

    INDEX idx_order_items_order (order_id),
    INDEX idx_order_items_book (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
