from ninja_extra import api_controller
from ninja_jwt.controller import NinjaJWTDefaultController


@api_controller("users/jwt", tags=["Authenticated"])
class CustomJwtController(NinjaJWTDefaultController):
    pass
