from fastapi import FastAPI
from src.routes.contacts import router as contacts_router

app = FastAPI(
    title="Contacts API", description="API for managing contacts", version="1.0.0"
)

# Include routes
app.include_router(contacts_router, prefix="/contacts", tags=["Contacts"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Contacts API"}
