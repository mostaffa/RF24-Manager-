from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.core.security import get_current_user

def require_permission(permission: str):
    def checker(user: User = Depends(get_current_user)):
        role = user.role
        if not role:
            raise HTTPException(status_code=403, detail="No role assigned")

        perms = {p.name for p in role.permissions}
        if permission not in perms:
            raise HTTPException(status_code=403, detail="Permission denied")

        return True
    return checker


def require_superuser():
    def checker(user: User = Depends(get_current_user)):
        role = user.role
        print(f"\u001b[32mUser {user.username} has role {role.name if role else 'None'}\u001b[0m")
        if not role or role.id != 1:
            raise HTTPException(
                status_code=403,
                detail="Superuser role required",
            )
        return True
    return checker

