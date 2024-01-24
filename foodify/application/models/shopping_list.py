from application.database.database import Base, session
from sqlalchemy import Column, Integer, ForeignKey, BigInteger, func, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from application.models.product_super_relationship import ProductSuperRelationship
from application.models.products import Products
from application.models.super import Supermarket
from core.logging import logger
from fpdf import FPDF



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

            # Busco si existe el producto en la tabla de relación de producto-supermercado para descargar el precio
            relation = (
                session.query(ProductSuperRelationship.super_id)
                .filter(ProductSuperRelationship.product_id == product.id)
                .all()
            )
            for i, value in enumerate(relation):
                super_list.append(value[0])
            super_list = list(dict.fromkeys(super_list))

            if not super_list:
                # Download prices for first time
                ean = (
                    session.query(Products.ean).filter(Products.id == product.id).first()
                )
                Supermarket.extract_prices_supermarkets(ean=ean, product_added=product)

            if super_list:

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

    @classmethod
    def sow_products_in_shopping_list(cls):
        """
            Actualiza la lista de compras y recopila los productos en la lista.

            :param cls: Classmethod de ShoppingList.
            :return: Una lista de diccionarios que contienen los detalles de los productos en la lista de compras.
                     Cada diccionario tiene las siguientes claves:
                       - "name": El nombre del producto.
                       - "date_in": La fecha en que se agregó el producto a la lista en formato ISO.
                       - "super": El nombre del supermercado donde se puede encontrar el producto.
                       - "price": El precio del producto.
                       - "currency": La moneda en la que se muestra el precio.
            """

        cls.update_shopping_list()
        all_products_in_shopping_list = session.query(ShoppingList).all()
        products = []
        for product_in_shopping_list in all_products_in_shopping_list:
            name = session.query(Products.name).filter(Products.id == product_in_shopping_list.product_id).first()
            supermarket = session.query(Supermarket.name).filter(
                Supermarket.id == product_in_shopping_list.super_id).first()
            date_in = product_in_shopping_list.date_in
            date_buy = product_in_shopping_list.date_buy
            price = session.query(ProductSuperRelationship) \
                .filter(ProductSuperRelationship.product_id == product_in_shopping_list.product_id,
                        ProductSuperRelationship.super_id == product_in_shopping_list.super_id).first()

            if not date_buy:
                product_data = {
                    "name": name[0],
                    "date_in": date_in.isoformat(),
                    "super": supermarket[0].value,
                    "price": price.price,
                    "currency": price.currency
                }
                products.append(product_data)
        return products

    @classmethod
    def create_buy_links(cls):
        """
            Crea enlaces de compra para los productos de la lista de la compra.

            :return: Una lista de json que contienen los detalles de los productos con enlaces de compra.
                     Cada json tiene las siguientes claves:
                       - "id": El identificador numérico del producto.
                       - "Producto": Una cadena que indica el número de producto en la lista.
                       - "Nombre": El nombre del producto.
                       - "Supermercado": El nombre del supermercado donde se puede encontrar el producto.
                       - "Precio": El precio del producto.
                       - "URL": El enlace de compra del producto.
            """
        products = session.query(cls).filter(cls.date_buy == None).all()
        shopping_list = []

        # Recorrer la lista de productos y agregarlos al PDF
        for i, product in enumerate(products):
            producto = session.query(Products).filter(Products.id == product.product_id).first()
            supermarket = session.query(Supermarket.name).filter(Supermarket.id == product.super_id).first()

            price = session.query(ProductSuperRelationship.price) \
                .filter(ProductSuperRelationship.super_id == product.super_id,
                        ProductSuperRelationship.product_id == product.product_id) \
                .order_by(ProductSuperRelationship.date).first()

            url_super = session.query(Supermarket.url_scrapper).filter(Supermarket.id == product.super_id).first()
            url = f"{url_super[0]}{producto.ean}"

            product_json = {
                "id": i + 1,
                "Producto": f"Producto {i + 1}",
                "Nombre": producto.name,
                "Supermercado": supermarket[0].value,
                "Precio": price[0],
                "URL": url
            }

            shopping_list.append(product_json)

        return shopping_list

    @classmethod
    def create_pdf(cls):
        """
        Crea un archivo PDF con los detalles de los productos en la lista de la compra.

        :return: None
        """
        products = session.query(cls).filter(cls.date_buy == None).all()

        # Crear un objeto PDF
        pdf = FPDF()

        # Añadir una página al PDF
        pdf.add_page()

        # Establecer la fuente y el tamaño de la fuente
        pdf.set_font('Arial', size=12)

        date = datetime.utcnow().date()

        # Recorrer la lista de productos y agregarlos al PDF
        for i, product in enumerate(products):
            producto = session.query(Products).filter(Products.id == product.product_id).first()
            supermarket = session.query(Supermarket.name).filter(Supermarket.id == product.super_id).first()

            price = session.query(ProductSuperRelationship.price) \
                .filter(ProductSuperRelationship.super_id == product.super_id,
                        ProductSuperRelationship.product_id == product.product_id) \
                .order_by(ProductSuperRelationship.date).first()

            url_super = session.query(Supermarket.url_scrapper).filter(Supermarket.id == product.super_id).first()
            url = f"{url_super[0]}{producto.ean}"

            # Agregar los datos al PDF
            pdf.cell(0, 10, f"Producto {i + 1}:", ln=True)
            pdf.cell(0, 5, f"Nombre: {producto.name}, Supermercado: {supermarket[0].value}, Precio: {price[0]} Euros",
                     ln=True)
            pdf.cell(0, 5, f"URL: {url}", ln=True)
            pdf.cell(0, 10, "", ln=True)

        # Guardar el archivo PDF
        pdf.output(f'./pdf/{date}-ListaCompra.pdf')
