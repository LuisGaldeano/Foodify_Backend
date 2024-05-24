from fastapi import APIRouter

from application.database.database import db_dependency
from application.models.fridge import Fridge
from application.schemas.fridge import UpdateFridgeProduct

router = APIRouter()


@router.get("/fridge")
async def fridge(db: db_dependency):
    fridge_products = Fridge.get_fridge_products(db=db)
    return fridge_products


@router.post("/update_fridge_product_name")
async def update_fridge_product_name(
    db: db_dependency, product_update: UpdateFridgeProduct
):
    old_product_data = product_update.old_product_data
    new_product_data = product_update.new_product_data
    update_fridge_product = Fridge.update_fridge_products(
        old_product_data=old_product_data, new_product_data=new_product_data, db=db
    )

    return update_fridge_product
