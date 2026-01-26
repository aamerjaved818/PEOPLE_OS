#!/usr/bin/env python3
"""
Production Environment Configuration Script
Configures Redis, Celery, database, and SMTP settings
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional


class EnvironmentConfigurator:
    """Configure production environment for Phase 4B Part 3"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / '.env'
        self.backup_env = self.project_root / '.env.backup'
        
    def check_redis(self) -> bool:
        """Check if Redis is installed and running"""
        try:
            result = subprocess.run(
                ['redis-cli', 'ping'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def check_postgresql(self) -> bool:
        """Check if PostgreSQL is available"""
        try:
            result = subprocess.run(
                ['psql', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def generate_env_config(self) -> Dict[str, str]:
        """Generate environment configuration"""
        return {
            # Email Configuration (SMTP)
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'SMTP_USE_TLS': 'true',
            'SENDER_EMAIL': 'your-email@gmail.com',
            'SENDER_PASSWORD': 'your-app-password',
            'SENDER_NAME': 'peopleOS eBusiness Suite',
            
            # Celery Configuration
            'CELERY_BROKER_URL': 'redis://localhost:6379/0',
            'CELERY_RESULT_BACKEND': 'redis://localhost:6379/1',
            'CELERY_TIMEZONE': 'UTC',
            
            # Redis Configuration
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': '6379',
            'REDIS_DB': '0',
            
            # Report Configuration
            'REPORTS_DIR': '/tmp/reports',
            'REPORT_RETENTION_DAYS': '30',
            'MAX_REPORT_SIZE_MB': '100',
            
            # Database Configuration
            'DATABASE_URL': 'sqlite:///./app.db',
            # Alternative for PostgreSQL:
            # 'DATABASE_URL': 'postgresql://user:password@localhost/peopledb',
            
            # API Configuration
            'API_HOST': '0.0.0.0',
            'API_PORT': '8000',
            'DEBUG': 'false',
            
            # Security
            'SECRET_KEY': self._generate_secret_key(),
            'JWT_ALGORITHM': 'HS256',
            'JWT_EXPIRATION_HOURS': '24',
        }
    
    @staticmethod
    def _generate_secret_key() -> str:
        """Generate a secure secret key"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def backup_existing_env(self) -> bool:
        """Backup existing .env file if it exists"""
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    content = f.read()
                with open(self.backup_env, 'w') as f:
                    f.write(content)
                print(f"✓ Backed up existing .env to {self.backup_env}")
                return True
            except Exception as e:
                print(f"✗ Failed to backup .env: {e}")
                return False
        return True
    
    def write_env_file(self, config: Dict[str, str]) -> bool:
        """Write environment configuration to .env file"""
        try:
            with open(self.env_file, 'w') as f:
                f.write("# peopleOS eBusiness Suite Production Environment Configuration\n")
                f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n")
                f.write("# IMPORTANT: Update email credentials and database URL for your environment\n\n")
                
                # Group settings by category
                categories = {
                    'Email Configuration': [k for k in config if 'SMTP' in k or 'SENDER' in k],
                    'Celery & Task Queue': [k for k in config if 'CELERY' in k],
                    'Redis Configuration': [k for k in config if 'REDIS' in k],
                    'Report Configuration': [k for k in config if 'REPORT' in k],
                    'Database Configuration': [k for k in config if 'DATABASE' in k],
                    'API Configuration': [k for k in config if 'API' in k or 'DEBUG' in k],
                    'Security': [k for k in config if 'SECRET' in k or 'JWT' in k],
                }
                
                for category, keys in categories.items():
                    if keys:
                        f.write(f"# {category}\n")
                        for key in sorted(keys):
                            f.write(f"{key}={config[key]}\n")
                        f.write("\n")
            
            print(f"✓ Environment configuration written to {self.env_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to write .env file: {e}")
            return False
    
    def create_directories(self) -> bool:
        """Create necessary directories"""
        directories = [
            self.project_root / 'logs',
            self.project_root / 'tmp' / 'reports',
            self.project_root / 'migrations' / 'versions',
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created directory: {directory}")
            except Exception as e:
                print(f"✗ Failed to create directory {directory}: {e}")
                return False
        
        return True
    
    def check_python_dependencies(self) -> bool:
        """Check if required Python packages are installed"""
        required_packages = {
            'fastapi': 'FastAPI',
            'sqlalchemy': 'SQLAlchemy',
            'celery': 'Celery',
            'redis': 'Redis',
            'apscheduler': 'APScheduler',
            'jinja2': 'Jinja2',
            'pydantic': 'Pydantic',
        }
        
        missing = []
        for package, name in required_packages.items():
            try:
                __import__(package)
                print(f"✓ {name} is installed")
            except ImportError:
                print(f"✗ {name} is NOT installed")
                missing.append(package)
        
        if missing:
            print(f"\nTo install missing packages, run:")
            print(f"pip install {' '.join(missing)}")
            return False
        
        return True
    
    def print_setup_instructions(self) -> None:
        """Print setup instructions"""
        instructions = """
╔════════════════════════════════════════════════════════════════════╗
║                  PRODUCTION SETUP INSTRUCTIONS                    ║
╚════════════════════════════════════════════════════════════════════╝

1. UPDATE ENVIRONMENT VARIABLES
   ───────────────────────────────
   Edit .env and update:
   - SMTP_HOST, SMTP_PORT: Email server details
   - SENDER_EMAIL, SENDER_PASSWORD: Email credentials
   - CELERY_BROKER_URL, CELERY_RESULT_BACKEND: Redis URLs
   - DATABASE_URL: Database connection string
   - SECRET_KEY: Keep the generated value (already set)

2. SETUP DATABASE
   ───────────────
   Run database migration:
   $ alembic upgrade head

3. START REDIS
   ────────────
   Option A (Docker):
   $ docker run -d -p 6379:6379 --name redis redis:latest

   Option B (Local):
   $ redis-server

4. START CELERY WORKER
   ────────────────────
   $ celery -A backend.services.async_tasks worker \\
     --loglevel=info \\
     --concurrency=4

5. START CELERY BEAT SCHEDULER
   ────────────────────────────
   $ celery -A backend.services.async_tasks beat \\
     --loglevel=info

6. START API SERVER
   ─────────────────
   $ python -m uvicorn main:app \\
     --host 0.0.0.0 \\
     --port 8000 \\
     --workers 4

7. TEST THE SYSTEM
   ────────────────
   $ curl -X GET http://localhost:8000/api/analytics/schedules

   Or use the React UI:
   $ npm start

╔════════════════════════════════════════════════════════════════════╗
║                      NEXT STEPS                                    ║
╚════════════════════════════════════════════════════════════════════╝

1. Verify all services are running:
   - API: http://localhost:8000
   - Redis: redis-cli ping (should return PONG)
   - Celery: celery -A backend.services.async_tasks inspect active

2. Create test schedule:
   - Use React UI or API
   - Verify schedule appears in database

3. Monitor task execution:
   - Check Celery worker output
   - Review logs in /logs directory

4. Verify email delivery:
   - Check email inbox
   - Review email delivery logs

For detailed documentation, see:
- QUICKSTART_PHASE_4B_PART3.md
- PHASE_4B_PART3_IMPLEMENTATION.md
- INTEGRATION_CHECKLIST.md

════════════════════════════════════════════════════════════════════
        """
        print(instructions)
    
    def configure(self) -> bool:
        """Run complete environment configuration"""
        print("\n" + "="*60)
        print("peopleOS eBusiness Suite - Phase 4B Part 3 - Production Environment Setup")
        print("="*60 + "\n")
        
        # Step 1: Check system
        print("📋 Step 1: Checking system requirements...")
        print("-" * 60)
        
        redis_available = self.check_redis()
        pg_available = self.check_postgresql()
        
        if redis_available:
            print("✓ Redis is available")
        else:
            print("⚠ Redis is not running (required for production)")
        
        if pg_available:
            print("✓ PostgreSQL is available (recommended for production)")
        else:
            print("ℹ PostgreSQL not available (SQLite will be used)")
        
        # Step 2: Check Python dependencies
        print("\n📋 Step 2: Checking Python dependencies...")
        print("-" * 60)
        deps_ok = self.check_python_dependencies()
        
        if not deps_ok:
            print("\n⚠ Some dependencies are missing!")
            return False
        
        # Step 3: Create directories
        print("\n📋 Step 3: Creating necessary directories...")
        print("-" * 60)
        if not self.create_directories():
            return False
        
        # Step 4: Backup and generate config
        print("\n📋 Step 4: Generating environment configuration...")
        print("-" * 60)
        if not self.backup_existing_env():
            return False
        
        config = self.generate_env_config()
        if not self.write_env_file(config):
            return False
        
        # Step 5: Print instructions
        print("\n✅ Environment configuration complete!\n")
        self.print_setup_instructions()
        
        return True


def main():
    """Main entry point"""
    configurator = EnvironmentConfigurator()
    success = configurator.configure()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
