CREATE DATABASE IF NOT EXISTS spendwise_db;
USE spendwise_db;

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    type ENUM('Income','Expense') NOT NULL DEFAULT 'Expense'
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    description VARCHAR(180) NOT NULL,
    category_id INT NULL,
    transaction_type ENUM('Income','Expense') NOT NULL DEFAULT 'Expense',
    amount DECIMAL(12,2) NOT NULL,
    archived TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transaction_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS profile (
    profile_id INT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL DEFAULT 'Juan Dela Cruz',
    phone VARCHAR(30) DEFAULT '',
    birth_date DATE NULL
);

INSERT IGNORE INTO categories (name, type) VALUES
('Housing','Expense'), ('Food','Expense'), ('Transport','Expense'),
('Utilities','Expense'), ('Entertainment','Expense'), ('Shopping','Expense'),
('Health','Expense'), ('Education','Expense'), ('Other','Expense'),
('Salary','Income'), ('Allowance','Income'), ('Freelance','Income');

INSERT IGNORE INTO profile (profile_id, full_name, phone, birth_date)
VALUES (1, 'Juan Dela Cruz', '09758496213', '2003-06-20');
