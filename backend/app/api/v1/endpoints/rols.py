from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.user import Role, Permission
from app.models.permission import RolePermission
from app.schemas.role import RoleCreate, RoleRead
from app.schemas.permission import PermissionRead
from app.core.rbac import require_superuser
from app.websockets.connection_manager import sio

router = APIRouter()


def build_role_rooms(role_id: int) -> list[str]:
    return [f"role_{role_id}", "role_1"]


@router.post(
    "/",
    response_model=RoleRead,
    dependencies=[Depends(require_superuser())],
)
async def create_role(role_in: RoleCreate, db: Session = Depends(get_session)):
    # 1. Check if role exists
    existing_role = db.exec(select(Role).where(Role.name == role_in.name)).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")

    # 2. Map schema to model
    db_role = Role(name=role_in.name)
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    await sio.emit(
        "msg",
        {"type": "role_created", "payload": db_role.dict()},
        room=build_role_rooms(db_role.id),
    )
    return db_role

@router.get(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(require_superuser())],
)
def read_role(role_id: int, db: Session = Depends(get_session)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.get(
    "/",
    response_model=list[RoleRead],
    dependencies=[Depends(require_superuser())],
)
def read_roles(db: Session = Depends(get_session)):
    roles = db.exec(select(Role)).all()
    return roles

@router.put(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(require_superuser())],
)
async def update_role(role_id: int, role_in: RoleCreate, db: Session = Depends(get_session)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    # Check if new name conflicts with existing role
    if role.name != role_in.name:
        existing_role = db.exec(select(Role).where(Role.name == role_in.name)).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role name already exists")
    role.name = role_in.name
    db.add(role)
    db.commit()
    db.refresh(role)
    await sio.emit(
        "msg",
        {"type": "role_updated", "payload": role.dict()},
        room=build_role_rooms(role_id),
    )
    return role

@router.delete(
    "/{role_id}",
    response_model=dict,
    dependencies=[Depends(require_superuser())],
)
async def delete_role(role_id: int, db: Session = Depends(get_session)):
    # if role_id == 1 prevent deletion of superuser role
    if role_id == 1:
        raise HTTPException(status_code=400, detail="Cannot delete superuser role")
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()
    await sio.emit(
        "msg",
        {"type": "role_deleted", "payload": {"role_id": role_id}},
        room=build_role_rooms(role_id),
    )
    return {"detail": "Role deleted"}


@router.get(
    "/{role_id}/permissions",
    response_model=list[PermissionRead],
    dependencies=[Depends(require_superuser())],
)
def read_role_permissions(role_id: int, db: Session = Depends(get_session)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role.permissions or []


@router.post(
    "/{role_id}/permissions/{permission_id}",
    response_model=dict,
    dependencies=[Depends(require_superuser())],
)
async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_session),
):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    permission = db.get(Permission, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    link_exists = db.exec(
        select(RolePermission).where(
            (RolePermission.role_id == role_id)
            & (RolePermission.permission_id == permission_id)
        )
    ).first()
    if link_exists:
        raise HTTPException(status_code=400, detail="Permission already assigned")

    db.add(RolePermission(role_id=role_id, permission_id=permission_id))
    db.commit()
    
    # Refresh to get updated relationships
    db.refresh(role)
    db.refresh(permission)

    await sio.emit(
        "msg",
        {
            "type": "role_permission_added",
            "payload": {"role": role.dict(), "permission": permission.dict()},
        },
        room=build_role_rooms(role_id),
    )
    return {"detail": "Permission assigned"}


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    response_model=dict,
    dependencies=[Depends(require_superuser())],
)
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_session),
):
    link = db.exec(
        select(RolePermission).where(
            (RolePermission.role_id == role_id)
            & (RolePermission.permission_id == permission_id)
        )
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Role permission not found")

    db.delete(link)
    db.commit()
    role = db.get(Role, role_id)
    permission = db.get(Permission, permission_id)
    await sio.emit(
        "msg",
        {
            "type": "role_permission_removed",
            "payload": {"role": role.dict(), "permission": permission.dict()},
        },
        room=build_role_rooms(role_id),
    )
    return {"detail": "Permission removed"}