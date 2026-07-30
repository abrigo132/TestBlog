from ninja import Schema


class UserRegisterSchema(Schema):
    username: str
    password: str
    bio: str
    email: str


class UserResponseSchema(Schema):
    id: int
    username: str
