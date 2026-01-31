from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User

# load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path=env_path)

# -------------------------------------------------------------------
# Config (move to env later)
# -------------------------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_SUPER_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# -------------------------------------------------------------------
# Security utils
# -------------------------------------------------------------------

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# -------------------------------------------------------------------
# Password helpers
# -------------------------------------------------------------------

def hash_password(password: str) -> str:
    # argon2 doesn't have the 72-byte limitation that bcrypt has
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# -------------------------------------------------------------------
# JWT helpers
# -------------------------------------------------------------------

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# -------------------------------------------------------------------
# Auth dependencies
# -------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.exec(
        select(User).where(User.id == int(user_id))
    ).first()

    if not user or not user.active:
        raise credentials_exception

    return user
