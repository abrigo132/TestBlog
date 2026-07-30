import json
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


def get_json(response):
    return json.loads(response.content)


@pytest.mark.django_db
def test_register_user_success(api_client):
    url = "/api/users/register"
    data = {
        "username": "newuser",
        "password": "securepassword123",
        "email": "newuser@example.com",
        "bio": "Новый пользователь",
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 201
    assert User.objects.count() == 1

    user = User.objects.first()
    assert user.username == "newuser"
    assert user.check_password("securepassword123")

    res_data = get_json(response)
    assert res_data["username"] == "newuser"


@pytest.mark.django_db
def test_register_user_duplicate_username(api_client, user):
    url = "/api/users/register"
    data = {"username": "testuser", "password": "anotherpassword"}

    response = api_client.post(url, data, format="json")

    assert response.status_code in [400, 422]
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_register_user_missing_fields(api_client):
    url = "/api/users/register"
    data = {"username": "incomplete"}

    response = api_client.post(url, data, format="json")

    assert response.status_code == 422


@pytest.mark.django_db
def test_obtain_jwt_token(api_client, user):
    url = "/api/users/jwt/pair"
    data = {"username": "testuser", "password": "testpassword123"}

    response = api_client.post(url, data, format="json")

    assert response.status_code == 200
    res_data = get_json(response)
    assert "access" in res_data
    assert "refresh" in res_data
    assert len(res_data["access"]) > 0


@pytest.mark.django_db
def test_obtain_jwt_token_wrong_password(api_client, user):
    url = "/api/users/jwt/pair"
    data = {"username": "testuser", "password": "wrongpassword"}

    response = api_client.post(url, data, format="json")

    assert response.status_code in [401, 400]


@pytest.mark.django_db
def test_obtain_jwt_token_nonexistent_user(api_client):
    url = "/api/users/jwt/pair"
    data = {"username": "ghost", "password": "anypassword"}

    response = api_client.post(url, data, format="json")

    assert response.status_code in [401, 400]


@pytest.mark.django_db
def test_refresh_jwt_token(api_client, user):
    # Получаем токены
    obtain_response = api_client.post(
        "/api/users/jwt/pair",
        {"username": "testuser", "password": "testpassword123"},
        format="json",
    )
    refresh_token = get_json(obtain_response)["refresh"]

    # Обновляем
    response = api_client.post(
        "/api/users/jwt/refresh", {"refresh": refresh_token}, format="json"
    )

    assert response.status_code == 200
    assert "access" in get_json(response)


@pytest.mark.django_db
def test_verify_jwt_token(api_client, user):
    obtain_response = api_client.post(
        "/api/users/jwt/pair",
        {"username": "testuser", "password": "testpassword123"},
        format="json",
    )
    access_token = get_json(obtain_response)["access"]

    response = api_client.post(
        "/api/users/jwt/verify", {"token": access_token}, format="json"
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_verify_invalid_jwt_token(api_client):
    response = api_client.post(
        "/api/users/jwt/verify", {"token": "invalid.token.here"}, format="json"
    )
    assert response.status_code in [400, 401]
