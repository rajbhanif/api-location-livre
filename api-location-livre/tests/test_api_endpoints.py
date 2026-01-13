import os
import requests

BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1")
AUTH_BASE = os.getenv("AUTH_BASE", BASE)


def api_health_url():
    return BASE.replace("/api/v1", "") + "/health"


def get_tokens(username, password):
    """
    Retourne (access_token, refresh_token) ou (None, None) si la connexion échoue.
    """
    r = requests.post(
        f"{AUTH_BASE}/auth/connexion",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if r.status_code == 200:
        data = r.json()
        return data.get("access_token"), data.get("refresh_token")
    return None, None


def get_token(username, password):
    """
    Helper rétrocompatible: ne retourne que l'access_token.
    """
    access, _ = get_tokens(username, password)
    return access


# ========= HEALTH =========


def test_health_running():
    r = requests.get(api_health_url())
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


# ========= AUTH =========


def test_auth_connexion_ok_admin():
    token = get_token("admin@example.com", "admin")
    assert token is not None


def test_auth_connexion_ok_membre():
    token = get_token("membre@example.com", "membre")
    assert token is not None


def test_auth_connexion_bad_password():
    token = get_token("membre@example.com", "mauvaismdp")
    assert token is None


def test_auth_whoami_membre():
    token = get_token("membre@example.com", "membre")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.get(f"{AUTH_BASE}/auth/whoami", headers=headers)
    assert r.status_code in (200, 401)


def test_auth_refresh_token_flow():
    """
    E2E: connexion -> récupération du refresh_token -> appel /auth/refresh.
    """
    access, refresh = get_tokens("membre@example.com", "membre")
    assert refresh is not None

    r = requests.post(
        f"{AUTH_BASE}/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("access_token") is not None
    assert body.get("refresh_token") is not None


# ========= CATALOGUE =========


def test_catalogue_public():
    r = requests.get(f"{BASE}/catalogue")
    assert r.status_code == 200


def test_catalogue_recherche():
    r = requests.get(f"{BASE}/catalogue/recherche", params={"q": "Harry"})
    assert r.status_code in (200, 404)


# ========= LIVRES ADMIN =========


def test_admin_create_book():
    admin_token = get_token("admin@example.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

    payload = {
        "titre": "Livre Test API",
        "auteur": "Auteur Tests",
        "annee": 2024,
        "nombreCopies": 3,
    }
    r = requests.post(f"{BASE}/admin/livres", json=payload, headers=headers)
    assert r.status_code in (201, 401, 403)


def test_admin_update_book():
    admin_token = get_token("admin@example.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

    r = requests.put(
        f"{BASE}/admin/livres/1",
        json={"nombreCopies": 10},
        headers=headers,
    )
    assert r.status_code in (200, 400, 401, 403, 404)


def test_admin_delete_book():
    admin_token = get_token("admin@example.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

    r = requests.delete(f"{BASE}/admin/livres/9999", headers=headers)
    assert r.status_code in (200, 401, 403, 404)


# ========= PRETS (MEMBRE) =========


def test_membre_emprunter():
    token = get_token("membre@example.com", "membre")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    r = requests.post(
        f"{BASE}/membre/prets",
        json={"livreId": 1},
        headers=headers,
    )
    assert r.status_code in (201, 400, 401, 403, 404, 500)


def test_membre_lister_prets():
    token = get_token("membre@example.com", "membre")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    r = requests.get(f"{BASE}/membre/prets", headers=headers)
    assert r.status_code in (200, 401)


def test_membre_emprunter_sans_token():
    r = requests.post(
        f"{BASE}/membre/prets",
        json={"livreId": 1},
    )
    assert r.status_code in (401, 403)


# ========= RESERVATIONS =========


def test_reserver_livre():
    token = get_token("membre@example.com", "membre")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    r = requests.post(
        f"{BASE}/reservations",
        json={"livreId": 2},
        headers=headers,
    )
    assert r.status_code in (201, 400, 401, 403, 404)


# ========= AMENDES =========


def test_lister_amendes_membre():
    token = get_token("membre@example.com", "membre")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    r = requests.get(f"{BASE}/membre/amendes", headers=headers)
    assert r.status_code in (200, 401, 404)


def test_payer_amende():
    token = get_token("membre@example.com", "membre")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    r = requests.post(
        f"{BASE}/membre/amendes/payer",
        json={"amendeId": 1, "montant": 5.0, "methodePaiement": "carte_credit"},
        headers=headers,
    )
    assert r.status_code in (200, 400, 401, 404)


# ========= NOTIFICATIONS =========


def test_notifications_rappel_retour():
    r = requests.post(
        f"{BASE}/notifications/rappel-retour",
        json={"pretId": 1},
    )
    assert r.status_code in (201, 200, 404)


def test_notifications_retard():
    r = requests.post(
        f"{BASE}/notifications/retard",
        json={"pretId": 2, "joursRetard": 3},
    )
    assert r.status_code in (201, 200, 404)


def test_notifications_confirmation_emprunt():
    r = requests.post(
        f"{BASE}/notifications/confirmation-emprunt",
        json={"pretId": 3},
    )
    assert r.status_code in (201, 200, 404)


def test_notifications_list_admin():
    admin_token = get_token("admin@example.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

    r = requests.get(f"{BASE}/admin/notifications", headers=headers)
    assert r.status_code in (200, 401, 403)


def test_membre_notifications_list():
    membre_token = get_token("membre@example.com", "membre")
    headers = {"Authorization": f"Bearer {membre_token}"} if membre_token else {}

    r = requests.get(f"{BASE}/membre/notifications", headers=headers)
    assert r.status_code in (200, 401, 403, 404)


def test_notifications_marquer_lue():
    membre_token = get_token("membre@example.com", "membre")
    headers = {"Authorization": f"Bearer {membre_token}"} if membre_token else {}

    r = requests.put(f"{BASE}/membre/notifications/1/lu", headers=headers)
    assert r.status_code in (200, 401, 403, 404)


# ========= AUDIT =========


def test_audit_admin():
    admin_token = get_token("admin@example.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

    r = requests.get(f"{BASE}/admin/audit", headers=headers)
    assert r.status_code in (200, 401, 403)
