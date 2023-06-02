import logging
from sqlalchemy.orm import relationship
import setting.logging as log
from database.database import Base, session
from sqlalchemy import Column, Integer, String

log.configure_logging()
logger = logging.getLogger(__name__)


class Brands(Base):
    __tablename__ = 'brand'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)

    products = relationship("Products", back_populates="brands")

    def __str__(self):
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def offs_save_brand(cls, product_data: dict):
        """
        Dado un producto, revisa si la marca está ya guardada en BD
            Si la marca está guardada devuelve el objeto de la marca
            Si no está guardada, guarda el nombre de la marca en base de datos y devuelve el objeto de la marca
        :param product_data: Producto
        :return: Objeto marca del producto
        """
        existing_brand = cls.select_brand(product_data['brands'].upper().strip())
        if not existing_brand:
            brand = Brands(
                name=product_data['brands'].upper().strip())

            session.add(brand)
            session.commit()

            logger.info(brand)

            return brand
        elif existing_brand:
            return existing_brand

    @classmethod
    def select_brand(cls, brand: str):
        """
        Dado un id de una marca, hace una query para obtener el nombre de la marca y la devuelve
        :param brand: Nombre de una marca
        :return: Objeto de la marca
        """
        brand = session.query(Brands).filter(Brands.name == brand).first()

        logger.info(brand)

        return brand
