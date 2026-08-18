# API Test Cases

## 1. STAFF profile

```bash
curl -i -H "X-User-Role: STAFF" http://127.0.0.1:8000/api/v1/profile
```

Expected: `200 OK`.

## 2. STAFF salary

```bash
curl -i -H "X-User-Role: STAFF" http://127.0.0.1:8000/api/v1/salary/modify
```

Expected:

```text
403 Forbidden
```

```json
{"error":"Permission Denied"}
```

## 3. HR salary

```bash
curl -i -H "X-User-Role: HR" http://127.0.0.1:8000/api/v1/salary/modify
```

Expected: `200 OK`.

## 4. HR settings

```bash
curl -i -H "X-User-Role: HR" http://127.0.0.1:8000/api/v1/system/settings
```

Expected: `403 Forbidden`.

## 5. ADMIN settings

```bash
curl -i -H "X-User-Role: ADMIN" http://127.0.0.1:8000/api/v1/system/settings
```

Expected: `200 OK`.

## 6. Missing role

```bash
curl -i http://127.0.0.1:8000/api/v1/profile
```

Expected: `403 Forbidden`.

## 7. Official CORS preflight

```bash
curl -i -X OPTIONS http://127.0.0.1:8000/api/v1/profile ^
  -H "Origin: https://internal.megamart.com" ^
  -H "Access-Control-Request-Method: GET" ^
  -H "Access-Control-Request-Headers: X-User-Role"
```

Expected: `200 OK` with CORS headers.

## 8. Evil origin preflight

```bash
curl -i -X OPTIONS http://127.0.0.1:8000/api/v1/profile ^
  -H "Origin: https://evil-attacker.xyz" ^
  -H "Access-Control-Request-Method: GET"
```

Expected: CORS response does not grant `Access-Control-Allow-Origin: https://evil-attacker.xyz`.

## 9. Unsupported DELETE preflight

```bash
curl -i -X OPTIONS http://127.0.0.1:8000/api/v1/profile ^
  -H "Origin: https://internal.megamart.com" ^
  -H "Access-Control-Request-Method: DELETE"
```

Expected: `400 Bad Request` from the CORS middleware.
