from fastapi import APIRouter

from application.auth import oauth_routes
from application.routes import fridge, manager, products, shoping_list, users

router = APIRouter()
router.include_router(oauth_routes.router, tags=["Oauth2"], prefix="/oauth2")
router.include_router(users.router, tags=["users"], prefix="/users")
router.include_router(fridge.router, tags=["fridge"], prefix="/fridge")
router.include_router(manager.router, tags=["update_all_prices"], prefix="/manager")
router.include_router(products.router, tags=["products"], prefix="/products")
router.include_router(
    shoping_list.router, tags=["shopping_list"], prefix="/shopping_list"
)
