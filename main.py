from database.database import Base, engine
from models.products import Products
from database.database import session
from models.sup_dia import SupDia
from models.sup_carr import SupCarr
from models.sup_alca import SupAlca
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.sql.expression import func

# Creación de la tabla
Base.metadata.create_all(bind=engine)

# Descarga de la api de openfoodfacts el producto
barcode = input()
check = Products.check_ean_exists(session, barcode)

'''
1. Esta parte métela todo en funciones para que sea más facil de leer el código
2. Tambièn hay que revisar por que no añade en la columna shop el string que le mando con los nombres de cada super
'''


if not check:
    print('Hago el registro')
    Products.get_product_and_save(session, barcode)

    # Añado a shop
    SupDia.supdia_extract_price(session, barcode)

    SupCarr.supcarr_extract_price(session, barcode)

    SupAlca.supalca_extract_price(session, barcode)

else:
    print('Ya está registrado')


shop = session.query(Products.shop).filter(Products.ean == barcode).first()
shop = shop[0].split(',')
if any('dia' in s.lower() for s in shop):
    # descarga los precios del supermercado Día
    try:
        print('Registrado en Día')
        SupDia.extract_data(session, barcode)
    except Exception as e:
        print('No lo registro en Día')
        print(e)
if any('carre' in s.lower() for s in shop):
    try:
        # Descarga los precios del supermercado Carrefour
        print('Registrado en Carrefour')
        SupCarr.extract_data(session, barcode)
    except Exception as e:
        print('No lo registro en Carrefour')
        print(e)
if any('alca' in s.lower() or 'auchan' in s.lower() for s in shop):
    try:
        # Descarga los precios del supermercado Carrefour
        print('Registrado en Alcampo')
        SupAlca.extract_data(session, barcode)
    except Exception as e:
        print('No lo registro en Alcampo')
        print(e)
