import functools
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from database.database import engine
from models import ShoppingList, Fridge
from src.foodify_manager import FoodifyManager
import uvicorn
from fastapi import FastAPI
from schema.products_sch import NewProductSchema
from models.products import Products
from models.brand import *

# First of all load the env values
load_dotenv()

# Create the database if needed
Base.metadata.create_all(bind=engine)

# Instancia del objeto app de Foodify
app = FastAPI(
    title="Foodify_API", description="API para registrar comida", version="0.0.1"
)

# Pasa los parámetros necesarios para que se ejecute el temporizador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

foodify_man = FoodifyManager()


@app.get("/products")
async def read_all_products():
    products = session.query(Products).all()
    return products


# Add schema
@app.post("/add_product")
async def add_product_endpoint(product: NewProductSchema):
    try:
        detected_barcodes = foodify_man.capture_image_and_get_barcodes()
        product_added, info = foodify_man.new_product(
            detected_barcodes=detected_barcodes,
            units=product.units,
            recurrent=product.recurrent,
        )

        return info
    except Exception as ex:
        print(ex)
        return "No encontré producto, enfoca mejor"


@app.get("/spend_product")
async def spend_products():
    try:
        detected_barcodes = foodify_man.capture_image_and_get_barcodes()
        spend_product, info = foodify_man.old_product(detected_barcodes=detected_barcodes)
        brand = session.query(Brands).filter(Brands.id == spend_product.brand_id).first()

        product_data = {
            "ean": spend_product.ean,
            "nombre": spend_product.name,
            "marca": brand.name,
            "nutriscore": spend_product.nutriscore,
            "recurrente": spend_product.recurrent,
            "unidades_paquete": spend_product.unit_packaging,
            "info": info
        }
        return product_data
    except Exception as ex:
        return "No encontré ningún producto, enfoca mejor"


@app.get("/update_shopping_list")
async def update_shopping_list():
    ShoppingList.update_shopping_list()
    return "Se ha actualizado la lista de la compra"


@app.get("/update_all_prices")
async def update_all_prices():
    foodify_man.update_prices(night_update=False)
    return "Se han actualizado todos los precios"


@app.get("/buy_shopping_list")
async def buy_shopping_list():
    buy_list = foodify_man.buy_shopping_list()
    info = {
        "response": "Se han comprado los productos de la lista de la compra",
        "list_bought": buy_list,
    }
    return info


@app.get('/fridge')
async def fridge():
    products_in_fridge = Fridge.sow_products_in_fridge()
    return products_in_fridge


@app.get('/shopping_list')
async def shopping_list():
    products_in_shopping_list = ShoppingList.sow_products_in_shopping_list()
    return products_in_shopping_list


@app.get('/product_added')
async def product_added():
    last_product_added = Products.last_product_added()
    logger.info('Hace el envío')
    return last_product_added


@app.get('/create_buy_links')
async def create_buy_links():
    buy_links = ShoppingList.create_buy_links()
    return buy_links


@app.get('/create_pdf')
async def create_pdf():
    ShoppingList.create_pdf()


@app.on_event("startup")
async def init_data():
    scheduler = BackgroundScheduler()
    # Esta función, sirve para pasarle el parámetro TRUE a update_prices
    update_prices_with_argument = functools.partial(foodify_man.update_prices, True)
    scheduler.add_job(update_prices_with_argument, "interval", hours=1)
    scheduler.start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
