from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.user import Role
from app.schemas.role import RoleCreate, RoleRead

router = APIRouter()
@router.post("/", response_model=RoleRead)
def create_role(role_in: RoleCreate, db: Session = Depends(get_session)):
    # 1. Check if role exists
    existing_role = db.exec(select(Role).where(Role.name == role_in.name)).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")

    # 2. Map schema to model
    db_role = Role(name=role_in.name)
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/{role_id}", response_model=RoleRead)
def read_role(role_id: int, db: Session = Depends(get_session)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.get("/", response_model=list[RoleRead])
def read_roles(db: Session = Depends(get_session)):
    roles = db.exec(select(Role)).all()
    return roles

@router.delete("/{role_id}", response_model=dict)
def delete_role(role_id: int, db: Session = Depends(get_session)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()
    return {"detail": "Role deleted"}