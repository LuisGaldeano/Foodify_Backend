import logging
import setting.logging as log
import cv2
from pyzbar import pyzbar

from models import Fridge
from models.products import Products
from models.super import Supermercado

log.configure_logging()
logger = logging.getLogger(__name__)


class FoodifyManager:
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
                # Establece la bandera de detección de código de barras en True
                self.print_rectangle(frame=frame, barcode=barcode)

    def scan_barcode(self, barcode: str):
        check = Products.check_ean_exists(barcode)
        if not check:
            # Logea el proceso
            logger.info("Doing register")
            # Obtiene el producto de offs y lo guarda
            Products.get_product_and_save(barcode)
            # Extrae los precios de los diferentes supermercados y los guarda en la tabla
            Supermercado.extract_prices_supermarket(barcode)
        elif check:
            product_data = {'code': barcode}
            Fridge.fridge_save_product(product_data)
            logger.info("Not a new product - Add to fridge")

    def detect_barcode(self, frame, new_product, detected_barcodes: list):
        if detected_barcodes:
            # Dibuha los rectángulos en la imagen
            self.print_rectangles(detected_barcodes=detected_barcodes, frame=frame)
            # Muestra el fotograma en una ventana
        cv2.imshow('scanner', frame)
        key = cv2.waitKey(1)
        if detected_barcodes and key == 13:
            for barcode in detected_barcodes:
                # Devuelve el código de barras
                barcode_to_use = barcode.data.decode("utf-8")
                if new_product:
                    self.scan_barcode(barcode=barcode_to_use)
                    logger.info("Producto registrado")
                elif not new_product:
                    self.send_to_shopping_list(barcode=barcode_to_use)

                    """
                    Tienes que definir la función shopping_list y hacer que borre el producto de la tabla nevera y lo
                    añada a la tabla lista de la compra
                    
                    
                    HECHO!!  --->   Para ello primero tienes que conseguir que cuando registras un producto nuevo se 
                    guarde no solo en la tabla products sino también en la tabla fridge
                    
                    Deja el que se vea por la api para más adelante, ejecuta foodify desde pruebas sin ejecutar la api
                    por ahora
                    """


                    logger.info("Producto enviado a shopping_list")

    def send_to_shopping_list(self, barcode:str):
        pass

    def capture_image(self, new_product):
        # Captura de un fotograma de la cámara
        success, frame = self.recorder.read()
        # Voltea el fotograma horizontalmente
        frame = cv2.flip(frame, 1)
        # Detecta los códigos de barras en el fotograma
        detected_barcodes = pyzbar.decode(frame)
        self.detect_barcode(frame=frame, detected_barcodes=detected_barcodes, new_product=new_product)

    def __init__(self, new_product=True):
        # Inicia la cámara pero no registra
        self.recorder = cv2.VideoCapture(0)
        # Mantiene la cámara abierta siempre
        while True:
            self.capture_image(new_product)
