from django.contrib.auth import get_user_model
from typing import Optional
from django.db.models import QuerySet

User = get_user_model()


def create_user(
    username: str, password: str, email: Optional[str] = None, **extra_fields
) -> User:
    return User.objects.create_user(
        username=username,
        password=password,
        email=email,
        **extra_fields,
    )


def get_user_by_username(username: str) -> Optional[User]:
    return User.objects.filter(username=username).first()


def get_all_users() -> QuerySet[User, User]:
    return User.objects.all()


def user_exists(username: str) -> bool:
    return User.objects.filter(username=username).exists()
