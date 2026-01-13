import os
import requests

BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1")


def get_token(username: str, password: str) -> str | None:
    r = requests.post(
        f"{BASE}/auth/connexion",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if r.status_code == 200:
        return r.json().get("access_token")
    return None


def test_whoami_requires_auth():
    r = requests.get(f"{BASE}/auth/whoami")
    assert r.status_code in (401, 403)


def test_whoami_membre_ok():
    token = get_token("membre@example.com", "membre")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/auth/whoami", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data.get("email") == "membre@example.com"
    assert data.get("role") == "membre"


def test_membre_prets_requires_auth():
    r = requests.get(f"{BASE}/membre/prets")
    assert r.status_code in (401, 403)


def test_membre_prets_with_token_ok():
    token = get_token("membre@example.com", "membre")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/membre/prets", headers=headers)
    assert r.status_code == 200


def test_admin_livres_update_forbidden_for_membre():
    token = get_token("membre@example.com", "membre")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"{BASE}/admin/livres/99999",
        json={},
        headers=headers,
    )
    assert r.status_code in (401, 403)


def test_admin_livres_update_allowed_for_admin():
    token = get_token("admin@example.com", "admin")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"{BASE}/admin/livres/99999",
        json={},
        headers=headers,
    )
    assert r.status_code in (200, 404)
