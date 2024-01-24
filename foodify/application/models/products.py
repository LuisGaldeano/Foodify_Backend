import logging
from sqlalchemy.orm import relationship
from core.logging import logger
from application.database.database import Base, session
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean
import openfoodfacts as offs
from application.models.brand import Brands


class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ean = Column(BigInteger, index=True)
    name = Column(String(255), index=True)
    image = Column(String(10000))
    nutriscore = Column(String)
    recurrent = Column(Boolean)
    unit_packaging = Column(Integer)

    brand_id = Column(Integer, ForeignKey("brand.id"))
    brands = relationship("Brands", back_populates="products")

    fridge = relationship("Fridge", back_populates="products")

    shoppinglists = relationship("ShoppingList", back_populates="products")

    productsuprel = relationship("ProductSuperRelationship", back_populates="products")

    def __str__(self):
        return f"id= {self.id} - name= {self.name} - ean= {self.ean}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def offs_save_product(cls, product_data: dict, recurrent: bool, units: int):
        """
        Guarda un nuevo producto en la base de datos utilizando los datos proporcionados.

        :param product_data: Un diccionario con los datos del producto, incluyendo el código, nombre, URL de imagen y nutriscore.
        :param recurrent: Indica si el producto es recurrente (True) o no recurrente (False).
        :param units: El número de unidades por paquete del producto.
        :return: El objeto del producto guardado en la base de datos.
        """

        brand = Brands.offs_save_brand(product_data)

        product = Products(
            ean=product_data["code"],
            name=product_data["product_name"],
            image=product_data["image_url"],
            nutriscore=product_data["nutriscore_grade"],
            brand_id=brand.id,
            recurrent=recurrent,
            unit_packaging=units,
        )

        session.add(product)
        session.commit()
        return product

    @classmethod
    def get_or_create_product(cls, barcode: str, recurrent: bool, units: int):
        """
        Obtiene un producto de la base de datos según el código de barras o crea un nuevo producto si no existe.

        :param barcode: El EAN del producto.
        :param recurrent: Indica si el producto es recurrente (True) o no recurrente (False).
        :param units: El número de unidades por paquete del producto.
        :return: El objeto del producto obtenido de la base de datos o el nuevo producto creado.
        :raises Exception: Si no se encuentra la información del producto en la fuente de datos externa.
        """

        product_query = session.query(Products).filter_by(ean=barcode).first()
        if product_query:
            product = session.query(Products).filter(Products.ean == barcode).first()
            logger.info("Product found")

            return product
        else:
            product_data = offs.products.get_product(barcode)["product"]

            if not product_data:
                raise Exception("Product data not found in offs")

            product = cls.offs_save_product(
                product_data=product_data, recurrent=recurrent, units=units
            )
            logger.info("Successful product registration")

            return product

    @classmethod
    def last_product_added(cls):
        """
            Obtiene los detalles del último producto agregado a través de su identificador.

            :return: Un diccionario con los siguientes detalles del producto:
                     - "ean": El código EAN del producto.
                     - "nombre": El nombre del producto.
                     - "marca": El nombre de la marca del producto.
                     - "nutriscore": El nutriscore del producto.
                     - "recurrente": Indicador booleano que muestra si el producto es recurrente.
                     - "unidades_paquete": El número de unidades en el empaque del producto.
            """
        product = session.query(Products).order_by((Products.id.desc())).first()
        brand = session.query(Brands).filter(Brands.id == product.brand_id).first()
        product_data = {
            "ean": product.ean,
            "nombre": product.name,
            "marca": brand.name,
            "nutriscore": product.nutriscore,
            "recurrente": product.recurrent,
            "unidades_paquete": product.unit_packaging
        }
        return product_data
