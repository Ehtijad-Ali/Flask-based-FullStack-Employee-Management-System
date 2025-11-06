-- schema.sql
CREATE DATABASE IF NOT EXISTS employees
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE employees;

CREATE TABLE IF NOT EXISTS employees (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(30),
  gender ENUM('Male','Female','Other','Prefer not to say') DEFAULT NULL,
  dob DATE,
  department VARCHAR(100),
  position VARCHAR(100),
  hire_date DATE,
  salary DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  city VARCHAR(100),
  address TEXT,
  status ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_department (department),
  INDEX idx_status (status),
  INDEX idx_name (last_name, first_name)
) ENGINE=InnoDB;