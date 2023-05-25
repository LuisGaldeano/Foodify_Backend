import logging
import setting.logging as log
import cv2
from pyzbar import pyzbar
from database.database import session
from models import Fridge, ShoppingList, ProductSuperRelationship
from models.products import Products
from models.super import Supermarket

log.configure_logging()
logger = logging.getLogger(__name__)


class FoodifyManager:
    def add_product(self, barcode: str, recurrent: bool, units: int):
        logger.info('Init product registration')
        # Si el producto está registrado devuelve el objeto producto con el barcode dado,
        # si no está registrado, lo descarga de offs, lo registra y devuelve el objeto del producto registrado.
        product_added = Products.get_or_create_product(barcode=barcode, recurrent=recurrent, units=units)
        ean = product_added.ean
        # ESTOY BASTANTE SEGURO DE QUE EL FALLO ME LO DA AQUI POR EL FORMATO EN EL QUE ME ENVÍA EL PRODUCT_ADDED DE LOS HUEVOS!!!!

        # Una vez registrado añade al frigorífico
        Fridge.fridge_save_product(product_added)

        # Busco si existe el producto en la tabla de relación de producto-supermercado para descargar el precio
        super_list = []
        relation = session.query(ProductSuperRelationship.super_id).filter(ProductSuperRelationship.product_id == product_added.id).all()
        for i, value in enumerate(relation):
            super_list.append(value[0])
        super_list = set(super_list)

        if not super_list:
            # Download prices for first time
            Supermarket.extract_prices_supermarkets(ean=ean, product_added=product_added)
        if super_list:

            # AQUÍ ES DONDE TIENES QUE PONER QUE SOLO DESCARGUE LOS PRECIOS CUANDO SE LO PIDES POR LA NOCHE

            pass

    def new_product(self, detected_barcodes: tuple, recurrent: bool, units: int):
        for barcode in detected_barcodes:
            # Devuelve el código de barras
            barcode_to_use = barcode.data.decode("utf-8")
            self.add_product(barcode=barcode_to_use, recurrent=recurrent, units=units)
            logger.info("Registered product")

    def old_product(self, detected_barcodes: tuple):
        for barcode in detected_barcodes:
            # Devuelve el código de barras
            barcode_to_use = barcode.data.decode("utf-8")
            self.check_unit_actual_in_fridge(barcode_to_use=barcode_to_use)
            logger.info("Producto gastado")

    def check_unit_actual_in_fridge(self, barcode_to_use: str):
        try:
            # Selecciona el producto con ese ean y me añade la fecha actual a date_out
            product = session.query(Products).filter(Products.ean == barcode_to_use).first()
            product_fridge = session.query(Fridge).filter(Fridge.product_id == product.id).order_by(Fridge.id.desc()).first()
            unit_actual = product_fridge.unit_actual
            new_unit_actual = unit_actual - 1

            if new_unit_actual == 0:
                logger.info('Se ha acabado el producto')
                # Añade el date_out y actualiza las unit_actual a 0
                session.query(Fridge).filter(Fridge.id == product_fridge.id).update({Fridge.date_out: datetime.utcnow(), Fridge.unit_actual: new_unit_actual})

                session.commit()

                if product.recurrent:
                    # Después de registrar la fecha de salida en Fridge envía a la lista de la compra
                    ShoppingList.send_to_shopping_list(product_fridge)
                    logger.info('Producto añadido a la lista de la compra')
            else:
                # Actualiza las unit_actual al nuevo valor actual
                session.query(Fridge).filter(Fridge.id == product_fridge.id).update({Fridge.unit_actual: new_unit_actual})

                session.commit()
        except:
            logger.exception('This product was not in the fridge')

    def print_rectangle(self, frame, barcode: str):
        # Marca el código de barras en el fotograma y le añade un rectángulo
        x, y, width, height = barcode.rect
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 2)  # Pinta el rectángulo
        cv2.putText(frame, str(barcode.data), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 2)  # Pinta el código

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
        success, frame = self.recorder.read()
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
