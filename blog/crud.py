from django.db.models import QuerySet
from .models import Post, Comment
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()


def create_post(author: User, title: str, content: str, category: str) -> Post:
    return Post.objects.create(
        author=author,
        title=title,
        content=content,
        category=category,
    )


def get_post(post_id: int) -> Optional[Post]:
    return Post.objects.filter(id=post_id).select_related("author").first()


def get_all_posts(category: Optional[str] = None) -> QuerySet[Post, Post]:
    queryset = Post.objects.all().select_related("author")
    if category:
        queryset = queryset.filter(category=category)
    return queryset


def get_post_by_author(author_id: int) -> Optional[Post]:
    return Post.objects.filter(author=author_id).select_related("author").first()


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
    return post


def delete_post(post: Post) -> None:
    post.delete()


def create_comment(post: Post, user: User, content: str) -> Comment:
    return Comment.objects.create(post=post, author=user, content=content)


def get_comments_for_post(post_id: int):
    return Comment.objects.filter(post=post_id).select_related("author")


def get_comment_by_id(comment_id: int) -> Optional[Comment]:
    return Comment.objects.get(id=comment_id)


def update_comment(content: str, comment: Comment) -> Comment:
    comment.content = content
    comment.save()
    return comment


def delete_comment(comment: Comment) -> None:
    comment.delete()
