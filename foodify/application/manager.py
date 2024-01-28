import os
from datetime import datetime

import cv2
import pytz
from pyzbar import pyzbar

from application.database.database import session
from application.models.fridge import Fridge
from application.models.product_super_relationship import \
    ProductSuperRelationship
from application.models.products import Products
from application.models.shopping_list import ShoppingList
from application.models.super import Supermarket
from core.logging import logger


class FoodifyManager:
    def add_product(self, barcode: str, recurrent: bool, units: int):
        """
            Agrega un producto a la nevera.

            Si el producto ya está registrado, devuelve el objeto del producto con el código de barras dado.
            Si el producto no está registrado, lo descarga de Open Food Facts, lo registra y devuelve el objeto del producto registrado.

            :param barcode: El código de barras del producto.
            :param recurrent: Indica si el producto es recurrente o no.
            :param units: La cantidad de unidades que tiene el paquete del producto.
            :return: Una tupla con el objeto del producto agregado y un mensaje informativo.
            """
        logger.info('Init product registration')
        # Si el producto está registrado devuelve el objeto producto con el barcode dado,
        # si no está registrado, lo descarga de offs, lo registra y devuelve el objeto del producto registrado.
        product_added = Products.get_or_create_product(barcode=barcode, recurrent=recurrent, units=units)

        product_in_fridge = session.query(Fridge).filter(Fridge.product_id == product_added.id,
                                                         Fridge.date_out is None).first()
        if not product_in_fridge:
            # Añade al frigorífico
            Fridge.save_fridge_product(product_added=product_added)
            info = f'El producto {product_added.name} se ha añadido a la nevera'
            logger.info(info)
            return product_added, info
        else:
            unit_actual = product_in_fridge.unit_actual
            unit_packaging = session.query(Products.unit_packaging).filter(Products.id == product_added.id).first()
            new_unit_actual = unit_actual + unit_packaging[0]
            # Actualiza las unit_actual al nuevo valor actual
            session.query(Fridge).filter(Fridge.product_id == product_added.id, Fridge.date_out is None) \
                .update({Fridge.unit_actual: new_unit_actual})

            session.commit()

            info = f'Ahora tienes {new_unit_actual} unidades del producto {product_added.name} en la nevera'
            logger.info(info)
            return product_added, info

    def add_super_first_time(self, product_added):
        """
            Agrega el supermercado por primera vez para un producto.

            Busca si el producto ya existe en la tabla de relaciones entre producto y supermercado para descargar el precio.
            Si no existe ninguna relación, descarga los precios del producto de los supermercados disponibles.

            :param product_added: El objeto del producto agregado.
            :return: None
            """
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
        """
            Registra un nuevo producto a partir de los códigos de barras detectados.

            Itera sobre los códigos de barras detectados y registra cada producto utilizando la función add_product.
            Devuelve el objeto del producto registrado y la información relacionada.

            :param detected_barcodes: Tupla de códigos de barras detectados.
            :param recurrent: Indica si el producto es recurrente.
            :param units: La cantidad de unidades que tiene el paquete del producto.
            :return: Tupla que contiene el objeto del producto registrado y la información relacionada.
            """
        for barcode in detected_barcodes:
            # Devuelve el código de barras
            barcode_to_use = barcode.data.decode("utf-8")
            product, info = self.add_product(barcode=barcode_to_use, recurrent=recurrent, units=units)
            logger.info("Registered product")

            return product, info

    def old_product(self, detected_barcodes: tuple):
        """
            Registra un producto gastado a partir de los códigos de barras detectados.

            Itera sobre los códigos de barras detectados y verifica el estado actual del producto en el frigorífico
            utilizando la función check_unit_actual_in_fridge. Registra el producto gastado y devuelve el objeto del
            producto y la información relacionada.

            :param detected_barcodes: Tupla de códigos de barras detectados.
            :return: Tupla que contiene el objeto del producto gastado y la información relacionada.
            """
        for barcode in detected_barcodes:
            # Devuelve el código de barras
            barcode_to_use = barcode.data.decode("utf-8")
            product, info = self.check_unit_actual_in_fridge(barcode_to_use=barcode_to_use)
            logger.info(f"Producto : {product.name}. {info}")
            return product, info

    def check_unit_actual_in_fridge(self, barcode_to_use: str):
        """
            Verifica el estado actual de un producto en el frigorífico a partir del código de barras utilizado.

            Busca el producto correspondiente al código de barras en la base de datos y obtiene su estado actual en el frigorífico.
            Actualiza el estado del producto en caso de que se haya gastado una unidad y devuelve el objeto del producto y la
            información relacionada.

            :param barcode_to_use: Código de barras utilizado para identificar el producto.
            :return: Tupla que contiene el objeto del producto y la información relacionada.
        """
        try:
            # Selecciona el producto con ese ean y me añade la fecha actual a date_out
            product = session.query(Products).filter(Products.ean == barcode_to_use).first()
            product_fridge = session.query(Fridge).filter(Fridge.product_id == product.id).order_by(
                Fridge.id.desc()).first()
            unit_actual = product_fridge.unit_actual
            new_unit_actual = unit_actual - 1

            # Crear un solo caso con elif

            if new_unit_actual == 0:
                logger.info('Se ha acabado el producto')
                # Añade el date_out y actualiza las unit_actual a 0
                session.query(Fridge).filter(Fridge.id == product_fridge.id).update(
                    {Fridge.date_out: datetime.utcnow(), Fridge.unit_actual: new_unit_actual})

                session.commit()

                if product.recurrent:
                    # Chequea si hay precios para ese producto en ProductSuperRelation
                    check = session.query(ProductSuperRelationship) \
                        .filter(ProductSuperRelationship.product_id == product.id).all()
                    if check:
                        # Después de registrar la fecha de salida en Fridge envía a la lista de la compra
                        ShoppingList.send_to_shopping_list(product_fridge)
                        info = f'El producto {product.name} se ha añadido a la lista de la compra'
                        return product, info
                    else:
                        Supermarket.extract_prices_supermarkets(ean=product.ean, product_added=product)
                        ShoppingList.send_to_shopping_list(product_fridge)
                        info = f'El producto {product.name} se ha añadido a la lista de la compra'
                        return product, info
            elif new_unit_actual >= 0:
                # Actualiza las unit_actual al nuevo valor actual
                session.query(Fridge).filter(Fridge.id == product_fridge.id).update(
                    {Fridge.unit_actual: new_unit_actual})

                session.commit()

                info = f'Te quedan {new_unit_actual} del producto {product.name}'
                return product, info
            else:
                info = f'El producto {product.name} no está en la nevera'
                return product, info
        except Exception as ex:
            logger.exception('This product was not in the fridge')
            raise ex

    def buy_shopping_list(self):
        """
            Realiza la compra de los productos que están en la lista de la compra.

            Obtiene todos los productos que están en la lista de la compra y realiza las acciones necesarias para comprar cada uno
            de ellos. Para cada producto, obtiene su nombre, el nombre del supermercado y el precio actual del producto en ese
            supermercado.
            Luego, actualiza la fecha de compra del producto en la lista de la compra y lo agrega al frigorífico.
            Finalmente, devuelve un diccionario que contiene los nombres de los productos como claves y una tupla que contiene el
            nombre del supermercado y el precio como valor.

            :return: Diccionario que contiene los productos comprados y su información relacionada.
        """
        # Traigo todos los productos que están en la lista de la compra
        buy_products = session.query(ShoppingList).filter(ShoppingList.date_buy is None).all()

        buy_list = {}

        for product in buy_products:
            # Traigo el nombre del producto de Products
            product_name = session.query(Products.name).filter(Products.id == product.product_id).first()

            # Traigo el nombre del supermercado de Supermarket
            super_name = session.query(Supermarket.name).filter(Supermarket.id == product.super_id).first()

            # Traigo el precio del producto de ProductSuperRelation
            price = session.query(ProductSuperRelationship.price) \
                .filter(ProductSuperRelationship.product_id == product.product_id,
                        Supermarket.id == product.super_id,
                        ProductSuperRelationship.date == datetime.utcnow().date()).first()

            # Agrego al diccionario
            buy_list[product_name[0]] = (super_name[0].value, price[0])

            # Actualiza las unit_actual al nuevo valor actual
            session.query(ShoppingList).filter(ShoppingList.product_id == product.product_id,
                                               ShoppingList.id == product.id) \
                .update({ShoppingList.date_buy: datetime.utcnow().date()})

            session.commit()

            # Añade al frigorifico
            product_added = session.query(Products).filter(Products.id == product.product_id).first()
            Fridge.save_fridge_product(product_added)

        return buy_list

    def update_prices(self, night_update: bool):
        """
            Actualiza los precios de los productos.

            Obtiene todos los productos de la base de datos y, dependiendo del valor de "night_update" y la hora actual, realiza
            la extracción de precios de los supermercados para cada producto.
            Si "night_update" es True y la hora actual es 1 de la mañana, se realiza la extracción de precios para todos los productos.
            Si "night_update" es False, se realiza la extracción de precios para todos los productos sin importar la hora actual.

            :param night_update: Indica si se debe realizar una actualización nocturna.
        """
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
        """
            Marca el código de barras en el fotograma y le añade un rectángulo.

            Esta función toma un fotograma "frame" y un código de barras "barcode" como entrada y marca el código de barras en el
            fotograma agregando un rectángulo alrededor de él. También muestra el código de barras como texto en el fotograma.

            :param frame: El fotograma en el que se encuentra el código de barras.
            :param barcode: El código de barras que se va a marcar.
        """
        # Marca el código de barras en el fotograma y le añade un rectángulo
        x, y, width, height = barcode.rect
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 2)  # Pinta el rectángulo
        cv2.putText(frame, str(barcode.data), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255),
                    2)  # Pinta el código

    def print_rectangles(self, frame, detected_barcodes: list):
        """
            Marca los códigos de barras detectados en el fotograma.

            Esta función toma un fotograma "frame" y una lista de códigos de barras detectados "detected_barcodes" como entrada,
            y marca cada código de barras en el fotograma agregando un rectángulo alrededor de él.
            Utiliza la función "print_rectangle" para marcar cada código de barras individualmente.

            :param frame: El fotograma en el que se encuentran los códigos de barras.
            :param detected_barcodes: La lista de códigos de barras detectados.
            """
        # Itera sobre cada código de barras detectado
        for barcode in detected_barcodes:
            # Verifica si el código de barras no está vacío
            if barcode.data != "":
                logger.info('Ha reconocido un barcode')
                # Establece la bandera de detección de código de barras en True
                self.print_rectangle(frame=frame, barcode=barcode)

    def detect_barcode(self, frame, detected_barcodes: list):
        """
            Detecta y marca los códigos de barras en un fotograma.

            Esta función toma un fotograma "frame" y una lista de códigos de barras detectados "detected_barcodes" como entrada,
            y marca los códigos de barras en el fotograma si se detectan. Utiliza la función "print_rectangles" para marcar los
            códigos de barras detectados.

            :param frame: El fotograma en el que se desea detectar los códigos de barras.
            :param detected_barcodes: La lista de códigos de barras detectados.
            :raises Exception: Si no se detectan códigos de barras en el fotograma.
            """
        if detected_barcodes:
            # Dibuha los rectángulos en la imagen
            self.print_rectangles(detected_barcodes=detected_barcodes, frame=frame)
            # cv2.imshow('scanner', frame)
        else:
            raise Exception

    def capture_image_and_get_barcodes(self) -> tuple:
        """
            Captura una imagen y obtiene los códigos de barras detectados.

            Esta función captura un fotograma de la cámara o carga una imagen de prueba desde una ruta especificada.
            Luego, voltea el fotograma horizontalmente y utiliza la biblioteca pyzbar para detectar los códigos de barras en
            el fotograma.
            Llama a la función "detect_barcode" para marcar los códigos de barras detectados en el fotograma.

            :return: Una tupla que contiene los códigos de barras detectados.
        """
        # Captura de un fotograma de la cámara
        if self.recorder:
            # This method will return if the camera made the photo or not and the photo
            # itself, so the first value we can skip it
            _, frame = self.recorder.read()
        else:
            test_image_path = os.getenv("TEST_IMAGE_PATH")
            logger.info(test_image_path)
            frame = cv2.imread(test_image_path)
        # Voltea el fotograma horizontalmente
        frame = cv2.flip(frame, 1)
        # Detecta los códigos de barras en el fotograma
        detected_barcodes = pyzbar.decode(frame)
        self.detect_barcode(frame=frame, detected_barcodes=detected_barcodes)
        return detected_barcodes

    def __init__(self):
        """
            Inicializa el objeto FoodifyManager.

            El método __init__ se encarga de iniciar el manager de Foodify.
            Configura el entorno, la ruta de la imagen de prueba y la cámara.
            En función del entorno, se establece el atributo 'recorder' para capturar imágenes de la cámara o se
            deja como 'None' en caso de que el entorno sea de prueba.

            Parámetros:
                - No recibe ningún parámetro.

        """

        environment = os.getenv("ENVIRONMENT")
        if environment == "dev":
            self.recorder = None
        else:
            self.recorder = cv2.VideoCapture(0)
        logger.info('End loading camera')


manager = FoodifyManager()
