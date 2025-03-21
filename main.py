from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.routes.contacts import router as contacts_router
from src.routes.users import router as users_router

# Setup limiter (without app.state)
limiter = Limiter(key_func=get_remote_address)

# Create app
app = FastAPI(
    title="Contacts API",
    description="API for managing contacts",
    version="1.0.0",
)


from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific domains in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register exception handler directly
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded. Please try again later."},
    )


# Include routers
app.include_router(contacts_router, prefix="/contacts", tags=["Contacts"])
app.include_router(users_router, prefix="/users", tags=["Users"])


# Root route
@app.get("/")
@limiter.limit("5/minute")  # Example usage
async def root(request: Request):
    return {"message": "Welcome to the Contacts API"}
