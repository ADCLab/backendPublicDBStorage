#!/bin/bash

# Set the username and password for the new user
NEW_USER='api_key_manager'
NEW_PASSWORD=${MYSQL_API_KEY_MANAGER_PASSWORD:-'api_password'}

echo "Creating user: $NEW_USER"

# Create the SQL script dynamically
cat <<EOF > /docker-entrypoint-initdb.d/init.sql
-- Create database
CREATE DATABASE IF NOT EXISTS api_tracking;
SELECT 'Created api_tracking database' AS message;

-- Use the database
USE api_tracking;

-- Create table to store API keys with an expires_at column
CREATE TABLE IF NOT EXISTS api_tracking.api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
SELECT 'Created api_tracking.api_keys table with expires_at column' AS message;

-- Create the new user and grant permissions
CREATE USER IF NOT EXISTS '$NEW_USER'@'%' IDENTIFIED BY '$NEW_PASSWORD';
GRANT ALL PRIVILEGES ON api_tracking.* TO '$NEW_USER'@'%';
FLUSH PRIVILEGES;
SELECT 'Created new user and granted privileges' AS message;

-- Create an event to delete expired API keys
DELIMITER //
CREATE EVENT IF NOT EXISTS delete_expired_keys
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    DELETE FROM api_keys WHERE expires_at < NOW();
END;
//
DELIMITER ;
SELECT 'Created event to delete expired keys' AS message;

-- Enable event scheduler
SET GLOBAL event_scheduler = ON;
SELECT 'Enabled event scheduler' AS message;
EOF

# Ensure correct file permissions
chmod 644 /docker-entrypoint-initdb.d/init.sql

echo "Created SQL initialization script with correct permissions"

# Start the MySQL server
echo "Starting MySQL server..."
exec docker-entrypoint.sh mysqld
