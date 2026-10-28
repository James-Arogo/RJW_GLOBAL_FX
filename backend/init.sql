-- Initialize PostgreSQL database for RJW GLOBAL FX
-- This script runs when the database container starts

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS forex_db;

-- Connect to the database
\c forex_db;

-- Create extensions for enhanced functionality
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create indexes for better performance
-- These will be created by SQLAlchemy but we can add additional ones

-- Create user for application
CREATE USER IF NOT EXISTS forex_user WITH PASSWORD 'forex_password';
GRANT ALL PRIVILEGES ON DATABASE forex_db TO forex_user;

-- Set default permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO forex_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO forex_user;
