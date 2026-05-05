-- Cyber Backend Project — MySQL Schema
-- Run this file in MySQL to create the required tables.
-- Command: mysql -u root -p cyber_threat_detection < database_schema.sql

CREATE DATABASE IF NOT EXISTS cyber_threat_detection;
USE cyber_threat_detection;

CREATE TABLE IF NOT EXISTS usb_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usb_device_id VARCHAR(255),
    device_name VARCHAR(255),
    vendor_name VARCHAR(255),
    action_taken VARCHAR(255) NOT NULL,
    session_start DATETIME,
    session_end DATETIME,
    system_user VARCHAR(100),
    lock_until DATETIME NULL
);

CREATE TABLE IF NOT EXISTS file_access_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    system_user VARCHAR(100),
    file_path VARCHAR(500),
    action VARCHAR(255),
    timestamp DATETIME DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(60) NOT NULL
);
