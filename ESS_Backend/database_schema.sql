-- ============================================================
-- OTSI Attendance Portal - Database Schema
-- Supabase/PostgreSQL
-- ============================================================

-- ─────────────────────────────────────────────────────────
-- 1. Employees Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    designation VARCHAR(100),
    department VARCHAR(100),
    manager_id VARCHAR(50),
    manager_name VARCHAR(150),
    phone VARCHAR(20),
    date_of_joining DATE,
    role VARCHAR(20) DEFAULT 'employee' CHECK (role IN ('employee', 'hr', 'admin')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'on_leave')),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    lockout_until TIMESTAMP,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_temp_code VARCHAR(6),
    mfa_temp_expires TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 2. Attendance Logs Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance_logs (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    check_in_latitude FLOAT,
    check_in_longitude FLOAT,
    check_in_location VARCHAR(255),
    is_wfh BOOLEAN DEFAULT FALSE,
    working_hours DECIMAL(5, 2),
    status VARCHAR(20) DEFAULT 'absent' CHECK (status IN ('present', 'absent', 'wfh', 'late', 'half_day')),
    is_late BOOLEAN DEFAULT FALSE,
    location_verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, attendance_date)
);

-- ─────────────────────────────────────────────────────────
-- 3. Leave Balance Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leave_balance (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL UNIQUE REFERENCES employees(employee_id) ON DELETE CASCADE,
    casual_leave INT DEFAULT 12,
    sick_leave INT DEFAULT 8,
    earned_leave DECIMAL(4, 1) DEFAULT 20.0,
    bereavement_leave INT DEFAULT 3,
    marriage_leave INT DEFAULT 0,
    lop_leave INT DEFAULT 0,
    last_reset_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 4. Leave Applications Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leave_applications (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    leave_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    number_of_days DECIMAL(3, 1),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    approved_by VARCHAR(50),
    approval_date TIMESTAMP,
    approval_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 5. Timesheet Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS timesheets (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    total_hours DECIMAL(5, 2),
    submitted_date TIMESTAMP,
    approved_by VARCHAR(50),
    approved_date TIMESTAMP,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, week_start_date)
);

-- ─────────────────────────────────────────────────────────
-- 6. Timesheet Entries Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS timesheet_entries (
    id SERIAL PRIMARY KEY,
    timesheet_id INT NOT NULL REFERENCES timesheets(id) ON DELETE CASCADE,
    entry_date DATE NOT NULL,
    project_name VARCHAR(200),
    task_description VARCHAR(500),
    hours_worked DECIMAL(3, 1) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 7. Help Desk Tickets Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    priority VARCHAR(10) DEFAULT 'p3' CHECK (priority IN ('p1', 'p2', 'p3')),
    subject VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    assigned_to VARCHAR(50),
    resolution TEXT,
    resolved_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 8. Notifications Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    title VARCHAR(200),
    message TEXT,
    type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 9. Audit Logs Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50),
    action VARCHAR(100),
    entity_type VARCHAR(50),
    entity_id INT,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 10. Password History Table
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS password_history (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- INDEXES for Performance
-- ─────────────────────────────────────────────────────────
CREATE INDEX idx_attendance_logs_employee_id ON attendance_logs(employee_id);
CREATE INDEX idx_attendance_logs_date ON attendance_logs(attendance_date);
CREATE INDEX idx_attendance_logs_employee_date ON attendance_logs(employee_id, attendance_date);
CREATE INDEX idx_leave_applications_employee_id ON leave_applications(employee_id);
CREATE INDEX idx_leave_applications_status ON leave_applications(status);
CREATE INDEX idx_timesheets_employee_id ON timesheets(employee_id);
CREATE INDEX idx_timesheets_status ON timesheets(status);
CREATE INDEX idx_support_tickets_employee_id ON support_tickets(employee_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);
CREATE INDEX idx_notifications_employee_id ON notifications(employee_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- ─────────────────────────────────────────────────────────
-- SAMPLE DATA  (run seed_users.py for hashed passwords)
-- Passwords shown here are plaintext for reference only —
-- the actual inserts use werkzeug scrypt hashes.
--
--   Role      │ Employee ID │ Password
--   ──────────┼─────────────┼─────────────────
--   Employee  │ EMP1001     │ Employee@123
--   HR        │ EMP2001     │ HRManager@123
--   Admin     │ ADMIN001    │ Admin@1234
--
-- Run:  python seed_users.py
-- ─────────────────────────────────────────────────────────
