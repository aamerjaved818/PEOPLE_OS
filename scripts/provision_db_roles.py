"""
People_OS Database Role Provisioning Script

This script provisions database users/roles per the People_OS Database Standard.
Currently a template for PostgreSQL migration. Adapt for production use.

Roles:
- dev_user:    RW on DEV only
- test_runner: RW on DEV, TEST
- ci_migrator: RW on DEV, TEST, STAGE; migrate-only on PROD
- app_runtime: RW on all (application service account)
- auditor:     RO on all
- human_admin: RW with controlled PROD access
"""
import os
import sys


# Role definitions per environment
ROLES = {
    "dev_user": {
        "development": "RW",
        "test": None,
        "stage": None,
        "production": None,
    },
    "test_runner": {
        "development": "RW",
        "test": "RW",
        "stage": None,
        "production": None,
    },
    "ci_migrator": {
        "development": "RW",
        "test": "RW",
        "stage": "RW",
        "production": "MIGRATE",
    },
    "app_runtime": {
        "development": "RW",
        "test": "RW",
        "stage": "RW",
        "production": "RW",
    },
    "auditor": {
        "development": "RO",
        "test": "RO",
        "stage": "RO",
        "production": "RO",
    },
}


def generate_postgresql_grants(role: str, database: str, access: str) -> list:
    """Generate PostgreSQL GRANT statements for a role."""
    statements = []

    if access is None:
        statements.append(f"REVOKE ALL ON DATABASE {database} FROM {role};")
    elif access == "RO":
        statements.append(f"GRANT CONNECT ON DATABASE {database} TO {role};")
        statements.append(
            f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role};"
        )
    elif access == "RW":
        statements.append(f"GRANT CONNECT ON DATABASE {database} TO {role};")
        statements.append(
            f"GRANT SELECT, INSERT, UPDATE, DELETE "
            f"ON ALL TABLES IN SCHEMA public TO {role};"
        )
    elif access == "MIGRATE":
        statements.append(f"GRANT CONNECT ON DATABASE {database} TO {role};")
        statements.append(
            f"GRANT CREATE, ALTER ON ALL TABLES IN SCHEMA public TO {role};"
        )

    return statements


def provision_all_roles():
    """Generate provisioning SQL for all roles across all environments."""
    databases = {
        "development": "peopleos_dev",
        "test": "peopleos_test",
        "stage": "peopleos_stage",
        "production": "peopleos_prod",
    }

    print("-- People_OS Database Role Provisioning Script")
    print("-- Generated per DATABASE_STANDARD.md")
    print("")

    for role_name, permissions in ROLES.items():
        print(f"-- Role: {role_name}")
        print(f"CREATE ROLE {role_name} WITH LOGIN PASSWORD 'CHANGE_ME';")
        for env, access in permissions.items():
            db = databases[env]
            grants = generate_postgresql_grants(role_name, db, access)
            for stmt in grants:
                print(stmt)
        print("")


if __name__ == "__main__":
    provision_all_roles()
