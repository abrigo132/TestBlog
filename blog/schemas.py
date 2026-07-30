from datetime import datetime
from ninja import Schema
from typing import Optional


class PostCreate(Schema):
    title: str
    content: str
    category: str = "Traditional"


class PostUpdate(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class PostResponse(Schema):
    id: int
    title: str
    content: str
    category: str
    author_id: int
    created_at: datetime
    author_name: str

    @staticmethod
    def resolve_author_name(obj):
        return obj.author.username


class PostListSchema(Schema):
    """Упрощенная схема для списка, чтобы не гонять лишний текст content"""

    id: int
    title: str
    category: str
    created_at: datetime
    author_username: str

    @staticmethod
    def resolve_author_username(obj):
        return obj.author.username
