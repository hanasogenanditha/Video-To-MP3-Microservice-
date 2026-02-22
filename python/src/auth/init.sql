-- Create user (Docker-safe)
CREATE USER IF NOT EXISTS 'auth_user'@'%' IDENTIFIED BY 'Auth123';

-- Create database
CREATE DATABASE IF NOT EXISTS auth;

-- Grant privileges
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'%';
FLUSH PRIVILEGES;

-- Use database
USE auth;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Insert test user
INSERT INTO users (email, password)
VALUES ('hanasogenanditha@gmail.com', 'Admin123');
  
