# MegaMart ERP - Centralized RBAC Middleware & Strict CORS

## 1. Mục tiêu

Bài thực hành xây dựng một Backend FastAPI cho hệ thống ERP nội bộ MegaMart nhằm vá hai lỗ hổng:

1. **Thiếu phân quyền tập trung:** nhân viên thường có thể gọi API nhạy cảm nếu biết URL.
2. **CORS lỏng lẻo:** Backend đang cho phép mọi origin (`*`), làm tăng rủi ro khi người dùng truy cập website độc hại.

Project này triển khai:

- **RBAC tập trung** bằng Custom Middleware.
- 3 role: `ADMIN`, `HR`, `STAFF`.
- Role được mô phỏng qua header `X-User-Role` theo đúng yêu cầu bài tập.
- CORS chỉ cho `https://internal.megamart.com`.
- Chỉ cho phép `GET`, `POST`.
- Chỉ cho phép `Content-Type`, `X-User-Role`.
- Không chặn request `OPTIONS` tại RBAC middleware.
- Có test RBAC và CORS.

> **Lưu ý bảo mật:** `X-User-Role` chỉ phù hợp cho mô phỏng bài tập. Không được tin tưởng role do client tự gửi trong hệ thống production. Production nên lấy role từ JWT/session đã được xác thực và ký hợp lệ.

---

## 2. Cấu trúc thư mục

```text
megamart-rbac/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── ARCHITECTURE.md
├── API_TEST_CASES.md
├── middleware/
│   ├── __init__.py
│   └── rbac_middleware.py
└── tests/
    ├── __init__.py
    ├── test_rbac.py
    └── test_cors.py
```

### Trách nhiệm module

- `main.py`: khởi tạo FastAPI, cấu hình CORS, đăng ký RBAC middleware và khai báo endpoint demo.
- `middleware/rbac_middleware.py`: trung tâm kiểm tra role, không lặp logic `if role...` trong từng API.
- `tests/`: kiểm thử quyền và chính sách CORS.
- `ARCHITECTURE.md`: giải thích Request-Response Pipeline và luồng bảo mật.
- `API_TEST_CASES.md`: các ca kiểm thử thủ công bằng curl/PowerShell.

---

## 3. Role Matrix

| Endpoint | ADMIN | HR | STAFF |
|---|:---:|:---:|:---:|
| `GET /api/v1/profile` | ✅ | ✅ | ✅ |
| `GET /api/v1/salary/modify` | ✅ | ✅ | ❌ |
| `GET /api/v1/system/settings` | ✅ | ❌ | ❌ |

Mọi role sai hoặc thiếu header trên route cần bảo vệ đều nhận:

```http
403 Forbidden
```

```json
{
  "error": "Permission Denied"
}
```

---

## 4. CORS Policy

Backend chỉ cho phép:

```text
Origin: https://internal.megamart.com
```

Methods:

```text
GET
POST
```

Headers:

```text
Content-Type
X-User-Role
```

Không sử dụng:

```python
allow_origins=["*"]
```

Website `https://evil-attacker.xyz` không nằm trong allowlist nên trình duyệt không được cấp CORS permission để đọc response.

`allow_credentials=False` được chọn vì bài yêu cầu không dùng wildcard và không yêu cầu cookie/session credentials. Nếu sau này bật credentials, origin phải tiếp tục là danh sách cụ thể, tuyệt đối không dùng `*`.

---

## 5. Request-Response Pipeline

```text
Browser / Frontend
        |
        v
+----------------------+
| CORS Middleware      |
| origin/method/header |
+----------------------+
        |
        v
+----------------------+
| RBAC Middleware      |
| X-User-Role -> role  |
+----------------------+
        |
        v
+----------------------+
| FastAPI Router       |
| Controller/Endpoint  |
+----------------------+
        |
        v
     Response
```

### Vì sao OPTIONS không cần role?

Browser thường gửi request `OPTIONS` để kiểm tra CORS trước request thực tế. Nếu RBAC chặn `OPTIONS` và bắt role, preflight sẽ thất bại trước khi request thật được gửi. Vì vậy middleware chủ động cho `OPTIONS` đi tiếp để `CORSMiddleware` xử lý.

---

## 6. Cách chạy

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Ứng dụng chạy tại:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 7. Chạy test

```bash
pytest -q
```

Test bao phủ:

- ADMIN truy cập toàn bộ endpoint.
- HR truy cập salary/profile nhưng bị chặn system settings.
- STAFF chỉ truy cập profile.
- Thiếu role -> 403.
- Role không tồn tại -> 403.
- Role viết thường -> được chuẩn hóa.
- Health endpoint public.
- Origin chính thức được CORS cho phép.
- Origin độc hại không nhận `Access-Control-Allow-Origin`.
- OPTIONS không yêu cầu role.
- GET/POST được phép.
- DELETE bị CORS từ chối.

---

## 8. Ví dụ nhanh

### STAFF xem profile

```bash
curl -H "X-User-Role: STAFF" http://127.0.0.1:8000/api/v1/profile
```

### STAFF gọi system settings

```bash
curl -i -H "X-User-Role: STAFF" http://127.0.0.1:8000/api/v1/system/settings
```

Kết quả dự kiến:

```json
{"error":"Permission Denied"}
```

### ADMIN gọi system settings

```bash
curl -H "X-User-Role: ADMIN" http://127.0.0.1:8000/api/v1/system/settings
```

### HR gọi salary

```bash
curl -H "X-User-Role: HR" http://127.0.0.1:8000/api/v1/salary/modify
```

---

## 9. Giải thích Authentication vs Authorization

**Authentication** trả lời: "Bạn là ai?"

**Authorization** trả lời: "Bạn được phép làm gì?"

Trong bài này, danh tính người dùng được giả lập bằng `X-User-Role`. Middleware thực hiện phần **Authorization/RBAC** bằng cách đối chiếu role với ma trận quyền.

Trong production nên thay:

```text
X-User-Role
```

bằng:

```text
Authorization: Bearer <JWT>
        |
        v
Verify signature + expiration
        |
        v
Extract role from trusted claims
        |
        v
RBAC Middleware
```

---

## 10. Kết luận bảo mật

Thiết kế này loại bỏ việc viết kiểm tra role thủ công trong từng endpoint. Khi cần thay đổi quyền, developer chỉ cập nhật `ROLE_PERMISSIONS` trong một module trung tâm.

CORS cũng được thu hẹp từ "mọi origin" thành đúng domain Frontend chính thức của MegaMart, giảm khả năng một website bên ngoài sử dụng trình duyệt của nhân viên để thực hiện các cross-origin request được trình duyệt cấp quyền đọc response.
