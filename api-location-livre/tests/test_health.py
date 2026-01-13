import os
import requests

BASE = os.getenv("API_BASE", "http://localhost:8000")

def test_health_running():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
