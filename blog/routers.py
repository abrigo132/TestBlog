from ninja import Router
from ninja_jwt.authentication import JWTAuth
from typing import Optional, List


from .schemas import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListSchema,
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from . import crud

router = Router(tags=["Posts"])


@router.post("", response={201: PostResponse, 401: dict}, auth=JWTAuth())
def create_post(request, post: PostCreate):
    post = crud.create_post(
        author=request.auth,
        title=post.title,
        content=post.content,
        category=post.category,
    )

    return 201, post


@router.get("", response=List[PostListSchema])
def get_all_posts(request, category: Optional[str] = None):
    posts = crud.get_all_posts(category=category)
    return posts


@router.get("/{post_id}", response={200: PostResponse, 404: dict})
def get_post_by_id(request, post_id: int):
    post = crud.get_post(post_id)
    if post is None:
        return 404, {"detail": "Пост не найден"}
    return 200, post


@router.put(
    "/{post_id}", response={201: PostResponse, 404: dict, 403: dict}, auth=JWTAuth()
)
def update_post(request, post_id: int, payload: PostUpdate):
    post = crud.get_post(post_id=post_id)
    if post is None:
        return 404, {"detail": "Пост не найден"}

    if post.author != request.auth:
        return 403, {"detail": "Вы не можете редактировать чужой пост"}

    updated_post = crud.update_post(
        post=post,
        title=payload.title,
        content=payload.content,
        category=payload.category,
    )

    return 201, updated_post


@router.delete("/{post_id}", response={201: None, 404: dict, 403: dict}, auth=JWTAuth())
def delete_post(request, post_id: int):
    post = crud.get_post(post_id=post_id)
    if post is None:
        return 404, {"detail": "Пост не найден"}

    if post.author != request.auth:
        return 403, {"detail": "Вы не можете удалить чужой пост"}

    crud.delete_post(post)

    return 201, None


@router.get("/{post_id}/comments", response=List[CommentResponse])
def list_comments(request, post_id: int):
    if not crud.get_post(post_id=post_id):
        return 404, {"detail": "Пост не найден"}

    comments = crud.get_comments_for_post(post_id=post_id)
    return comments


@router.post(
    "/{post_id}/comments",
    response={201: CommentResponse, 404: dict},
    auth=JWTAuth(),
)
def create_comment_for_post(request, post_id: int, payload: CommentCreate):
    post = crud.get_post(post_id=post_id)
    if post is None:
        return 404, {"detail": "Пост не найден"}

    comment = crud.create_comment(
        post=post,
        content=payload.content,
        user=request.auth,
    )
    return 201, comment


@router.put(
    "/{post_id}/comments/{comment_id}",
    response={200: CommentResponse, 404: dict, 403: dict},
    auth=JWTAuth(),
)
def update_comment_for_post(
    request,
    post_id: int,
    comment_id: int,
    comment_payload: CommentUpdate,
):
    post = crud.get_post(post_id=post_id)

    if post is None:
        return 404, {"detail": "Пост не найден"}

    comment = crud.get_comment_by_id(comment_id=comment_id)

    if comment is None:
        return 404, {"detail": "Комментарий не найден"}

    if comment.post_id != post_id:
        return 404, {"detail": "Комментарий не найден в этом посте"}

    if comment.author != request.auth:
        return 403, {"detail": "Вы не можете изменять чужой комментарий"}

    updated_comment = crud.update_comment(
        comment=comment, content=comment_payload.content
    )

    return 200, updated_comment


@router.delete(
    "/{post_id}/comments/{comment_id}",
    response={204: None, 404: dict, 403: dict},
    auth=JWTAuth(),
)
def delete_comment_for_post(
    request,
    post_id: int,
    comment_id: int,
):
    comment = crud.get_comment_by_id(comment_id=comment_id)

    if comment is None:
        return 404, {"detail": "Комментарий не найден"}

    if comment.post_id != post_id:
        return 404, {"detail": "Комментарий не найден в этом посте"}

    if comment.author != request.auth:
        return 403, {"detail": "Вы не можете удалять чужой комментарий"}

    crud.delete_comment(comment=comment)

    return 204, None
