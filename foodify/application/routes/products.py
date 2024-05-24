from fastapi import APIRouter

from application.database.database import db_dependency
from application.manager import manager
from application.models import Brands
from application.models.products import Products
from application.schemas.products_sch import NewProductSchema
from core.logging import logger

router = APIRouter()


@router.get("/products")
async def read_all_products(db: db_dependency):
    products = db.query(Products).all()
    return products


@router.post("/add_product")
async def add_product_endpoint(db: db_dependency, product: NewProductSchema):
    try:
        detected_barcodes = manager.capture_image_and_get_barcodes()
        product_added, info = manager.new_product(
            detected_barcodes=detected_barcodes,
            units=product.units,
            recurrent=product.recurrent,
            db=db,
        )

        return info
    except Exception as ex:
        print(ex)
        return "No encontré producto, enfoca mejor"


@router.get("/spend_product")
async def spend_products(db: db_dependency):
    try:
        detected_barcodes = manager.capture_image_and_get_barcodes()
        spend_product, info = manager.old_product(
            detected_barcodes=detected_barcodes, db=db
        )
        brand = db.query(Brands).filter(Brands.id == spend_product.brand_id).first()

        product_data = {
            "ean": spend_product.ean,
            "nombre": spend_product.name,
            "marca": brand.name,
            "nutriscore": spend_product.nutriscore,
            "recurrente": spend_product.recurrent,
            "unidades_paquete": spend_product.unit_packaging,
            "info": info,
        }
        return product_data
    except Exception as ex:
        logger.exception(f"Exception {ex}")
        return "No encontré ningún producto, enfoca mejor"


@router.get("/product_added")
async def product_added(db: db_dependency):
    last_product_added = Products.last_product_added(db=db)
    logger.info("Hace el envío")
    return last_product_added
