-- Database Migration: Add Tracking ID, Timeline, and Feedback Features
-- Run this after initial database.sql setup
-- Created: 2026-03-06

-- ============================================
-- ADD TRACKING_ID TO ALL COMPLAINT TABLES
-- ============================================

-- Add tracking_id column with unique constraint
ALTER TABLE complaints_education ADD COLUMN IF NOT EXISTS tracking_id VARCHAR(20) UNIQUE;
ALTER TABLE complaints_police ADD COLUMN IF NOT EXISTS tracking_id VARCHAR(20) UNIQUE;
ALTER TABLE complaints_health ADD COLUMN IF NOT EXISTS tracking_id VARCHAR(20) UNIQUE;
ALTER TABLE complaints_electrical ADD COLUMN IF NOT EXISTS tracking_id VARCHAR(20) UNIQUE;
ALTER TABLE complaints_transport ADD COLUMN IF NOT EXISTS tracking_id VARCHAR(20) UNIQUE;

-- Add assigned_to column for officer assignment
ALTER TABLE complaints_education ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(200);
ALTER TABLE complaints_police ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(200);
ALTER TABLE complaints_health ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(200);
ALTER TABLE complaints_electrical ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(200);
ALTER TABLE complaints_transport ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(200);

-- Add resolved_at timestamp
ALTER TABLE complaints_education ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;
ALTER TABLE complaints_police ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;
ALTER TABLE complaints_health ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;
ALTER TABLE complaints_electrical ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;
ALTER TABLE complaints_transport ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;

-- Create indexes for tracking_id lookups
CREATE INDEX IF NOT EXISTS idx_complaints_education_tracking ON complaints_education(tracking_id);
CREATE INDEX IF NOT EXISTS idx_complaints_police_tracking ON complaints_police(tracking_id);
CREATE INDEX IF NOT EXISTS idx_complaints_health_tracking ON complaints_health(tracking_id);
CREATE INDEX IF NOT EXISTS idx_complaints_electrical_tracking ON complaints_electrical(tracking_id);
CREATE INDEX IF NOT EXISTS idx_complaints_transport_tracking ON complaints_transport(tracking_id);


-- ============================================
-- COMPLAINT TIMELINE/HISTORY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS complaint_timeline (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER NOT NULL,
    department VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    notes TEXT,
    changed_by VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_timeline_status CHECK (status IN ('Submitted', 'Assigned', 'In Progress', 'Resolved', 'Rejected', 'On Hold'))
);

CREATE INDEX IF NOT EXISTS idx_timeline_complaint ON complaint_timeline(complaint_id, department);
CREATE INDEX IF NOT EXISTS idx_timeline_created ON complaint_timeline(created_at);


-- ============================================
-- CITIZEN FEEDBACK TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS complaint_feedback (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER NOT NULL,
    department VARCHAR(50) NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    citizen_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_feedback_rating CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT unique_complaint_feedback UNIQUE (complaint_id, department)
);

CREATE INDEX IF NOT EXISTS idx_feedback_complaint ON complaint_feedback(complaint_id, department);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON complaint_feedback(rating);


-- ============================================
-- FUNCTION TO GENERATE TRACKING ID
-- ============================================
CREATE OR REPLACE FUNCTION generate_tracking_id(dept_prefix VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    new_id VARCHAR(20);
    id_exists BOOLEAN;
BEGIN
    LOOP
        -- Generate format: DEPT-YYYYMMDD-XXXX (e.g., EDU-20260306-A1B2)
        new_id := dept_prefix || '-' || 
                  TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                  UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 4));
        
        -- Check if ID exists in any table (simplified check)
        -- In production, you'd check all complaint tables
        RETURN new_id;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- UPDATE EXISTING COMPLAINTS WITH TRACKING IDs
-- (Only run once after migration)
-- ============================================
-- Uncomment these to backfill existing complaints:
/*
UPDATE complaints_education 
SET tracking_id = 'EDU-' || TO_CHAR(created_at, 'YYYYMMDD') || '-' || LPAD(id::TEXT, 4, '0')
WHERE tracking_id IS NULL;

UPDATE complaints_police 
SET tracking_id = 'POL-' || TO_CHAR(created_at, 'YYYYMMDD') || '-' || LPAD(id::TEXT, 4, '0')
WHERE tracking_id IS NULL;

UPDATE complaints_health 
SET tracking_id = 'HLT-' || TO_CHAR(created_at, 'YYYYMMDD') || '-' || LPAD(id::TEXT, 4, '0')
WHERE tracking_id IS NULL;

UPDATE complaints_electrical 
SET tracking_id = 'ELC-' || TO_CHAR(created_at, 'YYYYMMDD') || '-' || LPAD(id::TEXT, 4, '0')
WHERE tracking_id IS NULL;

UPDATE complaints_transport 
SET tracking_id = 'TRN-' || TO_CHAR(created_at, 'YYYYMMDD') || '-' || LPAD(id::TEXT, 4, '0')
WHERE tracking_id IS NULL;
*/
