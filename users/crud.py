from django.contrib.auth import get_user_model
from typing import Optional
from django.db.models import QuerySet
import logging

User = get_user_model()
logger = logging.getLogger("users")


def create_user(
    username: str, password: str, email: Optional[str] = None, **extra_fields
) -> User:
    logger.info(f"Creating user {username}")
    return User.objects.create_user(
        username=username,
        password=password,
        email=email,
        **extra_fields,
    )


def get_user_by_username(username: str) -> Optional[User]:
    logger.info(f"Getting user {username}")
    return User.objects.filter(username=username).first()


def get_all_users() -> QuerySet[User, User]:
    logger.info("Getting all users")
    return User.objects.all()


def user_exists(username: str) -> bool:
    logger.info(f"Getting user {username}")
    return User.objects.filter(username=username).exists()
