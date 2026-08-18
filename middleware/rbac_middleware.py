from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest


class RBACMiddleware(BaseHTTPMiddleware):
    """Centralized Role-Based Access Control middleware.

    The assignment explicitly allows a role to be simulated via X-User-Role.
    In production, this header must NOT be trusted from the client; it should
    be derived from a validated JWT/session instead.
    """

    ROLE_PERMISSIONS = {
        "/api/v1/salary/modify": {"ADMIN", "HR"},
        "/api/v1/system/settings": {"ADMIN"},
        "/api/v1/profile": {"ADMIN", "HR", "STAFF"},
    }

    async def dispatch(self, request: StarletteRequest, call_next):
        # CORS preflight requests must never be blocked by RBAC.
        if request.method == "OPTIONS":
            return await call_next(request)

        required_roles = self.ROLE_PERMISSIONS.get(request.url.path)

        # Routes outside the protected mapping are public.
        if required_roles is None:
            return await call_next(request)

        role = request.headers.get("X-User-Role")
        if not role:
            return JSONResponse(
                status_code=403,
                content={"error": "Permission Denied"},
            )

        role = role.strip().upper()
        if role not in required_roles:
            return JSONResponse(
                status_code=403,
                content={"error": "Permission Denied"},
            )

        # Make the validated role available to the endpoint.
        request.state.user_role = role
        return await call_next(request)
