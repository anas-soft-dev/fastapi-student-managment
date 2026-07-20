"""
Database seeder.

Run with:  python seeder.py

Inserts roles (admin, student, teacher), creates all permissions used across
the routers, assigns the relevant permissions to each role, and creates a
default admin user. Safe to run multiple times — existing roles/permissions
and the admin user are reused, not duplicated.
"""

from app.database import Base, engine, SessionLocal
import app.models.user
import app.models.role
import app.models.subject
from app.models.role import Role, Permission
from app.models.user import User
from app.auth import make_hash

# Default admin account created on first seed
ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "12345678"

# All permissions used across the application routers
PERMISSIONS = [
    # profile
    "view profile","update profile",
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
        "update profile",
        "view student",
        "view subject",
        "assign subject", "revoke subject",
        "mark attendance",
        "view attendance report",
    ],
    "student": [
        "view profile",
        "update profile",
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


def get_or_create_admin_user(db, admin_role: Role) -> User:
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if user:
        return user

    user = User(
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        password=make_hash(ADMIN_PASSWORD),
    )
    user.roles.append(admin_role)
    db.add(user)
    db.flush()
    return user


def seed():
    # Make sure all tables exist before seeding
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        # 1. Create all permissions
        permissions = {name: get_or_create_permission(db, name) for name in PERMISSIONS}

        # 2. Create roles and assign their permissions
        roles = {}
        for role_name, perm_names in ROLE_PERMISSIONS.items():
            role = get_or_create_role(db, role_name)
            roles[role_name] = role

            existing = {p.name for p in role.permissions}
            for perm_name in perm_names:
                if perm_name not in existing:
                    role.permissions.append(permissions[perm_name])

        # 3. Create the default admin user (skipped if the email already exists)
        existed = db.query(User).filter(User.email == ADMIN_EMAIL).first() is not None
        get_or_create_admin_user(db, roles["admin"])

        db.commit()
        print("Seeding completed successfully.")
        print(f"  Roles: {', '.join(ROLE_PERMISSIONS.keys())}")
        print(f"  Permissions: {len(PERMISSIONS)}")
        if existed:
            print(f"  Admin user: {ADMIN_EMAIL} (already existed, unchanged)")
        else:
            print(f"  Admin user: {ADMIN_EMAIL} / {ADMIN_PASSWORD} (created)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
