from dotenv import load_dotenv
from database.database import Base, engine, get_db, session
from src.foodify_manager import FoodifyManager
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from schema.products_sch import ProductsBase
from models.products import Products
from models.super import Supermarket

# First of all load the env values
load_dotenv()

# Create the database if needed
Base.metadata.create_all(bind=engine)

# Instancia del objeto app de Foodify
app = FastAPI(title='Foodify_API', description='API para registrar comida', version='0.0.1')

foodify_man = FoodifyManager()


@app.get('/products')
async def read_all_products():
    products = session.query(Products).all()
    return products


# Add schema
@app.post('/add_product')
async def add_product_endpoint(product: NewProductSchema):
    try:
        detected_barcodes = foodify_man.capture_image_and_get_barcodes()
        foodify_man.new_product(detected_barcodes=detected_barcodes, units=product.units, recurrent=product.recurrent)
        return "producto encontrado"
    except Exception as ex:
        print(ex)
        return "No encontré producto, enfoca mejor"

@app.get('/spend_product')
async def spend_products():
    try:
        detected_barcodes = foodify_man.capture_image_and_get_barcodes()
        foodify_man.old_product(detected_barcodes=detected_barcodes)
        return "producto encontrado"
    except Exception as ex:
        return "No encontré producto, enfoca mejor"


@app.get('/buy_shopping_list')
async def buy_shopping_list():
    products = session.query(Supermarket).all()
    return products


@app.get('/products/{barcode}', response_model=ProductsBase)
async def read_product_by_barcode(ean: int):
    db_product = Products.get_product_by_barcode(ean=ean)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
