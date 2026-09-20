-- =========================================================
-- VSB GARMENT MANUFACTURING COMPANY MANAGEMENT SYSTEM
-- Pure MySQL Relational Database Schema DDL
-- Database: vsb_garment_management
-- =========================================================

CREATE DATABASE IF NOT EXISTS `vsb_garment_management` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `vsb_garment_management`;

-- 1. Company Settings
CREATE TABLE IF NOT EXISTS `company_settings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `company_name` VARCHAR(150) NOT NULL DEFAULT 'VSB Garment Manufacturing',
    `opening_balance` DOUBLE NOT NULL DEFAULT 500000.00,
    `currency_symbol` VARCHAR(10) NOT NULL DEFAULT '₹',
    `phone` VARCHAR(30) DEFAULT '+91 98765 43210',
    `email` VARCHAR(100) DEFAULT 'contact@vsbgarments.com',
    `address` TEXT,
    `gstin` VARCHAR(50) DEFAULT '33AAACV1234F1Z5',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. System Users (Roles: Admin, Manager, Accountant)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` VARCHAR(20) NOT NULL DEFAULT 'Manager',
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120),
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Factory Workers (50-100 Capacity)
CREATE TABLE IF NOT EXISTS `workers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `worker_id` VARCHAR(30) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `department` VARCHAR(50) NOT NULL,
    `designation` VARCHAR(100) NOT NULL,
    `joining_date` DATE NOT NULL,
    `monthly_salary` DOUBLE NOT NULL DEFAULT 0.00,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Active',
    `address` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_workers_dept` (`department`),
    INDEX `idx_workers_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Finished Garment Products Catalog & Stock
CREATE TABLE IF NOT EXISTS `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` VARCHAR(30) NOT NULL UNIQUE,
    `name` VARCHAR(120) NOT NULL,
    `category` VARCHAR(60) NOT NULL,
    `size` VARCHAR(20) NOT NULL DEFAULT 'M',
    `material` VARCHAR(80) NOT NULL DEFAULT 'Cotton',
    `production_cost` DOUBLE NOT NULL DEFAULT 0.00,
    `selling_price` DOUBLE NOT NULL DEFAULT 0.00,
    `available_quantity` INT NOT NULL DEFAULT 0,
    `minimum_stock` INT NOT NULL DEFAULT 10,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Active',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_products_cat` (`category`),
    INDEX `idx_products_stock` (`available_quantity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Raw Materials Inventory
CREATE TABLE IF NOT EXISTS `raw_materials` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `material_id` VARCHAR(30) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `material_type` VARCHAR(50) NOT NULL DEFAULT 'Fabric',
    `supplier` VARCHAR(120) NOT NULL,
    `quantity` DOUBLE NOT NULL DEFAULT 0.00,
    `unit` VARCHAR(20) NOT NULL DEFAULT 'Meters',
    `cost_per_unit` DOUBLE NOT NULL DEFAULT 0.00,
    `total_cost` DOUBLE NOT NULL DEFAULT 0.00,
    `purchase_date` DATE NOT NULL,
    `stock_status` VARCHAR(30) NOT NULL DEFAULT 'In Stock',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Production Batches
CREATE TABLE IF NOT EXISTS `production` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `production_id` VARCHAR(30) NOT NULL UNIQUE,
    `product_id` INT NOT NULL,
    `production_date` DATE NOT NULL,
    `quantity_produced` INT NOT NULL DEFAULT 0,
    `worker_team` VARCHAR(120) NOT NULL,
    `raw_material_used` TEXT,
    `production_cost` DOUBLE NOT NULL DEFAULT 0.00,
    `quality_status` VARCHAR(30) NOT NULL DEFAULT 'Passed',
    `status` VARCHAR(30) NOT NULL DEFAULT 'In Progress',
    `remarks` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Sales Orders & Invoices
CREATE TABLE IF NOT EXISTS `sales` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `sale_id` VARCHAR(30) NOT NULL UNIQUE,
    `customer_name` VARCHAR(120) NOT NULL,
    `customer_phone` VARCHAR(25),
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `selling_price` DOUBLE NOT NULL DEFAULT 0.00,
    `total_amount` DOUBLE NOT NULL DEFAULT 0.00,
    `sale_date` DATE NOT NULL,
    `payment_status` VARCHAR(20) NOT NULL DEFAULT 'Paid',
    `payment_method` VARCHAR(30) NOT NULL DEFAULT 'Cash',
    `notes` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Income Streams
CREATE TABLE IF NOT EXISTS `income` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `income_id` VARCHAR(30) NOT NULL UNIQUE,
    `sale_id` INT NULL,
    `source_type` VARCHAR(50) NOT NULL DEFAULT 'Product Sales',
    `title` VARCHAR(150) NOT NULL,
    `amount` DOUBLE NOT NULL DEFAULT 0.00,
    `date` DATE NOT NULL,
    `payment_method` VARCHAR(30) NOT NULL DEFAULT 'Cash',
    `notes` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`sale_id`) REFERENCES `sales`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Worker Salaries
CREATE TABLE IF NOT EXISTS `salaries` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `salary_id` VARCHAR(30) NOT NULL UNIQUE,
    `worker_id` INT NOT NULL,
    `month` VARCHAR(20) NOT NULL,
    `basic_salary` DOUBLE NOT NULL DEFAULT 0.00,
    `bonus` DOUBLE NOT NULL DEFAULT 0.00,
    `deduction` DOUBLE NOT NULL DEFAULT 0.00,
    `net_salary` DOUBLE NOT NULL DEFAULT 0.00,
    `payment_date` DATE NULL,
    `payment_status` VARCHAR(20) NOT NULL DEFAULT 'Pending',
    `payment_method` VARCHAR(30) NOT NULL DEFAULT 'Bank Transfer',
    `notes` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_worker_month_salary` (`worker_id`, `month`),
    FOREIGN KEY (`worker_id`) REFERENCES `workers`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Statutory Taxes
CREATE TABLE IF NOT EXISTS `taxes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `tax_id` VARCHAR(30) NOT NULL UNIQUE,
    `tax_type` VARCHAR(60) NOT NULL,
    `tax_period` VARCHAR(50) NOT NULL,
    `tax_amount` DOUBLE NOT NULL DEFAULT 0.00,
    `due_date` DATE NOT NULL,
    `payment_date` DATE NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Pending',
    `notes` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Company Expenses
CREATE TABLE IF NOT EXISTS `expenses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `expense_id` VARCHAR(30) NOT NULL UNIQUE,
    `category` VARCHAR(60) NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `amount` DOUBLE NOT NULL DEFAULT 0.00,
    `date` DATE NOT NULL,
    `payment_method` VARCHAR(30) NOT NULL DEFAULT 'Cash',
    `salary_id` INT NULL,
    `tax_id` INT NULL,
    `material_id` INT NULL,
    `notes` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`salary_id`) REFERENCES `salaries`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`tax_id`) REFERENCES `taxes`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`material_id`) REFERENCES `raw_materials`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
