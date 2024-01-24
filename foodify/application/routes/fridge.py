from fastapi import APIRouter
from application.models.fridge import Fridge

router = APIRouter()


@router.get('/fridge')
async def fridge():
    products_in_fridge = Fridge.sow_products_in_fridge()
    return products_in_fridge
