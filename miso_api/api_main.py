import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import genesis_router, auth_router
from .database import engine, SessionLocal
from .models import db_models
from .security import get_password_hash

# Create database tables
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MISO Core API",
    version="0.1.0",
    description="The central Hub for orchestrating the MISO Fusion platform.",
)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    # Check if the admin user exists
    user = db.query(db_models.User).filter(db_models.User.username == "miso_admin").first()
    if not user:
        # Create the admin user if it doesn't exist
        hashed_password = get_password_hash("madeitso")
        admin_user = db_models.User(username="miso_admin", hashed_password=hashed_password)
        db.add(admin_user)
        db.commit()
        print("INFO: 'miso_admin' user created in the database.")
    db.close()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(genesis_router.router)

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "MISO Core API is operational."}

if __name__ == "__main__":
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)
