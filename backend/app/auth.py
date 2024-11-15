from .database import SessionLocal
from .models import Users
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2AuthorizationCodeBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2AuthorizationCodeBearer(
    tokenUrl='auth/token',
    authorizationUrl='auth/authorize'
)


class CreateUserRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def create_access_token(username: str, user_id: int, expires_delta: timedelta = timedelta(hours=1)):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow().replace(tzinfo=timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )
        return {'username': username, "id": user_id}
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        ) from e


def authenticate_user(username: str, password: str, db: Annotated[Session, Depends(get_db)]):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    existing_user = db.query(Users).filter(
        Users.username == create_user_request.username
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password)
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return {"message": "User created successfully", "username": create_user_model.username}


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency, response: Response):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    access_token = create_access_token(
        username=user.username, user_id=user.id, expires_delta=timedelta(
            minutes=20)
    )
    expires = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(minutes=30)
    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=expires,
        httponly=True,
        secure=True,  # make sure to set this to True in production
        samesite='Strict',
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_user_info(user: Annotated[dict, Depends(get_current_user)]):
    return {"user": user}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}
