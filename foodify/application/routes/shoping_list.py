from fastapi import APIRouter

from application.database.database import db_dependency
from application.manager import manager
from application.models.shopping_list import ShoppingList

router = APIRouter()


@router.get("/shopping_list")
async def shopping_list(db: db_dependency):
    products_in_shopping_list = ShoppingList.sow_products_in_shopping_list(db=db)
    return products_in_shopping_list


@router.get("/update_shopping_list")
async def update_shopping_list(db: db_dependency):
    ShoppingList.update_shopping_list(db=db)
    return "Se ha actualizado la lista de la compra"


@router.get("/buy_shopping_list")
async def buy_shopping_list(db: db_dependency):
    buy_list = manager.buy_shopping_list(db=db)
    info = {
        "response": "Se han comprado los productos de la lista de la compra",
        "list_bought": buy_list,
    }
    return info
