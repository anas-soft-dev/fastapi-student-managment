"""
Database seeder.

Run with:  python seeder.py

Inserts roles (admin, student, teacher), creates all permissions used across
the routers, and assigns the relevant permissions to each role. Safe to run
multiple times — existing roles/permissions are reused, not duplicated.
"""

from app.database import Base, engine, SessionLocal
import app.models.user
import app.models.role
import app.models.subject
from app.models.role import Role, Permission

# All permissions used across the application routers
PERMISSIONS = [
    # profile
    "view profile",
    # teacher
    "view teacher", "add teacher", "edit teacher", "delete teacher",
    # student
    "view student", "add student", "edit student", "delete student",
    # subject
    "view subject", "add subject", "edit subject", "delete subject",
    "assign subject", "revoke subject",
    # teacher <-> subject assignment
    "assign teacher subject", "revoke teacher subject",
    # attendance
    "mark attendance", "view attendance report", "view own attendance",
]

# Permissions granted to each role
ROLE_PERMISSIONS = {
    "admin": PERMISSIONS,  # admin gets everything
    "teacher": [
        "view profile",
        "view student",
        "view subject",
        "assign subject", "revoke subject",
        "mark attendance",
        "view attendance report",
    ],
    "student": [
        "view profile",
        "view subject",
        "view own attendance",
    ],
}


def get_or_create_permission(db, name: str) -> Permission:
    permission = db.query(Permission).filter(Permission.name == name).first()
    if not permission:
        permission = Permission(name=name)
        db.add(permission)
        db.commit()
        db.refresh(permission)
    return permission


def get_or_create_role(db, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if not role:
        role = Role(name=name)
        db.add(role)
        db.flush()
    return role


def seed():
    # Make sure all tables exist before seeding
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        # 1. Create all permissions
        permissions = {name: get_or_create_permission(db, name) for name in PERMISSIONS}

        # 2. Create roles and assign their permissions
        for role_name, perm_names in ROLE_PERMISSIONS.items():
            role = get_or_create_role(db, role_name)

            existing = {p.name for p in role.permissions}
            for perm_name in perm_names:
                if perm_name not in existing:
                    role.permissions.append(permissions[perm_name])

        db.commit()
        print("Seeding completed successfully.")
        print(f"  Roles: {', '.join(ROLE_PERMISSIONS.keys())}")
        print(f"  Permissions: {len(PERMISSIONS)}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
