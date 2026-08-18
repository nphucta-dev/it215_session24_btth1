# MegaMart RBAC & CORS - Hồ sơ sản phẩm

## Nỗi đau khách hàng

MegaMart có hai vấn đề: kiểm tra role thủ công ở từng endpoint và CORS mở `*`. Cả hai đều làm tăng nguy cơ rò rỉ hoặc truy cập trái phép.

## Người dùng

- ADMIN: toàn quyền.
- HR: quản lý dữ liệu nhân sự/lương.
- STAFF: chỉ xem hồ sơ cá nhân.

## Chức năng

1. Centralized RBAC middleware.
2. Salary endpoint chỉ ADMIN/HR.
3. System settings chỉ ADMIN.
4. Profile cho ADMIN/HR/STAFF.
5. Strict CORS.
6. OPTIONS không yêu cầu role.
7. Test tự động.

## Quy tắc

- Role hợp lệ và thuộc tập quyền -> request đi tiếp.
- Role thiếu/không có quyền -> `403` và `{"error":"Permission Denied"}`.
- OPTIONS -> bỏ qua RBAC để CORS xử lý.
- Origin ngoài allowlist -> không được browser cấp CORS permission.

## API

| Method | Path | Role |
|---|---|---|
| GET | `/api/v1/salary/modify` | ADMIN, HR |
| GET | `/api/v1/system/settings` | ADMIN |
| GET | `/api/v1/profile` | ADMIN, HR, STAFF |
| GET | `/health` | Public |
