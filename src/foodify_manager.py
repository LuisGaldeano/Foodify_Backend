import logging
import os
from datetime import datetime
import setting.logging as log
import cv2
from pyzbar import pyzbar
from database.database import session
from models import Fridge, ShoppingList, ProductSuperRelationship
from models.products import Products
from models.super import Supermarket
import pytz

log.configure_logging()
logger = logging.getLogger(__name__)


class FoodifyManager:

    def add_product(self, barcode: str, recurrent: bool, units: int):
        logger.info('Init product registration')
        # Si el producto está registrado devuelve el objeto producto con el barcode dado,
        # si no está registrado, lo descarga de offs, lo registra y devuelve el objeto del producto registrado.
        product_added = Products.get_or_create_product(barcode=barcode, recurrent=recurrent, units=units)

        product_in_fridge = session.query(Fridge).filter(Fridge.product_id == product_added.id,
                                                         Fridge.date_out == None).first()
        if not product_in_fridge:
            # Añade al frigorífico
            Fridge.fridge_save_product(product_added=product_added)
            return f'El producto {product_added.name} se ha añadido a la nevera'
        else:
            unit_actual = product_in_fridge.unit_actual
            unit_packaging = session.query(Products.unit_packaging).filter(Products.id == product_added.id).first()
            new_unit_actual = unit_actual + unit_packaging[0]
            # Actualiza las unit_actual al nuevo valor actual
            session.query(Fridge).filter(Fridge.product_id == product_added.id, Fridge.date_out == None)\
                .update({Fridge.unit_actual: new_unit_actual})

            session.commit()

            return f'Ahora tienes {new_unit_actual} unidades del producto {product_added.name} en la nevera'

    def add_super_first_time(self, product_added):
        # Busco si existe el producto en la tabla de relación de producto-supermercado para descargar el precio
        super_list = []
        relation = session.query(ProductSuperRelationship.super_id).filter(
            ProductSuperRelationship.product_id == product_added.id).all()
        for i, value in enumerate(relation):
            super_list.append(value[0])
        super_list = set(super_list)

        if not super_list:
            # Download prices for first time
            Supermarket.extract_prices_supermarkets(ean=product_added.ean, product_added=product_added)

    def new_product(self, detected_barcodes: tuple, recurrent: bool, units: int):
        for barcode in detected_barcodes:
            # Devuelve el código de barras
            barcode_to_use = barcode.data.decode("utf-8")
            product = self.add_product(barcode=barcode_to_use, recurrent=recurrent, units=units)
            logger.info("Registered product")
            return product

    def old_product(self, detected_barcodes: tuple):
        for barcode in detected_barcodes:
            # Devuelve el código de barras
            barcode_to_use = barcode.data.decode("utf-8")
            check = self.check_unit_actual_in_fridge(barcode_to_use=barcode_to_use)
            logger.info("Producto gastado")
            return check

    def check_unit_actual_in_fridge(self, barcode_to_use: str):
        try:
            # Selecciona el producto con ese ean y me añade la fecha actual a date_out
            product = session.query(Products).filter(Products.ean == barcode_to_use).first()
            product_fridge = session.query(Fridge).filter(Fridge.product_id == product.id).order_by(
                Fridge.id.desc()).first()
            unit_actual = product_fridge.unit_actual
            new_unit_actual = unit_actual - 1

            # Crear un solo caso con elif

            if new_unit_actual >= 0:
                if new_unit_actual == 0:
                    logger.info('Se ha acabado el producto')
                    # Añade el date_out y actualiza las unit_actual a 0
                    session.query(Fridge).filter(Fridge.id == product_fridge.id).update(
                        {Fridge.date_out: datetime.utcnow(), Fridge.unit_actual: new_unit_actual})

                    session.commit()

                    if product.recurrent:
                        # Después de registrar la fecha de salida en Fridge envía a la lista de la compra
                        ShoppingList.send_to_shopping_list(product_fridge)
                        return f'El producto {product.name} se ha añadido a la lista de la compra'
                else:
                    # Actualiza las unit_actual al nuevo valor actual
                    session.query(Fridge).filter(Fridge.id == product_fridge.id).update(
                        {Fridge.unit_actual: new_unit_actual})

                    session.commit()

                    return f'Te quedan {new_unit_actual} del producto {product.name}'
            else:
                return f'El producto {product.name} no está en la nevera'
        except Exception as ex:
            logger.exception('This product was not in the fridge')
            raise ex

    def buy_shopping_list(self):
        # Traigo todos los productos que están en la lista de la compra
        buy_products = session.query(ShoppingList).filter(ShoppingList.date_buy == None).all()

        buy_list = {}

        for product in buy_products:
            logger.info(product)
            # Traigo el nombre del producto de Products
            product_name = session.query(Products.name).filter(Products.id == product.product_id).first()
            logger.info(product_name)

            # Traigo el nombre del supermercado de Supermarket
            super_name = session.query(Supermarket.name).filter(Supermarket.id == product.super_id).first()
            logger.info(super_name)

            # Traigo el precio del producto de ProductSuperRelation
            price = session.query(ProductSuperRelationship.price) \
                .filter(ProductSuperRelationship.product_id == product.product_id,
                        Supermarket.id == product.super_id,
                        ProductSuperRelationship.date == datetime.utcnow().date()).first()

            logger.info(price)

            # Agrego al diccionario
            buy_list[product_name[0]] = (super_name[0].value, price[0])

            # Actualiza las unit_actual al nuevo valor actual
            session.query(ShoppingList).filter(ShoppingList.product_id == product.product_id,
                                               ShoppingList.id == product.id) \
                .update({ShoppingList.date_buy: datetime.utcnow().date()})

            session.commit()

            # Añade al frigorifico
            product_added = session.query(Products).filter(Products.id == product.product_id).first()
            Fridge.fridge_save_product(product_added)

        return buy_list

    def update_prices(self, night_update: bool):
        products = session.query(Products).all()
        timezone = pytz.timezone('Europe/Madrid')
        current_time = datetime.now(timezone)
        logger.info(f'{current_time.time().hour}')
        if night_update:
            if current_time.time().hour == 1:
                for product in products:
                    Supermarket.extract_prices_supermarkets(ean=product.ean, product_added=product)
        else:
            for product in products:
                Supermarket.extract_prices_supermarkets(ean=product.ean, product_added=product)

    def print_rectangle(self, frame, barcode: str):
        # Marca el código de barras en el fotograma y le añade un rectángulo
        x, y, width, height = barcode.rect
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 2)  # Pinta el rectángulo
        cv2.putText(frame, str(barcode.data), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255),
                    2)  # Pinta el código

    def print_rectangles(self, frame, detected_barcodes: list):
        # Itera sobre cada código de barras detectado
        for barcode in detected_barcodes:
            # Verifica si el código de barras no está vacío
            if barcode.data != "":
                logger.info('Ha reconocido un barcode')
                # Establece la bandera de detección de código de barras en True
                self.print_rectangle(frame=frame, barcode=barcode)

    def detect_barcode(self, frame, detected_barcodes: list):
        if detected_barcodes:
            # Dibuha los rectángulos en la imagen
            self.print_rectangles(detected_barcodes=detected_barcodes, frame=frame)
            # cv2.imshow('scanner', frame)
        else:
            raise Exception

    def capture_image_and_get_barcodes(self) -> tuple:
        # Captura de un fotograma de la cámara
        if self.recorder:
            # This method will return if the camera made the photo or not and the photo
            # itself, so the first value we can skip it
            _, frame = self.recorder.read()
        else:
            test_image_path = os.getenv("TEST_IMAGE_PATH")
            frame = cv2.imread(test_image_path)
        # Voltea el fotograma horizontalmente
        frame = cv2.flip(frame, 1)
        # Detecta los códigos de barras en el fotograma
        detected_barcodes = pyzbar.decode(frame)
        self.detect_barcode(frame=frame, detected_barcodes=detected_barcodes)
        return detected_barcodes

    def __init__(self):

        # Inicia el manager
        environment = os.getenv("ENVIRONMENT", None)
        test_image_path = os.getenv("TEST_IMAGE_PATH", None)
        logger.info(f"Init foodify manager for '{environment}' environment")
        if (
                environment and
                environment == "test"
        ):
            self.recorder = None
        else:
            self.recorder = cv2.VideoCapture(0)
        logger.info('End loading camera')
