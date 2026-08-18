from fastapi.testclient import TestClient

from main import app

client = TestClient(app)



def test_admin_can_access_all_protected_routes():
    headers = {"X-User-Role": "ADMIN"}
    assert client.get("/api/v1/profile", headers=headers).status_code == 200
    assert client.get("/api/v1/salary/modify", headers=headers).status_code == 200
    assert client.get("/api/v1/system/settings", headers=headers).status_code == 200



def test_hr_can_access_salary_and_profile_but_not_settings():
    headers = {"X-User-Role": "HR"}
    assert client.get("/api/v1/profile", headers=headers).status_code == 200
    assert client.get("/api/v1/salary/modify", headers=headers).status_code == 200

    response = client.get("/api/v1/system/settings", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"error": "Permission Denied"}



def test_staff_can_only_access_profile():
    headers = {"X-User-Role": "STAFF"}
    assert client.get("/api/v1/profile", headers=headers).status_code == 200

    for path in ["/api/v1/salary/modify", "/api/v1/system/settings"]:
        response = client.get(path, headers=headers)
        assert response.status_code == 403
        assert response.json() == {"error": "Permission Denied"}



def test_missing_role_is_denied():
    response = client.get("/api/v1/profile")
    assert response.status_code == 403
    assert response.json() == {"error": "Permission Denied"}



def test_unknown_role_is_denied():
    response = client.get("/api/v1/profile", headers={"X-User-Role": "GUEST"})
    assert response.status_code == 403
    assert response.json() == {"error": "Permission Denied"}



def test_role_is_case_insensitive():
    response = client.get("/api/v1/profile", headers={"X-User-Role": "admin"})
    assert response.status_code == 200
    assert response.json()["role"] == "ADMIN"



def test_public_health_endpoint_does_not_require_role():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
