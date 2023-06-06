import logging
from datetime import datetime
from database.database import Base, session
from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Date
from sqlalchemy.orm import relationship
import setting.logging as log
from models.products import Products

log.configure_logging()
logger = logging.getLogger(__name__)


class Fridge(Base):
    __tablename__ = 'fridge'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_in = Column(Date, default=datetime.utcnow)
    date_out = Column(Date)
    unit_actual = Column(Integer)

    product_id = Column(BigInteger, ForeignKey("products.id"))
    products = relationship("Products", back_populates="fridge")

    def __str__(self):
        return f"id= {self.id}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def fridge_save_product(cls, product_added):
        """
        Calcula las unidades que hay en la nevera de un producto,
        le suma las unidades que tenga cada paquete y las guarda en DB

        :param product_added: Objeto de producto
        :return: None
        """

        unit_actual = cls.initial_unit_fridge(product_added)
        fridge_entry = Fridge(
            product_id=product_added.id,
            unit_actual=unit_actual
        )

        session.add(product)
        session.commit()
        session.close()

    @classmethod
    def initial_unit_fridge(cls, product_added) -> int:
        """
        Calcula el número actualizado de unidades en la nevera al agregar las unidades por paquete del producto dado.

        :param producto_agregado: El objeto del producto que se agrega.
        :return: El nuevo total de unidades en la nevera después de agregar las unidades por paquete.
        """

        # Obtengo las unidades del paquete y las unidades que hay en la nevera
        unit_actual = session.query(Fridge.unit_actual).filter(Fridge.product_id == product_added.id).order_by(
            Fridge.id.desc()).limit(1).scalar()
        units_per_package = session.query(Products.unit_packaging).filter(Products.id == product_added.id).scalar()
        # Hago la operación de sumar a lo que hay en la nevera lo que añado
        if unit_actual is None:
            new_unit_actual = units_per_package
        else:
            new_unit_actual = unit_actual + units_per_package

        return new_unit_actual

    @classmethod
    def sow_products_in_fridge(cls):
        all_products_in_fridge = session.query(Fridge).all()
        products = []
        for product_in_fridge in all_products_in_fridge:
            name = session.query(Products.name).filter(Products.id == product_in_fridge.product_id).first()
            date_in = product_in_fridge.date_in
            unit_actual = product_in_fridge.unit_actual
            if unit_actual != 0:
                product_data = {
                    "name": name[0],
                    "unit_actual": unit_actual,
                    "date_in": date_in.isoformat()
                }
                products.append(product_data)
        return products
