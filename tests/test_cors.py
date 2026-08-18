from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


OFFICIAL_ORIGIN = "https://internal.megamart.com"
EVIL_ORIGIN = "https://evil-attacker.xyz"



def test_official_origin_is_allowed():
    response = client.get("/api/v1/profile", headers={"X-User-Role": "STAFF", "Origin": OFFICIAL_ORIGIN})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == OFFICIAL_ORIGIN



def test_evil_origin_is_not_allowed():
    response = client.get("/api/v1/profile", headers={"X-User-Role": "STAFF", "Origin": EVIL_ORIGIN})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers



def test_preflight_does_not_require_role():
    response = client.options(
        "/api/v1/profile",
        headers={
            "Origin": OFFICIAL_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-User-Role",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == OFFICIAL_ORIGIN
    assert response.headers.get("access-control-allow-methods") == "GET, POST"



def test_post_is_allowed_by_cors_policy():
    response = client.options(
        "/api/v1/profile",
        headers={
            "Origin": OFFICIAL_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, X-User-Role",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-methods") == "GET, POST"



def test_delete_is_not_allowed_by_cors_policy():
    response = client.options(
        "/api/v1/profile",
        headers={
            "Origin": OFFICIAL_ORIGIN,
            "Access-Control-Request-Method": "DELETE",
        },
    )
    assert response.status_code == 400
