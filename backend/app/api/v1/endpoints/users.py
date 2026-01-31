from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.rbac import require_permission
from app.core.security import hash_password

router = APIRouter()

@router.post("/",
            response_model=UserRead,
            dependencies=[Depends(require_permission("user:create"))]
            )
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_session)):
    # 1. Check if user exists
    existing_user = db.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # 2. Map schema to model and hash password
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role_id=user_in.role_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/{user_id}",
             response_model=UserRead,
             dependencies=[Depends(require_permission("user:read"))]
             )
def read_user(user_id: int, db: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id).options(selectinload(User.role))
    user = db.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/",
            response_model=list[UserRead],
            dependencies=[Depends(require_permission("user:read"))]
            )
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_session)):
    statement = select(User).options(selectinload(User.role)).offset(skip).limit(limit)
    users = db.exec(statement).all()
    return users

@router.delete("/{user_id}", response_model=dict,
               dependencies=[Depends(require_permission("user:delete"))]
               )
def delete_user(user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

@router.put("/{user_id}", response_model=UserRead,
            dependencies=[Depends(require_permission("user:update"))]
            )
def update_user(user_id: int, user_in: UserCreate, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = user_in.username
    user.email = user_in.email
    user.hashed_password = hash_password(user_in.password)
    user.role_id = user_in.role_id

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

