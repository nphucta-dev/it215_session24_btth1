# Kiến trúc hệ thống MegaMart RBAC

## 1. Thành phần

### FastAPI application
Điều phối route, middleware và response.

### CORSMiddleware
Được đặt ở lớp ngoài RBAC để xử lý browser preflight trước khi authorization.

### RBACMiddleware
Đọc URL, tra `ROLE_PERMISSIONS`, lấy `X-User-Role`, chuẩn hóa và kiểm tra quyền.

### Endpoint
Chỉ tập trung xử lý nghiệp vụ của endpoint. Endpoint không chứa logic RBAC lặp lại.

---

## 2. Luồng request

```text
Frontend
   |
   | HTTP request + Origin
   v
CORS Middleware
   |
   |-- Origin hợp lệ --> tiếp tục
   |-- Origin lạ -----> browser không được cấp CORS permission
   v
RBAC Middleware
   |
   |-- OPTIONS -------> tiếp tục để CORS xử lý preflight
   |
   |-- Route public --> tiếp tục
   |
   |-- Protected route
   |       |
   |       +--> thiếu X-User-Role --> 403
   |       |
   |       +--> role không đủ quyền --> 403
   |       |
   |       +--> role hợp lệ --> tiếp tục
   v
FastAPI Endpoint
   |
   v
JSON Response
```

---

## 3. Cơ chế RBAC tập trung

`ROLE_PERMISSIONS` là policy table:

```python
ROLE_PERMISSIONS = {
    "/api/v1/salary/modify": {"ADMIN", "HR"},
    "/api/v1/system/settings": {"ADMIN"},
    "/api/v1/profile": {"ADMIN", "HR", "STAFF"},
}
```

Ưu điểm:

- Không lặp `if role == ...` ở endpoint.
- Policy tập trung, dễ audit.
- Dễ thêm route mới.
- Dễ viết unit/integration test.

---

## 4. CORS policy

```python
allow_origins=["https://internal.megamart.com"]
allow_methods=["GET", "POST"]
allow_headers=["Content-Type", "X-User-Role"]
```

Không có wildcard origin.

Một request từ:

```text
https://evil-attacker.xyz
```

không được browser cấp `Access-Control-Allow-Origin` tương ứng.

---

## 5. Giới hạn của mô hình mô phỏng

Client có thể tự gửi `X-User-Role: ADMIN`, vì vậy đây không phải cơ chế authentication thực tế.

Production cần:

```text
Login
  -> JWT signed by server
  -> Authorization: Bearer <token>
  -> Verify JWT
  -> Extract role claim
  -> RBAC
```

Điểm quan trọng: **RBAC middleware phải tin một nguồn role đã được authentication kiểm chứng, không tin header role do trình duyệt tùy ý tạo.**
