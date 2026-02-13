# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import TokenWithUser, TokenData, UserLogin, UserOut
from app.core.security import verify_password, create_access_token, get_current_user
from app.websockets.connection_manager import disconnect_user

router = APIRouter()

@router.post("/login", response_model=TokenWithUser)
def login(response: Response,form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    # 1. Retrieve user by username
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 3. Create access token
    access_token = create_access_token(subject=str(user.id))
    # return token with userout
    # return Token(access_token=access_token, token_type="bearer")
    # set header with token and return user info
    # response.headers["Authorization"] = f"Bearer {access_token}"
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer", "user": UserOut(user=user)}
    

# /api/v1/auth/me endpoint to get current user info
@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return {"user": current_user}

# /api/v1/auth/logout endpoint to logout user
@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    # disconnect user from all websocket rooms
    await disconnect_user(current_user.id)
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}