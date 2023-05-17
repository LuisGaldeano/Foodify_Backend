import logging
import setting.logging as log
import cv2
from pyzbar import pyzbar
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

    def detect_barcode(self, frame, detected_barcodes: list):
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
                self.scan_barcode(barcode=barcode_to_use)
                logger.info("Imagen guardada")




    def capture_image(self):
        # Captura de un fotograma de la cámara
        success, frame = self.recorder.read()
        # Voltea el fotograma horizontalmente
        frame = cv2.flip(frame, 1)
        # Detecta los códigos de barras en el fotograma
        detected_barcodes = pyzbar.decode(frame)
        self.detect_barcode(frame=frame, detected_barcodes=detected_barcodes)

    def __init__(self):
        # Inicia la cámara pero no registra
        self.recorder = cv2.VideoCapture(0)
        # Mantiene la cámara abierta siempre
        while True:
            self.capture_image()
