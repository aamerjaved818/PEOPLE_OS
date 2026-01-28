#!/usr/bin/env python3
"""
peopleOS eBusiness Suite Launcher
Usage: python start.py [dev|prod|status|health]
"""

import subprocess
import sys
import socket
import shutil
import time
import webbrowser
import os
import re
from pathlib import Path

# --- Configuration Loading ---
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / ".env"

def load_env_config():
    """Load configuration from .env file without external dependencies."""
    config = {
        "API_PORT": 8000,
        "FRONTEND_PORT": None,
        "PREVIEW_PORT": None,
        "APP_ENV": "development"
    }
    
    if ENV_FILE.exists():
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("'").strip('"')
                        if key in config or key in ["API_PORT", "FRONTEND_PORT", "PREVIEW_PORT"]:
                            if key.endswith("PORT") or key == "PORT":
                                try:
                                    config[key] = int(value)
                                except ValueError:
                                    pass
                            else:
                                config[key] = value
        except Exception as e:
            print(f"[WARN] Failed to read .env: {e}")
    
    # Resolve Effective Ports
    effective_backend = config.get("API_PORT") or config.get("PORT") or 8000
    effective_frontend = config.get("FRONTEND_PORT") or 5173
    effective_preview = config.get("PREVIEW_PORT") or 9000
    
    return {
        "BACKEND_PORT": effective_backend,
        "FRONTEND_PORT": effective_frontend,
        "FRONTEND_PROD_PORT": effective_preview,
        "APP_ENV": config.get("APP_ENV", "development")
    }

CONF = load_env_config()

# Derived Constants
BACKEND_PORT = CONF["BACKEND_PORT"]
FRONTEND_DEV_PORT = CONF["FRONTEND_PORT"]
FRONTEND_PROD_PORT = CONF["FRONTEND_PROD_PORT"]


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def enable_vt_mode():
        """Enable ANSI escape sequences on Windows 10/11."""
        if os.name == 'nt':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception:
                pass

Colors.enable_vt_mode()


def print_banner():
    """Print startup banner."""
    print(f"""
{Colors.CYAN}{Colors.BOLD}+----------------------------------------------------------+
|            peopleOS eBusiness Suite Launcher             |
+----------------------------------------------------------+{Colors.END}
""")


def port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False


def wait_for_port(port: int, timeout: int = 20) -> bool:
    """Wait for a port to become available."""
    start = time.time()
    while time.time() - start < timeout:
        if port_in_use(port):
            return True
        time.sleep(0.5)
    return False


def check_prerequisites() -> tuple[Path, bool]:
    """Check for .venv and node_modules. Always uses .venv."""
    if os.name == 'nt':
        venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
    
    node_modules = (PROJECT_ROOT / "node_modules").exists()
    
    return venv_python, node_modules


def print_status():
    """Print current system status in a structured format."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}System Status Summary{Colors.END}")
    print("-" * 40)
    
    services = [
        ("Backend  ", BACKEND_PORT),
        ("Frontend ", FRONTEND_DEV_PORT)
    ]
    
    for name, port in services:
        status = f"{Colors.GREEN}[RUNNING]{Colors.END}" if port_in_use(port) else f"{Colors.RED}[STOPPED]{Colors.END}"
        print(f"  {name} {Colors.YELLOW}:{port}{Colors.END}    {status}")
    
    venv_python, node_modules = check_prerequisites()
    print("-" * 40)
    print(f"  {Colors.BOLD}Prerequisites:{Colors.END}")
    print(f"  .venv         {'[OK]' if venv_python.exists() else '[MISSING]'}")
    print(f"  node_modules  {'[OK]' if node_modules else '[MISSING]'}")
    print("-" * 40 + "\n")

def run_doctor():
    """Run comprehensive system diagnostics."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}--- peopleOS System Doctor ---{Colors.END}\n")
    
    checks = []
    
    # 1. Python Check
    py_version = sys.version_info
    py_ok = py_version.major == 3 and py_version.minor >= 9
    checks.append(("Python >= 3.9", f"{sys.version.split()[0]}", py_ok))
    
    # 2. Node Check
    node = shutil.which("node")
    if node:
        try:
            node_ver = subprocess.check_output(["node", "--version"]).decode().strip()
            node_ok = int(node_ver.lstrip('v').split('.')[0]) >= 18
            checks.append(("Node.js >= 18", node_ver, node_ok))
        except:
            checks.append(("Node.js", "Error checking version", False))
    else:
        checks.append(("Node.js", "Not Found", False))
        
    # 3. Environment Check
    critical_env = ["JWT_SECRET_KEY", "CORS_ORIGINS", "API_PORT"]
    missing_env = []
    if ENV_FILE.exists():
        content = ENV_FILE.read_text()
        for key in critical_env:
            if key not in content: missing_env.append(key)
        checks.append(("Environment", f"Missing: {', '.join(missing_env)}" if missing_env else "All critical keys found", not missing_env))
    else:
        checks.append(("Environment", ".env file missing", False))
        
    # 4. Identity Health Check (Backend Architecture Compliance)
    identity_ok = True
    identity_msg = "OK (In-memory only)"
    
    # Try multiple potential database locations and environment-specific names
    env_name = CONF.get("APP_ENV", "development")
    db_files = [
        f"people_os_{env_name}.db",
        "people_os_dev.db",
        "people_os.db"
    ]
    db_dirs = [
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "backend" / "data"
    ]
    
    found_db = None
    for dname in db_dirs:
        for fname in db_files:
            p = dname / fname
            if p.exists():
                found_db = p
                break
        if found_db: break
    
    if found_db:
        try:
            import sqlite3
            conn = sqlite3.connect(found_db)
            cursor = conn.cursor()
            
            # Check if core_users table exists first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_users';")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM core_users WHERE role = 'Root';")
                root_count = cursor.fetchone()[0]
                if root_count > 0:
                    identity_ok = False
                    identity_msg = f"Inconsistent (Found {root_count} Root users in DB)"
                else:
                    identity_msg = f"OK (Verified {found_db.name})"
            else:
                identity_msg = f"Safe (Tables not initialized in {found_db.name})"
            
            conn.close()
        except Exception as e:
            identity_msg = f"Check failed: {str(e)}"
            identity_ok = False
    else:
        identity_msg = "Database not found (Safe)"
    
    checks.append(("Identity", identity_msg, identity_ok))

    # 5. Disk & Path Check
    import tempfile
    space_ok = True
    try:
        # Check if we can write to a temporary file
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            tmp.write(b"test")
        
        # Check disk space (very basic check)
        if hasattr(shutil, "disk_usage"):
            usage = shutil.disk_usage(PROJECT_ROOT)
            free_gb = usage.free / (1024**3)
            space_ok = free_gb > 0.5
            checks.append(("Disk Space", f"{free_gb:.1f} GB free", space_ok))
    except Exception as e:
        checks.append(("File System", f"Permission denied or error: {str(e)}", False))

    # Print Results
    for label, info, ok in checks:
        icon = f"{Colors.GREEN}[PASS]{Colors.END}" if ok else f"{Colors.RED}[FAIL]{Colors.END}"
        print(f"  {icon} {label:<15} : {info}")
    
    print(f"\n{Colors.BOLD}Diagnostic Complete.{Colors.END}\n")
    return all(c[2] for c in checks)



def tail_log(logfile: Path, lines: int = 20):
    """Print the last N lines of a log file."""
    if not logfile.exists():
        return
    
    try:
        with open(logfile, 'r', encoding='utf-8', errors='replace') as f:
            # Efficient tail implementation for small-medium logs
            content = f.readlines()
            tail = content[-lines:]
            print(f"\n{Colors.RED}--- Error Log ({logfile.name}) ---{Colors.END}")
            for line in tail:
                print(f"{Colors.YELLOW}{line.strip()}{Colors.END}")
            print(f"{Colors.RED}-----------------------------------{Colors.END}\n")
    except Exception as e:
        print(f"{Colors.RED}Failed to read log: {e}{Colors.END}")

def start_backend(python_exe: Path, env: str = "development") -> subprocess.Popen | None:
    """Start the backend server using the centralized entry point."""
    if port_in_use(BACKEND_PORT):
        print(f"  {Colors.GREEN}[OK] Backend already running on :{BACKEND_PORT}{Colors.END}")
        return None
    
    print(f"  Starting backend ({env})...", end=" ", flush=True)
    
    env_vars = os.environ.copy()
    env_vars["APP_ENV"] = env
    env_vars["API_PORT"] = str(BACKEND_PORT)
    
    # Log file
    log_file = PROJECT_ROOT / "logs" / "launcher_backend.log"
    log_file.parent.mkdir(exist_ok=True)
    
    # Use standard python -m execution
    cmd = [str(python_exe), '-m', 'backend.main']
    
    with open(log_file, "w", encoding="utf-8") as out:
        proc = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=out,
            stderr=subprocess.STDOUT, # Merge stderr into stdout
            env=env_vars
        )
    
    if wait_for_port(BACKEND_PORT, timeout=15):
        print(f"{Colors.GREEN}[OK] Running on :{BACKEND_PORT}{Colors.END}")
        return proc
    else:
        print(f"{Colors.RED}[X] Failed to start{Colors.END}")
        tail_log(log_file)
        return None


def start_frontend(mode: str = "dev") -> subprocess.Popen | None:
    """Start the frontend server."""
    port = FRONTEND_DEV_PORT if mode == "dev" else FRONTEND_PROD_PORT
    
    if port_in_use(port):
        print(f"  {Colors.GREEN}[OK] Frontend already running on :{port}{Colors.END}")
        return None
    
    # Check for npm
    npm = shutil.which("npm")
    if not npm:
        print(f"  {Colors.RED}[X] npm not found in PATH{Colors.END}")
        return None
    
    # Log file
    log_file = PROJECT_ROOT / "logs" / "launcher_frontend.log"
    log_file.parent.mkdir(exist_ok=True)

    # Install deps if needed
    if not (PROJECT_ROOT / "node_modules").exists():
        print(f"  Installing dependencies...", end=" ", flush=True)
        with open(log_file, "a", encoding="utf-8") as out:
            result = subprocess.run(["npm", "install"], cwd=PROJECT_ROOT, stdout=out, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            print(f"{Colors.RED}[X] Failed (check {log_file.name}){Colors.END}")
            tail_log(log_file)
            return None
        print(f"{Colors.GREEN}[OK] Done{Colors.END}")
    
    cmd_name = "dev" if mode == "dev" else "preview:prod"
    if mode == "prod":
         # Build first
        print(f"  Building frontend...", end=" ", flush=True)
        with open(log_file, "a", encoding="utf-8") as out:
            result = subprocess.run(["npm", "run", "build"], cwd=PROJECT_ROOT, stdout=out, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            print(f"{Colors.RED}[X] Build failed{Colors.END}")
            tail_log(log_file)
            return None
        print(f"{Colors.GREEN}[OK] Done{Colors.END}")

    print(f"  Starting frontend ({mode})...", end=" ", flush=True)
    
    # Use npm run command which leverages vite config for ports
    cmd = ["npm", "run", cmd_name]
    
    with open(log_file, "w", encoding="utf-8") as out:
        proc = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=out,
            stderr=subprocess.STDOUT,
            shell=True if os.name == 'nt' else False
        )
    
    if wait_for_port(port, timeout=30):
        print(f"{Colors.GREEN}[OK] Running on :{port}{Colors.END}")
        return proc
    else:
        print(f"{Colors.RED}[X] Failed to start{Colors.END}")
        tail_log(log_file)
        return None


def start_dev():
    """Start development environment."""
    print(f"{Colors.BOLD}Starting Development Environment{Colors.END}\n")
    
    # Pre-flight checks
    venv_python, _ = check_prerequisites()
    if not venv_python.exists():
        print(f"{Colors.RED}Error: .venv not found. Run: python -m venv .venv{Colors.END}")
        return
    
    if not run_doctor():
        print(f"{Colors.YELLOW}Warning: System doctor reported issues. Startup may fail.{Colors.END}")
        time.sleep(2)
    
    # Start Backend
    backend_proc = start_backend(venv_python, "development")
    
    # Start Frontend
    frontend_proc = start_frontend("dev")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Access Output:{Colors.END}")
    print(f"  Frontend: http://localhost:{FRONTEND_DEV_PORT}")
    print(f"  Backend:  http://localhost:{BACKEND_PORT}/docs")
    
    try:
        webbrowser.open(f"http://localhost:{FRONTEND_DEV_PORT}")
    except:
        pass
    
    # Wait for processes
    try:
        while True:
            time.sleep(1)
            # Check if processes are alive
            if backend_proc and backend_proc.poll() is not None:
                print(f"\n{Colors.RED}[!] Backend stopped unexpectedly{Colors.END}")
                tail_log(PROJECT_ROOT / "logs" / "launcher_backend.log")
                break
            if frontend_proc and frontend_proc.poll() is not None:
                print(f"\n{Colors.RED}[!] Frontend stopped unexpectedly{Colors.END}")
                tail_log(PROJECT_ROOT / "logs" / "launcher_frontend.log")
                break
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stopping servers...{Colors.END}")
        if backend_proc: backend_proc.terminate()
        if frontend_proc: frontend_proc.terminate()


def start_prod():
    """Start production environment."""
    print(f"{Colors.BOLD}Starting Production Environment{Colors.END}\n")
    
    venv_python, _ = check_prerequisites()
    if not venv_python.exists():
        print(f"{Colors.RED}Error: .venv not found.{Colors.END}")
        return
    
    # Start Backend in Production Mode
    backend_proc = start_backend(venv_python, "production")
    
    # Start Frontend in Preview Mode
    frontend_proc = start_frontend("prod")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Access Output:{Colors.END}")
    print(f"  Frontend: http://localhost:{FRONTEND_PROD_PORT}")
    
    try:
        webbrowser.open(f"http://localhost:{FRONTEND_PROD_PORT}")
    except:
        pass

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stopping servers...{Colors.END}")
        if backend_proc: backend_proc.terminate()
        if frontend_proc: frontend_proc.terminate()


def main():
    """Main entry point."""
    print_banner()
    
    if len(sys.argv) < 2:
        print(f"{Colors.BOLD}Usage:{Colors.END} python start.py [command]")
        print(f"\n{Colors.BOLD}Commands:{Colors.END}")
        print("  dev      Start development servers (default)")
        print("  prod     Build and start production servers")
        print("  status   Show system status")
        print()
        start_dev()
        return
    
    command = sys.argv[1].lower()
    
    if command == "dev":
        start_dev()
    elif command == "prod":
        start_prod()
    elif command == "status":
        print_status()
    elif command == "doctor":
        run_doctor()
    else:
        print(f"{Colors.RED}Unknown command: {command}{Colors.END}")
        print("Valid commands: dev, prod, status, doctor")

if __name__ == "__main__":
    main()
