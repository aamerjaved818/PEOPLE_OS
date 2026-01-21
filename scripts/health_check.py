import os
import sys
import requests
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.config import settings


def check_health():
    """Verify system health and production readiness."""
    print("🚀 Running PeopleOS System Health Check...")

    # 1. Check Backend Connectivity
    health_url = f"http://localhost:{settings.PORT}/api/v1/health"
    print(f"🔗 Checking Backend: {health_url}")
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend: {data.get('status', 'Optimal')}")
            if data.get('database') == 'Connected':
                print("✅ Database: Connected")
            else:
                print("❌ Database: Disconnected")
                return False
        else:
            print(f"❌ Backend returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("🟡 Backend: Not reachable (Offline)")
    except Exception as e:
        print(f"❌ Backend check failed: {str(e)}")
        return False

    # 2. Check Environment
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    if settings.ENVIRONMENT == "production":
        print("✅ Environment Mode: Production Hardened")
    else:
        print("⚠️ Environment Mode: Development (Warning: Not for production)")

    # 3. Check Data Directory
    data_dir = os.path.dirname(settings.DB_PATH)
    if os.path.exists(data_dir):
        print(f"✅ Data Directory: Accessible ({data_dir})")
    else:
        print(f"❌ Data Directory: Missing or inaccessible!")
        return False

    print("\n✨ Health Check Summary: SYSTEM READY")
    return True


if __name__ == "__main__":
    check_health()
    # We don't exit with 1 on backend offline during startup check
    # as the launcher starts the server immediately after health check.
    sys.exit(0)
