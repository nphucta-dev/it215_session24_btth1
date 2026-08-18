from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from middleware.rbac_middleware import RBACMiddleware

app = FastAPI(
    title="MegaMart ERP - RBAC & CORS Security Demo",
    version="1.0.0",
    description=(
        "Demo API implementing centralized RBAC authorization middleware and strict CORS policy."
    ),
)

# Add RBAC first and CORS second so CORS is the outer layer.
# This lets browser OPTIONS preflight requests be handled before RBAC checks.
app.add_middleware(RBACMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://internal.megamart.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-User-Role"],
    allow_credentials=False,
)


@app.get("/api/v1/salary/modify", tags=["RBAC Demo"])
async def modify_salary(request: Request):
    return {
        "message": "Salary modification API accessed",
        "role": request.state.user_role,
    }


@app.get("/api/v1/system/settings", tags=["RBAC Demo"])
async def system_settings(request: Request):
    return {
        "message": "System settings API accessed",
        "role": request.state.user_role,
    }


@app.get("/api/v1/profile", tags=["RBAC Demo"])
async def profile(request: Request):
    return {
        "message": "Personal profile accessed",
        "role": request.state.user_role,
    }


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok"}
