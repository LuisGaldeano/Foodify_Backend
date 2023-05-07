from database.database import Base, engine
from models.products import Products
from database.database import session
from models.sup_dia import SupDia


# Creación de la tabla
Base.metadata.create_all(bind=engine)

# Descarga de la api de openfoodfacts el producto
barcode = input()
Products.get_product_and_save(session, barcode)

# descarga los precios del supermercado Día
SupDia.extract_data(session, barcode)
