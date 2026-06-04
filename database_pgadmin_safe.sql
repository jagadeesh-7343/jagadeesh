-- Production-Ready PostgreSQL Schema for Citizen Bridge
-- Created: 2026-02-24

-- ============================================
-- CITIZENS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS citizens (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    aadhar_number VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried columns (safe for repeated runs)
CREATE INDEX IF NOT EXISTS idx_citizens_email ON citizens(email);
CREATE INDEX IF NOT EXISTS idx_citizens_aadhar ON citizens(aadhar_number);
CREATE INDEX IF NOT EXISTS idx_citizens_created_at ON citizens(created_at);
CREATE INDEX IF NOT EXISTS idx_citizens_username ON citizens(username);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    email VARCHAR(255),
    phone VARCHAR(20),
    head_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name);

-- ============================================
-- DEPARTMENT COMPLAINT TABLES (one per sector)
-- ============================================
CREATE TABLE IF NOT EXISTS complaints_education (
    id SERIAL PRIMARY KEY,
    aadhaar VARCHAR(12),
    phone VARCHAR(10),
    address TEXT,
    mandal VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(6),
    problem_description TEXT,
    proof_image VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints_police (
    id SERIAL PRIMARY KEY,
    aadhaar VARCHAR(12),
    phone VARCHAR(10),
    address TEXT,
    mandal VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(6),
    problem_description TEXT,
    proof_image VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints_health (
    id SERIAL PRIMARY KEY,
    aadhaar VARCHAR(12),
    phone VARCHAR(10),
    address TEXT,
    mandal VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(6),
    problem_description TEXT,
    proof_image VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints_electrical (
    id SERIAL PRIMARY KEY,
    aadhaar VARCHAR(12),
    phone VARCHAR(10),
    address TEXT,
    mandal VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(6),
    problem_description TEXT,
    proof_image VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints_transport (
    id SERIAL PRIMARY KEY,
    aadhaar VARCHAR(12),
    phone VARCHAR(10),
    address TEXT,
    mandal VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(6),
    problem_description TEXT,
    proof_image VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
