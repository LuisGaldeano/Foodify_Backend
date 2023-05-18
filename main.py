from starlette.responses import StreamingResponse
from database.database import Base, engine, get_db, session
from src import foodify_manager
from src.foodify_manager import FoodifyManager
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from schema.products_sch import ProductsBase
from models.products import Products
from models.super import Supermercado


'''
**Tareas por hacer**

1. HECHO - Revisar por que no añade en la columna shop el string que le mando con los nombres de cada super
2. HECHO - https://www.youtube.com/watch?v=pAnBDKl7uuo  -->  Vídeo de como pimplementar la lectura por cámara
3. Revisar la librería streamlit para crear el front!
4. Añadir las tablas de fridge y shopping_list para gestionar esa parate de la aplicación

'''



# Instancia del objeto app de Foodify
app = FastAPI(title='Foodify_API', description='API para registrar comida', version='0.0.1')

# Instancia el objeto foodify_man de Foodify_manager
foodify_man = FoodifyManager()

# Creación de la tabla
Base.metadata.create_all(bind=engine)


@app.get('/products')
async def read_all_products():
    products = session.query(Products).all()
    return products


@app.get('/prices')
# NO CONSIGO QUE ME DEVUELVA LOS PRECIOS; ES POR ALGO DE AVAILABLE_SUPERS, REVISAR
async def read_all_prices():
    products = session.query(Supermercado).all()
    return products


@app.get('/products/{barcode}', response_model=ProductsBase)
async def read_product_by_barcode(ean: int):
    db_product = Products.get_product_by_barcode(ean=ean)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.get('/finished_product', response_model=ProductsBase)
async def finished_product_by_barcode():
    return StreamingResponse(foodify_man.capture_image(new_product=False), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
