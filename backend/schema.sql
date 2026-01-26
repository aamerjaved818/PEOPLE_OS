-- Core/Base Tables
CREATE TABLE IF NOT EXISTS core_organizations (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    enabled_modules TEXT DEFAULT '["hcm"]',
    head_id TEXT,
    tax_identifier TEXT,
    registration_number TEXT,
    founded_date TEXT,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    website TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT,
    logo TEXT,
    cover_url TEXT,
    industry TEXT,
    currency TEXT DEFAULT 'PKR',
    tax_year_end TEXT,
    social_links TEXT,
    description TEXT,
    system_authority TEXT,
    approval_workflows TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (head_id) REFERENCES core_users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS core_users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    name TEXT,
    email TEXT,
    organization_id TEXT,
    employee_id TEXT,
    is_active BOOLEAN DEFAULT 1,
    is_system_user BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES hcm_employees(id) ON DELETE SET NULL
);

-- Add head_id FK to organizations after users table is created
CREATE TABLE IF NOT EXISTS core_locations (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    location TEXT NOT NULL,
    organization_id TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    current_sequence INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    head_of_plant TEXT,
    contact_number TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS core_divisions (
    id TEXT PRIMARY KEY,
    plant_id TEXT NOT NULL,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (plant_id) REFERENCES core_locations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS core_departments (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL,
    isActive BOOLEAN DEFAULT 1,
    organization_id TEXT NOT NULL,
    hod_id TEXT,
    manager_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (hod_id) REFERENCES core_users(id) ON DELETE SET NULL,
    FOREIGN KEY (manager_id) REFERENCES core_users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS core_sub_departments (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    organization_id TEXT NOT NULL,
    parent_department_id TEXT NOT NULL,
    manager_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_department_id) REFERENCES core_departments(id) ON DELETE CASCADE,
    FOREIGN KEY (manager_id) REFERENCES core_users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS core_audit_logs (
    id TEXT PRIMARY KEY,
    organization_id TEXT,
    user TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT,
    time TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS core_role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    permission TEXT NOT NULL,
    organization_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS core_api_keys (
    id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE
);

-- HCM Tables
CREATE TABLE IF NOT EXISTS hcm_job_levels (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    organization_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hcm_grades (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    level INTEGER,
    job_level_id TEXT,
    is_active BOOLEAN DEFAULT 1,
    organization_id TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (job_level_id) REFERENCES hcm_job_levels(id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hcm_designations (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    grade_id TEXT NOT NULL,
    department_id TEXT,
    is_active BOOLEAN DEFAULT 1,
    organization_id TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (grade_id) REFERENCES hcm_grades(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES core_departments(id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hcm_shifts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    type TEXT,
    start_time TEXT,
    end_time TEXT,
    grace_period INTEGER,
    break_duration INTEGER,
    work_days TEXT,
    color TEXT,
    description TEXT,
    isActive BOOLEAN DEFAULT 1,
    organization_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hcm_employees (
    id TEXT PRIMARY KEY,
    employee_code TEXT,
    name TEXT NOT NULL,
    eobi_status BOOLEAN DEFAULT 0,
    social_security_status BOOLEAN DEFAULT 0,
    medical_status BOOLEAN DEFAULT 0,
    role TEXT,
    organization_id TEXT,
    department_id TEXT NOT NULL,
    designation_id TEXT NOT NULL,
    grade_id TEXT NOT NULL,
    plant_id TEXT,
    shift_id TEXT,
    status TEXT,
    join_date TEXT,
    email TEXT UNIQUE NOT NULL,
    date_of_birth TEXT,
    father_name TEXT,
    gender TEXT,
    cnic TEXT,
    cnic_expiry TEXT,
    cnic_issue_date TEXT,
    religion TEXT,
    marital_status TEXT,
    blood_group TEXT,
    nationality TEXT,
    phone TEXT,
    personal_email TEXT,
    personal_phone TEXT,
    present_address TEXT,
    permanent_address TEXT,
    present_district TEXT,
    permanent_district TEXT,
    gross_salary REAL DEFAULT 0.0,
    payment_mode TEXT,
    bank_account TEXT,
    bank_name TEXT,
    eobi_number TEXT,
    social_security_number TEXT,
    probation_period TEXT,
    confirmation_date TEXT,
    leaving_date TEXT,
    leaving_type TEXT,
    line_manager_id TEXT,
    sub_department_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES core_departments(id) ON DELETE RESTRICT,
    FOREIGN KEY (designation_id) REFERENCES hcm_designations(id) ON DELETE RESTRICT,
    FOREIGN KEY (grade_id) REFERENCES hcm_grades(id) ON DELETE RESTRICT,
    FOREIGN KEY (plant_id) REFERENCES core_locations(id) ON DELETE SET NULL,
    FOREIGN KEY (shift_id) REFERENCES hcm_shifts(id) ON DELETE SET NULL,
    FOREIGN KEY (line_manager_id) REFERENCES hcm_employees(id) ON DELETE SET NULL,
    FOREIGN KEY (sub_department_id) REFERENCES core_sub_departments(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS hcm_candidates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    position_applied TEXT,
    current_stage TEXT DEFAULT 'Applied',
    score INTEGER DEFAULT 0,
    resume_url TEXT,
    applied_date TEXT NOT NULL,
    avatar TEXT,
    organization_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (organization_id) REFERENCES core_organizations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS hcm_education (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    degree TEXT,
    institution TEXT,
    major TEXT,
    graduation_year TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (employee_id) REFERENCES hcm_employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hcm_experience (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    company TEXT,
    position TEXT,
    start_date TEXT,
    end_date TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (employee_id) REFERENCES hcm_employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hcm_family (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    relation TEXT,
    name TEXT,
    date_of_birth TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (employee_id) REFERENCES hcm_employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hcm_discipline (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    action TEXT,
    date TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (employee_id) REFERENCES hcm_employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hcm_increments (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    amount REAL,
    effective_date TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (employee_id) REFERENCES hcm_employees(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS ix_core_organizations_code ON core_organizations(code);
CREATE INDEX IF NOT EXISTS ix_core_users_username ON core_users(username);
CREATE INDEX IF NOT EXISTS ix_core_users_organization_id ON core_users(organization_id);
CREATE INDEX IF NOT EXISTS ix_core_departments_organization_id ON core_departments(organization_id);
CREATE INDEX IF NOT EXISTS ix_core_locations_organization_id ON core_locations(organization_id);
CREATE INDEX IF NOT EXISTS ix_hcm_employees_id ON hcm_employees(id);
CREATE INDEX IF NOT EXISTS ix_hcm_employees_name ON hcm_employees(name);
CREATE INDEX IF NOT EXISTS ix_hcm_employees_email ON hcm_employees(email);
CREATE INDEX IF NOT EXISTS ix_hcm_employees_organization_id ON hcm_employees(organization_id);
CREATE INDEX IF NOT EXISTS ix_hcm_employees_department_id ON hcm_employees(department_id);
CREATE INDEX IF NOT EXISTS ix_hcm_employees_designation_id ON hcm_employees(designation_id);
CREATE INDEX IF NOT EXISTS ix_hcm_grades_organization_id ON hcm_grades(organization_id);
CREATE INDEX IF NOT EXISTS ix_hcm_designations_organization_id ON hcm_designations(organization_id);
CREATE INDEX IF NOT EXISTS ix_hcm_job_levels_organization_id ON hcm_job_levels(organization_id);
CREATE INDEX IF NOT EXISTS ix_hcm_shifts_organization_id ON hcm_shifts(organization_id);
CREATE INDEX IF NOT EXISTS ix_core_audit_logs_organization_id ON core_audit_logs(organization_id);
