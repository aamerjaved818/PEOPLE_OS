import sqlite3
import os

db_path = "backend/data/people_os_dev.db"

def apply_cascades():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables that need fixing
    table_configs = {
        "hcm_payroll_ledger": """
            CREATE TABLE hcm_payroll_ledger (
                id INTEGER NOT NULL,
                employee_id VARCHAR NOT NULL,
                period_month VARCHAR NOT NULL,
                period_year VARCHAR NOT NULL,
                basic_salary FLOAT,
                gross_salary FLOAT,
                net_salary FLOAT,
                additions FLOAT,
                deductions FLOAT,
                status VARCHAR,
                payment_date VARCHAR,
                payment_mode VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE
            )
        """,
        "hcm_attendance": """
            CREATE TABLE hcm_attendance (
                id INTEGER NOT NULL,
                employee_id VARCHAR NOT NULL,
                date VARCHAR NOT NULL,
                clock_in VARCHAR,
                clock_out VARCHAR,
                status VARCHAR,
                shift_id VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE,
                FOREIGN KEY(shift_id) REFERENCES hcm_shifts (id)
            )
        """,
        "hcm_leave_balances": """
            CREATE TABLE hcm_leave_balances (
                id INTEGER NOT NULL,
                employee_id VARCHAR NOT NULL,
                year INTEGER NOT NULL,
                annual_total FLOAT,
                annual_used FLOAT,
                sick_total FLOAT,
                sick_used FLOAT,
                casual_total FLOAT,
                casual_used FLOAT,
                unpaid_used FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE
            )
        """,
        "hcm_leave_requests": """
            CREATE TABLE hcm_leave_requests (
                id VARCHAR NOT NULL,
                employee_id VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                start_date VARCHAR NOT NULL,
                end_date VARCHAR NOT NULL,
                days FLOAT,
                reason VARCHAR,
                status VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE
            )
        """,
        "hcm_employee_education": """
            CREATE TABLE hcm_employee_education (
                id INTEGER NOT NULL,
                employee_id VARCHAR,
                degree VARCHAR,
                institute VARCHAR,
                passing_year VARCHAR,
                score VARCHAR,
                marks_obtained FLOAT,
                total_marks FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE
            )
        """,
        "hcm_employee_experience": """
            CREATE TABLE hcm_employee_experience (
                id INTEGER NOT NULL,
                employee_id VARCHAR,
                company_name VARCHAR,
                designation VARCHAR,
                start_date VARCHAR,
                end_date VARCHAR,
                gross_salary FLOAT,
                remarks VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE
            )
        """,
        "hcm_employee_family": """
            CREATE TABLE hcm_employee_family (
                id INTEGER NOT NULL,
                employee_id VARCHAR,
                name VARCHAR,
                relationship VARCHAR,
                dob VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE
            )
        """,
        "hcm_employee_discipline": """
            CREATE TABLE hcm_employee_discipline (
                id INTEGER NOT NULL,
                employee_id VARCHAR,
                date VARCHAR,
                description VARCHAR,
                outcome VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE
            )
        """,
        "hcm_employee_increments": """
            CREATE TABLE hcm_employee_increments (
                id INTEGER NOT NULL,
                employee_id VARCHAR,
                effective_date VARCHAR,
                amount FLOAT,
                increment_type VARCHAR,
                remarks VARCHAR,
                previous_salary FLOAT,
                new_gross FLOAT,
                house_rent FLOAT,
                utility FLOAT,
                other_allowance FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                created_by VARCHAR,
                updated_by VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(employee_id) REFERENCES hcm_employees (id) ON UPDATE CASCADE
            )
        """
    }

    try:
        cursor.execute("PRAGMA foreign_keys=OFF;")
        
        for table, new_sql in table_configs.items():
            print(f"Fixing table: {table}")
            
            # 1. Rename old table
            cursor.execute(f"ALTER TABLE {table} RENAME TO {table}_old;")
            
            # 2. Create new table
            cursor.execute(new_sql)
            
            # 3. Get columns from old table to ensure correct mapping
            cursor.execute(f"PRAGMA table_info({table}_old);")
            columns = [col[1] for col in cursor.fetchall()]
            col_str = ", ".join(columns)
            
            # 4. Copy data
            cursor.execute(f"INSERT INTO {table} ({col_str}) SELECT {col_str} FROM {table}_old;")
            
            # 5. Drop old table
            cursor.execute(f"DROP TABLE {table}_old;")
            
        conn.commit()
        cursor.execute("PRAGMA foreign_keys=ON;")
        print("Success: All tables updated with ON UPDATE CASCADE.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_cascades()
