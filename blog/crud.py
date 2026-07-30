from django.db.models import QuerySet
from .models import Post, Comment
from django.contrib.auth import get_user_model
from typing import Optional
import logging

User = get_user_model()
logger = logging.getLogger("blog")


def create_post(author: User, title: str, content: str, category: str) -> Post:
    post = Post.objects.create(
        author=author,
        title=title,
        content=content,
        category=category,
    )
    logger.info(
        f"Пост '{title}' успешно создан пользователем {author.username} (ID: {post.id})"
    )
    return post


def get_post(post_id: int) -> Optional[Post]:
    logger.info(f"Запрос поста {post_id}")
    return Post.objects.filter(id=post_id).select_related("author").first()


def get_all_posts(category: Optional[str] = None) -> QuerySet[Post, Post]:
    queryset = Post.objects.all().select_related("author")
    if category:
        queryset = queryset.filter(category=category)
        logger.info(f"Запрос всех постов с категорией: {category}")
    logger.info("Запрос всех постов без категории")
    return queryset


def get_post_by_author(author_id: int) -> Optional[Post]:
    post = Post.objects.filter(author=author_id).select_related("author").first()
    logger.info(f"Запрос всех постов пользователя: {author_id}")
    return post


def update_post(
    post: Post,
    title: Optional[str] = None,
    content: Optional[str] = None,
    category: Optional[str] = None,
) -> Post:
    if title:
        post.title = title
    if content:
        post.content = content
    if category:
        post.category = category
    post.save()
    logger.info(f"Пост {post.id} изменён")
    return post


def delete_post(post: Post) -> None:
    post.delete()
    logger.info(f"Пост {post.id} удалён")


def create_comment(post: Post, user: User, content: str) -> Comment:
    comment = Comment.objects.create(post=post, author=user, content=content)
    logger.info(
        f"Комментарий к посту {post.id} создан пользователем {user.username} (ID: {comment.id})"
    )
    return comment


def get_comments_for_post(post_id: int) -> QuerySet[Comment]:
    comments = Comment.objects.filter(post=post_id).select_related("author")
    logger.info(f"Запрос всех комментариев к посту: {post_id}")
    return comments


def get_comment_by_id(comment_id: int) -> Optional[Comment]:
    comment = (
        Comment.objects.filter(id=comment_id).select_related("author", "post").first()
    )
    if comment:
        logger.info(f"Запрос комментария {comment_id} к посту {comment.post.id}")
    else:
        logger.info(f"Запрос несуществующего комментария {comment_id}")

    return comment


def update_comment(content: str, comment: Comment) -> Comment:
    comment.content = content
    comment.save()
    logger.info(f"Комментарий с id {comment.id} обновлён")
    return comment


def delete_comment(comment: Comment) -> None:
    comment.delete()
    logger.info(f"Комментарий с id {comment.id} удалён")
