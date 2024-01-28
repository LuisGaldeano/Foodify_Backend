from fastapi import APIRouter
from application.manager import manager
from application.models.shopping_list import ShoppingList

router = APIRouter()


@router.get("/update_all_prices")
async def update_all_prices():
    manager.update_prices(night_update=False)
    return "Se han actualizado todos los precios"


@router.get('/create_buy_links')
async def create_buy_links():
    buy_links = ShoppingList.create_buy_links()
    return buy_links


@router.get('/create_pdf')
async def create_pdf():
    ShoppingList.create_pdf()
