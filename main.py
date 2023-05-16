from database.database import Base, engine, get_db
from src.barcodes import iniciar_foodify
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from schema.products_sch import ProductsBase
from sqlalchemy.orm import Session
from models.products import Products
from models.super import Supermercado


# Instancia del objeto app de Foodify
app = FastAPI(title='Foodify_API', description='API para registrar comida', version='0.0.1')

# Creación de la tabla
Base.metadata.create_all(bind=engine)


@app.get('/products')
async def read_all_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    return products

@app.get('/prices')
async def read_all_prices(db: Session = Depends(get_db)):
    products = db.query(Supermercado).all()
    return products


@app.get('/products/{barcode}', response_model=ProductsBase)
async def read_product_by_barcode(ean: int, db: Session = Depends(get_db)):
    db_product = Products.get_product_by_barcode(db=db, ean=ean)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product



# iniciar_foodify()





'''
**Tareas por hacer**

1. Revisar por que no añade en la columna shop el string que le mando con los nombres de cada super
2. HECHO - https://www.youtube.com/watch?v=pAnBDKl7uuo  -->  Vídeo de como pimplementar la lectura por cámara
3. Revisar la librería streamlit para crear el front!

'''

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)