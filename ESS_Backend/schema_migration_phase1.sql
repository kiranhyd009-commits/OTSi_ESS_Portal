-- ============================================================
-- PHASE 1: DATABASE SCHEMA MIGRATION
-- OTSI ESS Portal - Super Admin & Organizational Structure
-- ============================================================
-- This migration adds:
-- 1. New SUPER_ADMIN role support
-- 2. Departments, Teams, Projects, Clients tables
-- 3. Employee-Team mapping
-- 4. Attendance Corrections workflow
-- 5. New Employee Requests tracking
-- ============================================================

-- ─────────────────────────────────────────────────────────
-- 1. UPDATE EMPLOYEES TABLE - Add organizational structure columns
-- ─────────────────────────────────────────────────────────
-- Note: Role remains as: 'employee', 'hr', 'admin'
-- The admin role will have super admin access (admin.otsi@otsi-usa.com will be OTSI0001)

-- Add department_id column if it doesn't exist (for better org structure)
ALTER TABLE employees ADD COLUMN IF NOT EXISTS department_id INT;

-- Add team_id column for team assignment
ALTER TABLE employees ADD COLUMN IF NOT EXISTS team_id INT;

-- Add client_id column for client assignment (external consultants)
ALTER TABLE employees ADD COLUMN IF NOT EXISTS client_id INT;

-- Add is_active column (to track active/inactive separately from status)
ALTER TABLE employees ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- ─────────────────────────────────────────────────────────
-- 2. CREATE CLIENTS TABLE
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    contact_person VARCHAR(150),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    location VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name);

-- ─────────────────────────────────────────────────────────
-- 3. CREATE DEPARTMENTS TABLE
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    manager_id VARCHAR(50),
    hr_manager_id VARCHAR(50),
    location VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (hr_manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_departments_status ON departments(status);
CREATE INDEX IF NOT EXISTS idx_departments_manager_id ON departments(manager_id);
CREATE INDEX IF NOT EXISTS idx_departments_hr_manager_id ON departments(hr_manager_id);

-- ─────────────────────────────────────────────────────────
-- 4. CREATE TEAMS TABLE
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    department_id INT NOT NULL,
    team_lead_id VARCHAR(50),
    hr_manager_id VARCHAR(50),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, department_id),
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    FOREIGN KEY (team_lead_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (hr_manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_teams_department_id ON teams(department_id);
CREATE INDEX IF NOT EXISTS idx_teams_team_lead_id ON teams(team_lead_id);
CREATE INDEX IF NOT EXISTS idx_teams_status ON teams(status);

-- ─────────────────────────────────────────────────────────
-- 5. CREATE PROJECTS TABLE
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    client_id INT,
    team_id INT,
    project_lead_id VARCHAR(50),
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'on_hold', 'completed', 'archived')),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (project_lead_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_projects_client_id ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_team_id ON projects(team_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_project_lead_id ON projects(project_lead_id);

-- ─────────────────────────────────────────────────────────
-- 6. CREATE EMPLOYEE_TEAMS JUNCTION TABLE
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS employee_teams (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    team_id INT NOT NULL,
    role VARCHAR(50),
    assigned_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, team_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_employee_teams_employee_id ON employee_teams(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_teams_team_id ON employee_teams(team_id);

-- ─────────────────────────────────────────────────────────
-- 7. CREATE ATTENDANCE_CORRECTIONS TABLE
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance_corrections (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    attendance_date DATE NOT NULL,
    correction_type VARCHAR(50) NOT NULL CHECK (correction_type IN ('check_in', 'check_out', 'status', 'full_day')),
    old_check_in_time TIMESTAMP,
    new_check_in_time TIMESTAMP,
    old_check_out_time TIMESTAMP,
    new_check_out_time TIMESTAMP,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    reason TEXT NOT NULL,
    requested_by VARCHAR(50) NOT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    approved_by VARCHAR(50),
    approval_comments TEXT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES employees(employee_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_attendance_corrections_employee_id ON attendance_corrections(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_corrections_status ON attendance_corrections(status);
CREATE INDEX IF NOT EXISTS idx_attendance_corrections_date ON attendance_corrections(attendance_date);
CREATE INDEX IF NOT EXISTS idx_attendance_corrections_employee_date ON attendance_corrections(employee_id, attendance_date);

-- ─────────────────────────────────────────────────────────
-- 8. CREATE NEW_EMPLOYEE_REQUESTS TABLE
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS new_employee_requests (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    designation VARCHAR(100),
    department_id INT,
    team_id INT,
    manager_id VARCHAR(50),
    date_of_joining DATE,
    reason TEXT,
    requested_by VARCHAR(50),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    approved_by VARCHAR(50),
    approval_comments TEXT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (requested_by) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES employees(employee_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_new_employee_requests_status ON new_employee_requests(status);
CREATE INDEX IF NOT EXISTS idx_new_employee_requests_employee_id ON new_employee_requests(employee_id);

-- ─────────────────────────────────────────────────────────
-- 9. CREATE APPROVAL_WORKFLOWS TABLE (Generic approval tracking)
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS approval_workflows (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('leave', 'attendance_correction', 'new_employee', 'expense', 'request')),
    entity_id INT NOT NULL,
    current_approver_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'escalated')),
    approval_level INT DEFAULT 1,
    max_approval_level INT DEFAULT 2,
    approval_date TIMESTAMP,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_approver_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_approval_workflows_entity ON approval_workflows(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_approval_workflows_status ON approval_workflows(status);
CREATE INDEX IF NOT EXISTS idx_approval_workflows_approver ON approval_workflows(current_approver_id);

-- ─────────────────────────────────────────────────────────
-- 10. ADD FOREIGN KEY CONSTRAINTS TO EMPLOYEES TABLE
-- ─────────────────────────────────────────────────────────
ALTER TABLE employees ADD CONSTRAINT fk_employees_department_id
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_employees_team_id
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_employees_client_id
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL;

-- ─────────────────────────────────────────────────────────
-- 11. CREATE VIEW FOR ORGANIZATIONAL HIERARCHY
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_org_hierarchy AS
SELECT
    d.id as dept_id,
    d.name as dept_name,
    d.manager_id as dept_manager_id,
    em.full_name as dept_manager_name,
    t.id as team_id,
    t.name as team_name,
    t.team_lead_id,
    et.full_name as team_lead_name,
    e.employee_id,
    e.full_name as employee_name,
    e.designation,
    e.email,
    p.id as project_id,
    p.name as project_name,
    c.name as client_name
FROM departments d
LEFT JOIN employees em ON d.manager_id = em.employee_id
LEFT JOIN teams t ON d.id = t.department_id
LEFT JOIN employees et ON t.team_lead_id = et.employee_id
LEFT JOIN employee_teams ept ON t.id = ept.team_id
LEFT JOIN employees e ON ept.employee_id = e.employee_id
LEFT JOIN projects p ON t.id = p.team_id
LEFT JOIN clients c ON p.client_id = c.id
ORDER BY d.name, t.name, e.full_name;

-- ─────────────────────────────────────────────────────────
-- 12. CREATE VIEW FOR ATTENDANCE STATUS SUMMARY
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_attendance_summary AS
SELECT
    CURRENT_DATE as report_date,
    'Present' as status_type,
    COUNT(DISTINCT al.employee_id) as count,
    e.department_id,
    d.name as department_name
FROM attendance_logs al
JOIN employees e ON al.employee_id = e.employee_id
LEFT JOIN departments d ON e.department_id = d.id
WHERE al.attendance_date = CURRENT_DATE
AND al.status = 'present'
AND e.is_active = TRUE
GROUP BY e.department_id, d.name

UNION ALL

SELECT
    CURRENT_DATE as report_date,
    'WFH' as status_type,
    COUNT(DISTINCT al.employee_id) as count,
    e.department_id,
    d.name as department_name
FROM attendance_logs al
JOIN employees e ON al.employee_id = e.employee_id
LEFT JOIN departments d ON e.department_id = d.id
WHERE al.attendance_date = CURRENT_DATE
AND al.is_wfh = TRUE
AND e.is_active = TRUE
GROUP BY e.department_id, d.name

UNION ALL

SELECT
    CURRENT_DATE as report_date,
    'On Leave' as status_type,
    COUNT(DISTINCT la.employee_id) as count,
    e.department_id,
    d.name as department_name
FROM leave_applications la
JOIN employees e ON la.employee_id = e.employee_id
LEFT JOIN departments d ON e.department_id = d.id
WHERE CURRENT_DATE BETWEEN la.start_date AND la.end_date
AND la.status = 'approved'
AND e.is_active = TRUE
GROUP BY e.department_id, d.name

UNION ALL

SELECT
    CURRENT_DATE as report_date,
    'Half Day' as status_type,
    COUNT(DISTINCT al.employee_id) as count,
    e.department_id,
    d.name as department_name
FROM attendance_logs al
JOIN employees e ON al.employee_id = e.employee_id
LEFT JOIN departments d ON e.department_id = d.id
WHERE al.attendance_date = CURRENT_DATE
AND al.status = 'half_day'
AND e.is_active = TRUE
GROUP BY e.department_id, d.name;

-- ─────────────────────────────────────────────────────────
-- 13. MIGRATION COMPLETE
-- ─────────────────────────────────────────────────────────
-- Run this SQL in Supabase SQL Editor to apply all changes
-- Tables created:
--   ✓ clients
--   ✓ departments
--   ✓ teams
--   ✓ employee_teams
--   ✓ projects
--   ✓ attendance_corrections
--   ✓ new_employee_requests
--   ✓ approval_workflows
-- 
-- Views created:
--   ✓ v_org_hierarchy
--   ✓ v_attendance_summary
-- ============================================================
