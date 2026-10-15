CREATE DATABASE IF NOT EXISTS logistics_exception_db;
USE logistics_exception_db;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(120) NOT NULL,
    customer_type ENUM('Retail','SMB','Enterprise') NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(80) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hubs (
    hub_id VARCHAR(20) PRIMARY KEY,
    hub_name VARCHAR(120) NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(80) NOT NULL,
    region VARCHAR(40) NOT NULL,
    congestion_level ENUM('Low','Medium','High') NOT NULL,
    capacity_kgs DECIMAL(10,2) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE carriers (
    carrier_id VARCHAR(20) PRIMARY KEY,
    carrier_name VARCHAR(120) NOT NULL,
    carrier_type ENUM('Express','Ground','Air','Regional') NOT NULL,
    on_time_rate DECIMAL(5,2) NOT NULL,
    avg_delay_hours DECIMAL(6,2) NOT NULL,
    fleet_size INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shipments (
    shipment_id VARCHAR(25) PRIMARY KEY,
    customer_id INT NOT NULL,
    carrier_id VARCHAR(20) NOT NULL,
    origin_hub_id VARCHAR(20) NOT NULL,
    destination_hub_id VARCHAR(20) NOT NULL,
    shipment_type VARCHAR(40) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    weight_kg DECIMAL(10,2) NOT NULL,
    distance_km INT NOT NULL,
    sla_hours INT NOT NULL,
    planned_delivery_datetime DATETIME NOT NULL,
    actual_delivery_datetime DATETIME NULL,
    status VARCHAR(30) NOT NULL,
    delay_flag TINYINT(1) NOT NULL DEFAULT 0,
    sla_breach TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id),
    FOREIGN KEY (origin_hub_id) REFERENCES hubs(hub_id),
    FOREIGN KEY (destination_hub_id) REFERENCES hubs(hub_id),
    INDEX idx_shipments_customer (customer_id),
    INDEX idx_shipments_carrier (carrier_id),
    INDEX idx_shipments_hubs (origin_hub_id, destination_hub_id),
    INDEX idx_shipments_status (status),
    INDEX idx_shipments_delay (delay_flag),
    INDEX idx_shipments_sla (sla_breach)
);

CREATE TABLE exceptions (
    exception_id INT PRIMARY KEY AUTO_INCREMENT,
    shipment_id VARCHAR(25) NOT NULL,
    exception_reason VARCHAR(80) NOT NULL,
    exception_type VARCHAR(40) NOT NULL,
    severity ENUM('Low','Medium','High','Critical') NOT NULL,
    status ENUM('Open','Assigned','In Progress','Resolved','Closed') NOT NULL DEFAULT 'Open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    assigned_to VARCHAR(80) NULL,
    notes TEXT,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id),
    INDEX idx_exceptions_shipment (shipment_id),
    INDEX idx_exceptions_reason (exception_reason),
    INDEX idx_exceptions_status (status)
);

CREATE TABLE shipment_status_history (
    status_history_id INT PRIMARY KEY AUTO_INCREMENT,
    shipment_id VARCHAR(25) NOT NULL,
    status VARCHAR(30) NOT NULL,
    status_timestamp DATETIME NOT NULL,
    remarks TEXT,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id),
    INDEX idx_status_history_shipment (shipment_id),
    INDEX idx_status_history_timestamp (status_timestamp)
);

CREATE VIEW shipment_kpi_summary AS
SELECT
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN delay_flag = 1 THEN 1 ELSE 0 END) AS delayed_shipments,
    AVG(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS on_time_delivery_rate,
    SUM(CASE WHEN sla_breach = 1 THEN 1 ELSE 0 END) / COUNT(*) AS sla_breach_rate
FROM shipments;
