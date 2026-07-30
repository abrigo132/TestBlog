from ninja_extra import NinjaExtraAPI

from users.controllers import CustomJwtController
from users.routers import router as user_router
from blog.routers import router as blog_router

api = NinjaExtraAPI(
    title="Test Blog",
    version="1.0.0",
    urls_namespace="api/",
)

api.register_controllers(CustomJwtController)
api.add_router("users/", user_router)
api.add_router("posts/", blog_router)
