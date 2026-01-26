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
        "API_PORT": None,
        "FRONTEND_PORT": None,
        "PREVIEW_PORT": None,
        "PORT": 8000,
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
    """Print current system status."""
    print(f"{Colors.BOLD}System Status:{Colors.END}")
    print(f"  Backend  :{BACKEND_PORT}       {'[OK] Running' if port_in_use(BACKEND_PORT) else '[X] Stopped'}")
    print(f"  Frontend :{FRONTEND_DEV_PORT}      {'[OK] Running' if port_in_use(FRONTEND_DEV_PORT) else '[X] Stopped'}")
    
    venv_python, node_modules = check_prerequisites()
    print(f"\n{Colors.BOLD}Prerequisites:{Colors.END}")
    print(f"  .venv         {'[OK] Found' if venv_python.exists() else '[X] Missing'}")
    print(f"  node_modules  {'[OK] Found' if node_modules else '[X] Missing'}")


def start_backend(python_exe: Path, env: str = "development") -> subprocess.Popen | None:
    """Start the backend server using the centralized entry point."""
    if port_in_use(BACKEND_PORT):
        print(f"  {Colors.GREEN}[OK] Backend already running on :{BACKEND_PORT}{Colors.END}")
        return None
    
    print(f"  Starting backend ({env})...", end=" ", flush=True)
    
    env_vars = os.environ.copy()
    env_vars["APP_ENV"] = env
    env_vars["PORT"] = str(BACKEND_PORT)
    
    # Use standard python -m execution
    cmd = [str(python_exe), '-m', 'backend.main']
    
    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env_vars
    )
    
    if wait_for_port(BACKEND_PORT, timeout=15):
        print(f"{Colors.GREEN}[OK] Running on :{BACKEND_PORT}{Colors.END}")
        return proc
    else:
        print(f"{Colors.RED}[X] Failed to start{Colors.END}")
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
    
    # Install deps if needed
    if not (PROJECT_ROOT / "node_modules").exists():
        print(f"  Installing dependencies...", end=" ", flush=True)
        result = subprocess.run(["npm", "install"], cwd=PROJECT_ROOT, capture_output=True)
        if result.returncode != 0:
            print(f"{Colors.RED}[X] Failed{Colors.END}")
            return None
        print(f"{Colors.GREEN}[OK] Done{Colors.END}")
    
    cmd_name = "dev" if mode == "dev" else "preview:prod"
    if mode == "prod":
         # Build first
        print(f"  Building frontend...", end=" ", flush=True)
        result = subprocess.run(["npm", "run", "build"], cwd=PROJECT_ROOT, capture_output=True)
        if result.returncode != 0:
            print(f"{Colors.RED}[X] Build failed{Colors.END}")
            # Continue anyway? No.
            return None
        print(f"{Colors.GREEN}[OK] Done{Colors.END}")

    print(f"  Starting frontend ({mode})...", end=" ", flush=True)
    
    # Use npm run command which leverages vite config for ports
    cmd = ["npm", "run", cmd_name]
    
    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True if os.name == 'nt' else False
    )
    
    if wait_for_port(port, timeout=30):
        print(f"{Colors.GREEN}[OK] Running on :{port}{Colors.END}")
        return proc
    else:
        print(f"{Colors.RED}[X] Failed to start{Colors.END}")
        return None


def start_dev():
    """Start development environment."""
    print(f"{Colors.BOLD}Starting Development Environment{Colors.END}\n")
    
    venv_python, _ = check_prerequisites()
    if not venv_python.exists():
        print(f"{Colors.RED}Error: .venv not found. Run: python -m venv .venv{Colors.END}")
        return
    
    # Start Backend
    start_backend(venv_python, "development")
    
    # Start Frontend
    start_frontend("dev")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Access Output:{Colors.END}")
    print(f"  Frontend: http://localhost:{FRONTEND_DEV_PORT}")
    print(f"  Backend:  http://localhost:{BACKEND_PORT}/docs")
    
    try:
        webbrowser.open(f"http://localhost:{FRONTEND_DEV_PORT}")
    except:
        pass


def start_prod():
    """Start production environment."""
    print(f"{Colors.BOLD}Starting Production Environment{Colors.END}\n")
    
    venv_python, _ = check_prerequisites()
    if not venv_python.exists():
        print(f"{Colors.RED}Error: .venv not found.{Colors.END}")
        return
    
    # Start Backend in Production Mode
    start_backend(venv_python, "production")
    
    # Start Frontend in Preview Mode
    start_frontend("prod")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Access Output:{Colors.END}")
    print(f"  Frontend: http://localhost:{FRONTEND_PROD_PORT}")
    
    try:
        webbrowser.open(f"http://localhost:{FRONTEND_PROD_PORT}")
    except:
        pass


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
    else:
        print(f"{Colors.RED}Unknown command: {command}{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stopped.{Colors.END}")
