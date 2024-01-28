from fastapi import APIRouter
from application.models.fridge import Fridge
from application.schemas.fridge import UpdateFridgeProduct

router = APIRouter()


@router.get('/fridge')
async def fridge():
    fridge_products = Fridge.get_fridge_products()
    return fridge_products


@router.post('/update_fridge_product_name')
async def update_fridge_product_name(product_update: UpdateFridgeProduct):
    old_product_data = product_update.old_product_data
    new_product_data = product_update.new_product_data
    update_fridge_product = Fridge.update_fridge_products(
        old_product_data=old_product_data,
        new_product_data=new_product_data)
    return update_fridge_product
