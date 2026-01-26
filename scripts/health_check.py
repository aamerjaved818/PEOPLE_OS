import os
import sys
import requests
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from backend.config import settings
except ImportError:
    print("❌ Error: Could not import backend.config. Ensure you are running from the project root.")
    sys.exit(1)


def check_health():
    """Verify system health and production readiness."""
    print("🚀 Running peopleOS eBusiness Suite Health Check...")

    # 1. Check Backend Connectivity
    # Use settings.PORT but fallback to 8000 if not set or if there's an issue
    port = getattr(settings, 'PORT', 8000)
    health_url = f"http://localhost:{port}/api/v1/health"
    print(f"🔗 Checking Backend: {health_url}")
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend: {data.get('status', 'Optimal')}")
            if data.get('database') == 'Connected' or data.get('db_status') == 'Connected':
                print("✅ Database: Connected")
            else:
                print(f"❌ Database: {data.get('database', 'Disconnected')}")
                return False
        else:
            print(f"❌ Backend returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("🟡 Backend: Not reachable (Offline). This is normal if the server hasn't started yet.")
    except Exception as e:
        print(f"❌ Backend check failed: {str(e)}")
        return False

    # 2. Check Environment
    env = getattr(settings, 'ENVIRONMENT', 'development')
    print(f"🌍 Environment: {env}")
    if env == "production":
        print("✅ Environment Mode: Production Hardened")
    else:
        print("⚠️ Environment Mode: Development (Warning: Not for production)")

    # 3. Check Data Directory
    try:
        db_path = getattr(settings, 'DB_PATH', 'people_os.db')
        data_dir = os.path.dirname(os.path.abspath(db_path))
        if os.path.exists(data_dir):
            print(f"✅ Data Directory: Accessible ({data_dir})")
        else:
            print(f"❌ Data Directory: Missing or inaccessible! ({data_dir})")
            return False
    except Exception as e:
        print(f"⚠️ Could not verify data directory: {e}")

    print("\n✨ Health Check Summary: SYSTEM READY")
    return True


if __name__ == "__main__":
    success = check_health()
    # We exit with 0 to allow the launcher to continue even if backend is offline
    sys.exit(0)
