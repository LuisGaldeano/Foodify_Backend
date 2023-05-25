from database.database import Base, session
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from models import ProductSuperRelationship
from models.super import Supermarket
import setting.logging as log
import logging

log.configure_logging()
logger = logging.getLogger(__name__)


class ShoppingList(Base):  # Supermercado Día
    __tablename__ = 'shoplist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_in = Column(DateTime, default=datetime.utcnow)
    date_buy = Column(DateTime)

    product_id = Column(BigInteger, ForeignKey("products.id"))
    products = relationship("Products", back_populates="shoppinglists")

    super_id = Column(Integer, ForeignKey("supermarket.id"))
    supers = relationship("Supermarket", back_populates="shoppinglists")


    def __str__(self):
        return f"id= {self.id}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def send_to_shopping_list(cls, product_fridge):
        # Obtengo la última fecha
        subquery = session.query(
            func.max(ProductSuperRelationship.date).label('max_date')
        ).filter(
            ProductSuperRelationship.product_id == product_fridge.product_id
        ).group_by(
            ProductSuperRelationship.product_id
        ).subquery()

        # Realizar la consulta principal para obtener el resultado final
        prod_super_relation = session.query(ProductSuperRelationship).filter(
            ProductSuperRelationship.product_id == product_fridge.product_id,
            ProductSuperRelationship.date == subquery.c.max_date
        ).order_by(
            ProductSuperRelationship.price
        ).first()

        shopping_list_product = ShoppingList(
            product_id=product_fridge.product_id,
            super_id=prod_super_relation.super_id
        )

        session.add(shopping_list_product)
        session.commit()

    @classmethod
    def get_prices_list(cls, ):
        products = session.query(ShoppingList.ean_id).all()
        for product in products:
            ean_id = str(product[0])
            Supermarket.extract_prices_supermarkets(ean_id)
