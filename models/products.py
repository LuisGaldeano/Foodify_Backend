import logging

from sqlalchemy.orm import relationship

import setting.logging as log
from database.database import Base, session
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean
import openfoodfacts as offs
# from models.fridge import Fridge
from models.brand import Brands

log.configure_logging()
logger = logging.getLogger(__name__)


class Products(Base):
    __tablename__ = 'products'
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
        brand = Brands.offs_save_brand(product_data)

        product = Products(
            ean=product_data['code'],
            name=product_data['product_name'],
            image=product_data['image_url'],
            nutriscore=product_data['nutriscore_grade'],
            brand_id=brand.id,
            recurrent=recurrent,
            unit_packaging=units
        )

        session.add(product)
        session.commit()
        session.close()

    @classmethod
    def get_or_create_product(cls, barcode: str, recurrent: bool, units: int):
        """
        This method will call offs api and get the data associated to the product
        """
        product_query = session.query(Products).filter_by(ean=barcode).first()
        if product_query:
            product = session.query(Products).filter(Products.ean == barcode).first()
            return product
        else:
            product_data = offs.products.get_product(barcode)['product']
            if not product_data:
                raise Exception("Product data not found in offs")

            product = cls.offs_save_product(product_data=product_data, recurrent=recurrent, units=units)
            logger.info('Successful product registration')
            return product

    @classmethod
    def check_ean_exists(cls, ean: str) -> bool:
        return session.query(Products).filter_by(ean=ean).scalar()

    @classmethod
    def get_product_by_name(cls, name: str):
        product = session.query(Products).filter(Products.name == name).first()
        return product

    @classmethod
    def get_product_by_barcode(cls, ean: int):
        product = session.query(Products).filter(Products.ean == ean).first()
        return product


