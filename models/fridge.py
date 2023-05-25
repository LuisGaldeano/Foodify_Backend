import logging
from datetime import datetime
from database.database import Base, session
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float, DateTime
from sqlalchemy.orm import relationship
import setting.logging as log
from models.products import Products

log.configure_logging()
logger = logging.getLogger(__name__)


class Fridge(Base):
    __tablename__ = 'fridge'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_in = Column(DateTime, default=datetime.utcnow)
    date_out = Column(DateTime)
    unit_initial = Column(Integer)
    unit_actual = Column(Integer)

    product_id = Column(BigInteger, ForeignKey("products.id"))
    products = relationship("Products", back_populates="fridge")

    def __str__(self):
        return f"id= {self.id}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def fridge_save_product(cls, product_added):
        # Calcula las unidades actuales y las iniciales
        # SOBRAN LAS unit_initial
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
        # Obtengo las unidades del paquete y las unidades que hay en la nevera
        unit_actual = session.query(Fridge.unit_actual).filter(Fridge.product_id == product_added.id).order_by(Fridge.id.desc()).limit(1).scalar()
        units_per_package = session.query(Products.unit_packaging).filter(Products.id == product_added.id).scalar()
        # Hago la operación de sumar a lo que hay en la nevera lo que añado
        if unit_actual is None:
            new_unit_actual = units_per_package
        else:
            new_unit_actual = unit_actual + units_per_package

        return new_unit_actual

    @classmethod
    def delete_product(cls, barcode_to_use: str):
        product = session.query(Fridge).filter(Fridge.ean_id == barcode_to_use).first()

        session.delete(product)
        session.commit()
