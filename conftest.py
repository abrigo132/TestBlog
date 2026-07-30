import json
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from blog.models import Post, Comment

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpassword123")


@pytest.fixture
def user2():
    return User.objects.create_user(username="testuser2", password="testpassword456")


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Правильная аутентификация для Django Ninja:
    получаем реальный JWT токен и устанавливаем его в заголовки клиента.
    """
    # 1. Получаем токен
    response = api_client.post(
        "/api/users/jwt/pair",
        {"username": user.username, "password": "testpassword123"},
        format="json",
    )

    # 2. Парсим JSON из стандартного HttpResponse
    data = json.loads(response.content)
    token = data["access"]

    # 3. Устанавливаем заголовок для всех последующих запросов этого клиента
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def authenticated_client2(api_client, user2):
    """Аутентифицированный клиент для второго пользователя"""
    response = api_client.post(
        "/api/users/jwt/pair",
        {"username": user2.username, "password": "testpassword456"},
        format="json",
    )
    data = json.loads(response.content)
    token = data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def post(user):
    # ИСПРАВЛЕНО: используем объект user, а не жесткий author_id=1
    return Post.objects.create(
        author=user,
        title="Тестовый пост",
        content="Содержимое тестов-posta",
        category="traditional",
    )


@pytest.fixture
def comment(user, post):
    return Comment.objects.create(
        post=post, author=user, content="Тестовый комментарий"
    )


@pytest.fixture
def comment_by_user2(user2, post):
    return Comment.objects.create(
        post=post, author=user2, content="Комментарий от второго пользователя"
    )
