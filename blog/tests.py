import json
import pytest
from blog.models import Post, Comment


def get_json(response):
    """Хелпер для парсинга JSON из HttpResponse Django Ninja"""
    return json.loads(response.content)


@pytest.mark.django_db
def test_create_post_success(authenticated_client, user):
    url = "/api/posts/"  # Без слеша в конце
    data = {
        "title": "Новый пост",
        "content": "Текст нового поста",
        "category": "crypto",
    }

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == 201
    assert Post.objects.count() == 1
    assert Post.objects.first().author == user
    assert get_json(response)["title"] == "Новый пост"


@pytest.mark.django_db
def test_create_post_unauthorized(api_client):
    url = "/api/posts/"
    data = {"title": "Новый пост", "content": "Текст", "category": "crypto"}

    response = api_client.post(url, data, format="json")

    assert response.status_code in [401, 403]
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_get_all_posts(api_client, user):
    Post.objects.create(
        title="Пост 1", content="Текст 1", category="traditional", author=user
    )
    Post.objects.create(
        title="Пост 2", content="Текст 2", category="crypto", author=user
    )

    url = "/api/posts/"
    response = api_client.get(url, format="json")
    response_with_category = api_client.get(f"{url}?category=crypto", format="json")

    assert response.status_code == 200
    assert response_with_category.status_code == 200

    res_data = get_json(response)
    res_data_cat = get_json(response_with_category)

    assert isinstance(res_data, list)
    assert len(res_data) == 2
    assert len(res_data_cat) == 1


@pytest.mark.django_db
def test_get_all_posts_with_unknown_category(api_client):
    url = "/api/posts/"
    response = api_client.get(f"{url}?category=finance", format="json")

    assert response.status_code == 200
    assert len(get_json(response)) == 0


@pytest.mark.django_db
def test_get_post_by_id(api_client, post):
    url = f"/api/posts/{post.id}"
    response = api_client.get(url, format="json")

    assert response.status_code == 200
    assert get_json(response)["title"] == post.title


@pytest.mark.django_db
def test_get_post_by_id_unknown(api_client):
    url = "/api/posts/999"
    response = api_client.get(url, format="json")

    assert response.status_code == 404
    assert get_json(response)["detail"] == "Пост не найден"


@pytest.mark.django_db
def test_update_post(authenticated_client, post):
    url = f"/api/posts/{post.id}"
    data = {
        "title": "Обновленный заголовок",
        "content": post.content,
        "category": post.category,
    }

    response = authenticated_client.put(url, data, format="json")

    assert response.status_code == 200
    assert get_json(response)["title"] == "Обновленный заголовок"

    post.refresh_from_db()
    assert post.title == "Обновленный заголовок"


@pytest.mark.django_db
def test_update_post_unauthorized(api_client, post):
    url = f"/api/posts/{post.id}"
    data = {"title": "Попытка взлома"}

    response = api_client.put(url, data, format="json")

    assert response.status_code in [401, 403]
    post.refresh_from_db()
    assert post.title != "Попытка взлома"


@pytest.mark.django_db
def test_delete_post(authenticated_client, post):
    url = f"/api/posts/{post.id}"
    response = authenticated_client.delete(url, format="json")

    assert response.status_code == 204
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_delete_post_unauthorized(api_client, post):
    url = f"/api/posts/{post.id}"
    response = api_client.delete(url, format="json")

    assert response.status_code in [401, 403]
    assert Post.objects.count() == 1


@pytest.mark.django_db
def test_delete_post_with_unknown_id(authenticated_client):
    url = "/api/posts/999"
    response = authenticated_client.delete(url, format="json")

    assert response.status_code == 404
    assert get_json(response)["detail"] == "Пост не найден"


@pytest.mark.django_db
def test_create_comment_success(authenticated_client, post):
    url = f"/api/posts/{post.id}/comments"
    data = {"content": "Новый комментарий"}

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == 201
    assert Comment.objects.count() == 1
    assert get_json(response)["content"] == "Новый комментарий"


@pytest.mark.django_db
def test_create_comment_unauthorized(api_client, post):
    url = f"/api/posts/{post.id}/comments"
    data = {"content": "Попытка без токена"}

    response = api_client.post(url, data, format="json")

    assert response.status_code in [401, 403]
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_create_comment_to_nonexistent_post(authenticated_client):
    url = "/api/posts/999/comments"
    data = {"content": "Комментарий к несуществующему посту"}

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == 404
    # Исправлено: текст ошибки должен совпадать с тем, что в роутере
    assert get_json(response)["detail"] == "Пост не найден"


@pytest.mark.django_db
def test_get_comments_list(api_client, post, comment, comment_by_user2):
    url = f"/api/posts/{post.id}/comments"
    response = api_client.get(url, format="json")

    assert response.status_code == 200
    res_data = get_json(response)
    assert len(res_data) == 2

    # Исправлено: проверяем наличие контента в списке, а не строгий индекс,
    # так как порядок сортировки в тестовой БД может варьироваться
    contents = [item["content"] for item in res_data]
    assert "Тестовый комментарий" in contents
    assert "Комментарий от второго пользователя" in contents


@pytest.mark.django_db
def test_get_comments_empty_list(api_client, post):
    url = f"/api/posts/{post.id}/comments"
    response = api_client.get(url, format="json")

    assert response.status_code == 200
    assert len(get_json(response)) == 0


@pytest.mark.django_db
def test_update_own_comment(authenticated_client, post, comment):
    url = f"/api/posts/{post.id}/comments/{comment.id}"
    data = {"content": "Обновленный комментарий"}

    response = authenticated_client.put(url, data, format="json")

    assert response.status_code == 200
    assert get_json(response)["content"] == "Обновленный комментарий"

    comment.refresh_from_db()
    assert comment.content == "Обновленный комментарий"


@pytest.mark.django_db
def test_update_other_users_comment(authenticated_client, post, comment_by_user2):
    url = f"/api/posts/{post.id}/comments/{comment_by_user2.id}"
    data = {"content": "Попытка взлома"}

    response = authenticated_client.put(url, data, format="json")

    assert response.status_code == 403
    assert get_json(response)["detail"] == "Вы не можете изменять чужой комментарий"


@pytest.mark.django_db
def test_update_comment_unauthorized(api_client, post, comment):
    url = f"/api/posts/{post.id}/comments/{comment.id}"
    data = {"content": "Без токена"}

    response = api_client.put(url, data, format="json")

    assert response.status_code in [401, 403]


@pytest.mark.django_db
def test_delete_own_comment(authenticated_client, post, comment):
    url = f"/api/posts/{post.id}/comments/{comment.id}"
    response = authenticated_client.delete(url, format="json")

    assert response.status_code == 204
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_delete_other_users_comment(authenticated_client, post, comment_by_user2):
    url = f"/api/posts/{post.id}/comments/{comment_by_user2.id}"
    response = authenticated_client.delete(url, format="json")

    assert response.status_code == 403
    assert get_json(response)["detail"] == "Вы не можете удалять чужой комментарий"
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_delete_comment_unauthorized(api_client, post, comment):
    url = f"/api/posts/{post.id}/comments/{comment.id}"
    response = api_client.delete(url, format="json")

    assert response.status_code in [401, 403]
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_delete_nonexistent_comment(authenticated_client, post):
    url = f"/api/posts/{post.id}/comments/999"
    response = authenticated_client.delete(url, format="json")

    assert response.status_code == 404
    assert get_json(response)["detail"] == "Комментарий не найден"
