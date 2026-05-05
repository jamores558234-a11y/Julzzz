-- Create Database
CREATE DATABASE IF NOT EXISTS car_aircon_db;
USE car_aircon_db;

-- Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Staff', 'Mechanic') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    contact VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers Table (split name into 3 fields)
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    last_name VARCHAR(50) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vehicles Table
CREATE TABLE vehicles (
    vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    model VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    year INT,
    color VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Services Table
CREATE TABLE services (
    service_id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_id INT NOT NULL,
    mechanic_id INT,
    issue_complaint TEXT NOT NULL,
    status ENUM('Pending', 'Ongoing', 'Completed') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (mechanic_id) REFERENCES users(user_id)
);

-- Repairs Table
CREATE TABLE repairs (
    repair_id INT PRIMARY KEY AUTO_INCREMENT,
    service_id INT NOT NULL,
    diagnosis_result TEXT,
    repair_actions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
);

-- Inventory Table
CREATE TABLE inventory (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100) NOT NULL,
    quantity_available INT NOT NULL DEFAULT 0,
    minimum_threshold INT DEFAULT 5,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Stock In Table
CREATE TABLE stock_in (
    stock_in_id INT PRIMARY KEY AUTO_INCREMENT,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    supplier VARCHAR(100) NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES inventory(item_id) ON DELETE CASCADE
);

-- Stock Out Table
CREATE TABLE stock_out (
    stock_out_id INT PRIMARY KEY AUTO_INCREMENT,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES inventory(item_id) ON DELETE CASCADE
);

-- Service Parts Table
CREATE TABLE service_parts (
    service_part_id INT PRIMARY KEY AUTO_INCREMENT,
    service_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity_used INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES inventory(item_id) ON DELETE CASCADE
);

-- Billing Table
CREATE TABLE billing (
    billing_id INT PRIMARY KEY AUTO_INCREMENT,
    service_id INT NOT NULL,
    parts_cost DECIMAL(10, 2) NOT NULL DEFAULT 0,
    labor_fee DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('Pending', 'Paid', 'Partial') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
);

-- Payments Table
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    billing_id INT NOT NULL,
    amount_paid DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (billing_id) REFERENCES billing(billing_id) ON DELETE CASCADE
);

-- Sample Data
INSERT INTO users (username, password, role, full_name, contact) VALUES
('admin', 'admin123', 'Admin', 'Administrator', '0912345678'),
('staff1', 'staff123', 'Staff', 'John Staff', '0912345679'),
('mech1', 'mech123', 'Mechanic', 'Mike Mechanic', '0912345680');

INSERT INTO customers (first_name, middle_name, last_name, contact, email, address) VALUES
('Juan', 'Reyes', 'dela Cruz', '0912345678', 'juan@example.com', '123 Main St'),
('Maria', 'Lopez', 'Santos', '0912345679', 'maria@example.com', '456 Oak Ave'),
('Jose', 'Miguel', 'Garcia', '0912345680', 'jose@example.com', '789 Pine Rd');

INSERT INTO vehicles (customer_id, plate_number, model, type, year, color) VALUES
(1, 'ABC-1234', 'Toyota Camry', 'Sedan', 2020, 'Silver'),
(2, 'DEF-5678', 'Honda CR-V', 'SUV', 2021, 'Black'),
(3, 'GHI-9012', 'Mitsubishi Mirage', 'Hatchback', 2019, 'White');

INSERT INTO inventory (item_name, quantity_available, minimum_threshold, unit_price) VALUES
('Refrigerant R134a', 20, 5, 500.00),
('Compressor Oil', 15, 3, 800.00),
('Air Filter', 30, 10, 200.00),
('Condenser', 8, 2, 5000.00),
('Evaporator', 5, 2, 4500.00);