from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
from typing import Optional

from app.persistence.database import get_db
from app.models.schemas import User, UserRole
from app.core.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: UserRole = UserRole.SEEKER

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user exists
    statement = select(User).where(User.email == request.email)
    existing_user = db.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        full_name=request.full_name,
        password_hash=hashed_password,
        role=request.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"status": "success", "user_id": user.id}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user
    statement = select(User).where(User.email == form_data.username)
    user = db.exec(statement).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }
