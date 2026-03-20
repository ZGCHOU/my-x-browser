-- Create Database
CREATE DATABASE IF NOT EXISTS icanx_db;
USE icanx_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    status ENUM('active', 'disabled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Licenses/Access Rights
CREATE TABLE IF NOT EXISTS licenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    expire_at DATETIME,
    max_profiles INT DEFAULT 5,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(255),
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tags Table (for user categorization)
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6366f1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. User Tags Relationship Table
CREATE TABLE IF NOT EXISTS user_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_tag (user_id, tag_id)
);

-- INSERT Initial Super Admin (username: admin, password: 123456 - Hash needs verification)
-- IMPORTANT: Use bcrypt.hash('123456', 10) in your script to generate actual hashed passwords.
-- For manual SQL insert, we just leave it for now.
INSERT INTO users (username, password, role) VALUES ('admin', '$2a$10$zW/.A86yIs7O14qkDX.cjOB8ik2gLCtOgZe.Un3cG/haAjAog/NMW', 'admin'); 
INSERT INTO `icanx_db`.`licenses` (`id`, `user_id`, `expire_at`, `max_profiles`, `balance`) VALUES (1, 1, '2099-12-31 23:59:59', 9999, 0.00);