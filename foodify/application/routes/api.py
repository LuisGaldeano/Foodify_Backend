from fastapi import APIRouter
from application.routes import fridge, shoping_list, products, manager

router = APIRouter()
router.include_router(fridge.router, tags=["fridge"], prefix="/fridge")
router.include_router(manager.router, tags=["update_all_prices"], prefix="/manager")
router.include_router(products.router, tags=["products"], prefix="/products")
router.include_router(shoping_list.router, tags=["shopping_list"], prefix="/shopping_list")
