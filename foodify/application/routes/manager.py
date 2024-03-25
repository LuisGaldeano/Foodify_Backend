from fastapi import APIRouter

from application.database.database import db_dependency
from application.manager import FoodifyManager
from application.models.shopping_list import ShoppingList

router = APIRouter()


@router.get("/update_all_prices")
async def update_all_prices(db: db_dependency):
    FoodifyManager().update_prices(night_update=False, db=db)
    return "Se han actualizado todos los precios"


@router.get("/create_buy_links")
async def create_buy_links(db: db_dependency):
    buy_links = ShoppingList.create_buy_links(db=db)
    return buy_links


@router.get("/create_pdf")
async def create_pdf(db: db_dependency):
    ShoppingList.create_pdf(db=db)
