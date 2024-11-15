from fastapi import FastAPI, Depends
from fastapi import FastAPI, status, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from . import auth, models, file_upload
from .auth import get_current_user
from .database import engine, SessionLocal, Base
from .middleware import TokenAuthMiddleware
from . import rag_integration

app = FastAPI()

# Include routers
app.include_router(auth.router)
app.include_router(file_upload.router)
app.include_router(rag_integration.router)

# Add middleware
app.add_middleware(TokenAuthMiddleware)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Dependency to get a database session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Annotated dependencies
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return {"User": user}
