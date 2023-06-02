from database.database import Base, session
from sqlalchemy import Column, Integer, ForeignKey, BigInteger, func, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from models import ProductSuperRelationship, Products
from models.super import Supermarket
import setting.logging as log
import logging

log.configure_logging()
logger = logging.getLogger(__name__)


class ShoppingList(Base):  # Supermercado Día
    __tablename__ = "shoplist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_in = Column(Date, default=datetime.utcnow)
    date_buy = Column(Date)

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
        """
        Agrega un producto a la lista de compras a partir de la información de la nevera.
            subquery: Realiza un filtro por el id del producto para la fecha más actual en la que hay precios
            query: Filtra por producto y por la fecha máxima para obtener un objeto de la relación

        :param product_fridge: El objeto del producto en la nevera.
        :return: None
        """
        # Obtengo la última fecha
        subquery = (
            session.query(func.max(ProductSuperRelationship.date).label("max_date"))
            .filter(ProductSuperRelationship.product_id == product_fridge.product_id)
            .group_by(ProductSuperRelationship.product_id)
            .subquery()
        )

        # Realizar la consulta principal para obtener el resultado final
        prod_super_relation = (
            session.query(ProductSuperRelationship)
            .filter(
                ProductSuperRelationship.product_id == product_fridge.product_id,
                ProductSuperRelationship.date == subquery.c.max_date,
            )
            .order_by(ProductSuperRelationship.price)
            .first()
        )

        shopping_list_product = ShoppingList(
            product_id=product_fridge.product_id, super_id=prod_super_relation.super_id
        )

        session.add(shopping_list_product)
        session.commit()

    @classmethod
    def update_shopping_list(cls):
        """
        Actualiza la lista de compras con los productos y precios más baratos disponibles en los supermercados.
            Si todos los productos tienen registro en ProductSuperRelation actualiza
            los productos de la lista de la compra a los supers con el precio más barato,
            Si no tiene ningún registro descarga por primera vez los precios

        :return: None
        """
        products = session.query(Products).all()

        for product in products:
            super_list = []
            logger.info(product)
            # Busco si existe el producto en la tabla de relación de producto-supermercado para descargar el precio
            relation = (
                session.query(ProductSuperRelationship.super_id)
                .filter(ProductSuperRelationship.product_id == product.id)
                .all()
            )
            for i, value in enumerate(relation):
                super_list.append(value[0])
            super_list = list(dict.fromkeys(super_list))
            logger.info(super_list)
            if not super_list:
                logger.info("Está en NOT RELATION")
                # Download prices for first time
                ean = (
                    session.query(Products.ean).filter(Products.id == product.id).first()
                )
                Supermarket.extract_prices_supermarkets(ean=ean, product_added=product)

            if super_list:
                logger.info("Está en RELATION")
                # Obtengo la última fecha
                subquery = (
                    session.query(
                        func.max(ProductSuperRelationship.date).label("max_date")
                    )
                    .filter(ProductSuperRelationship.product_id == product.id)
                    .group_by(ProductSuperRelationship.product_id)
                    .subquery()
                )

                # Realizar la consulta principal para obtener el resultado final
                min_price_super = (
                    session.query(ProductSuperRelationship)
                    .filter(
                        ProductSuperRelationship.product_id == product.id,
                        ProductSuperRelationship.date == subquery.c.max_date,
                    )
                    .order_by(ProductSuperRelationship.price)
                    .first()
                )

                logger.info("Todos los precios coinciden")

                super_id = (
                    session.query(ShoppingList.super_id)
                    .filter(ShoppingList.product_id == product.id)
                    .first()
                )

                if min_price_super.super_id != super_id:
                    session.query(ShoppingList).filter(
                        ShoppingList.product_id == min_price_super.product_id
                    ).update({ShoppingList.super_id: min_price_super.super_id})

                    session.commit()

                    logger.info("Actualiza la tabla y la añade a mostrar")
