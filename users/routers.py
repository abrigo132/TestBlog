from ninja import Router
from . import crud
from .schemas import UserRegisterSchema, UserResponseSchema

router = Router(tags=["Auth and Users"])


@router.post("/register", response={201: UserResponseSchema, 401: dict})
def register_user(request, user_payload: UserRegisterSchema):
    if crud.user_exists(user_payload.username):
        return 400, {"detail": "Пользователь с таким логином уже существует"}

    user = crud.create_user(
        username=user_payload.username,
        password=user_payload.password,
        email=user_payload.email,
        bio=user_payload.bio,
    )

    return 201, user
