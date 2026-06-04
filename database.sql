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

-- Create indexes for frequently queried columns
CREATE INDEX idx_citizens_email ON citizens(email);
CREATE INDEX idx_citizens_aadhar ON citizens(aadhar_number);
CREATE INDEX idx_citizens_created_at ON citizens(created_at);
CREATE INDEX idx_citizens_username ON citizens(username);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    email VARCHAR(255),
    phone VARCHAR(20),
    head_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departments_name ON departments(name);

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
-- Insert 5 fixed departments (health, transport, electrical, police, education)
INSERT INTO departments (name, description, email, phone, head_name) 
VALUES 
    ('Police', 'Law enforcement, safety, and crime prevention', 'police@city.gov', '1800-POLICE-1', 'Rajesh Kumar'),
    ('Health & Sanitation', 'Handles health, sanitation, and waste management issues', 'health@city.gov', '1800-HEALTH-1', 'Dr. Priya Singh'),
    ('Transport', 'Manages traffic, roads, and public transportation', 'transport@city.gov', '1800-TRANSPORT-1', 'Amit Patel'),
    ('Education', 'Manages schools, colleges, and educational institutions', 'education@city.gov', '1800-EDU-1', 'Vikram Sharma'),
    ('Electrical', 'Handles power supply and electrical infrastructure', 'electrical@city.gov', '1800-POWER-1', 'Deepak Verma')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- DEPARTMENT OFFICERS / STAFF TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS department_officers (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    officer_name VARCHAR(200) NOT NULL,
    department_code VARCHAR(100) NOT NULL,
    department_id INTEGER,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_officer_department FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_officers_dept_code ON department_officers(department_code);
CREATE INDEX IF NOT EXISTS idx_officers_username ON department_officers(username);

-- ============================================
-- COMPLAINTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Accepted' NOT NULL,
    priority VARCHAR(20),
    location VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    attachment_url VARCHAR(255),
    ai_summary TEXT,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_complaints_citizen FOREIGN KEY (citizen_id) 
        REFERENCES citizens(id) ON DELETE CASCADE,
    CONSTRAINT fk_complaints_department FOREIGN KEY (department_id) 
        REFERENCES departments(id) ON DELETE SET NULL,
    
    -- Data Validation Constraints
    CONSTRAINT chk_complaint_status CHECK (status IN ('Accepted', 'In Progress', 'Resolved', 'Rejected', 'On Hold')),
    CONSTRAINT chk_complaint_priority CHECK (priority IN ('Low', 'Medium', 'High', 'Critical'))
);

-- Create indexes for performance optimization
CREATE INDEX idx_complaints_citizen_id ON complaints(citizen_id);
CREATE INDEX idx_complaints_department_id ON complaints(department_id);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_created_at ON complaints(created_at);
CREATE INDEX idx_complaints_updated_at ON complaints(updated_at);
CREATE INDEX idx_complaints_priority ON complaints(priority);

-- ============================================
-- AUDIT LOG TABLE (Production Best Practice)
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for audit queries
CREATE INDEX idx_audit_logs_record_id ON audit_logs(record_id);
CREATE INDEX idx_audit_logs_changed_at ON audit_logs(changed_at);

-- ============================================
-- COMMENTS TABLE (For Department Feedback)
-- ============================================
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_comments_complaint FOREIGN KEY (complaint_id) 
        REFERENCES complaints(id) ON DELETE CASCADE,
    CONSTRAINT fk_comments_author FOREIGN KEY (author_id) 
        REFERENCES citizens(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_comments_complaint_id ON comments(complaint_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);

-- ============================================
-- MATERIALIZED VIEW FOR REPORTING
-- ============================================
CREATE MATERIALIZED VIEW IF NOT EXISTS complaint_statistics AS
SELECT 
    d.id,
    d.name as department_name,
    COUNT(c.id) as total_complaints,
    COUNT(CASE WHEN c.status = 'Resolved' THEN 1 END) as resolved_count,
    COUNT(CASE WHEN c.status = 'In Progress' THEN 1 END) as in_progress_count,
    COUNT(CASE WHEN c.status = 'Rejected' THEN 1 END) as rejected_count,
    ROUND(100.0 * COUNT(CASE WHEN c.status = 'Resolved' THEN 1 END) / 
        NULLIF(COUNT(c.id), 0), 2) as resolution_rate
FROM departments d
LEFT JOIN complaints c ON d.id = c.department_id
GROUP BY d.id, d.name;

CREATE INDEX idx_complaint_statistics_dept_id ON complaint_statistics(id);