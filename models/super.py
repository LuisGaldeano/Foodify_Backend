from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float, DateTime
from sqlalchemy.orm import relationship
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup as bs
import requests as req
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from models import Products

log.configure_logging()
logger = logging.getLogger(__name__)

PATH = ChromeDriverManager().install()  # instala driver de chrome


class Supermercado(Base):  # Supermercado Día
    __tablename__ = 'supermercado'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(255))
    price_num = Column(Float)
    price_simbol = Column(String(40))
    product_url = Column(String(255))
    fecha = Column(DateTime, default=datetime.utcnow)
    super = Column(String(255))

    ean_id = Column(BigInteger, ForeignKey("products.ean"))
    supermercado = relationship("Products")

    def __str__(self):
        return f"id= {self.id} - name= {self.product_name}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def save_product_dia(cls, ean: str, product_name: str, price_num: float, price_simbol: str,
                         product_url: str):
        supdia = Supermercado(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url,
            super='Dia'

        )

        session.add(supdia)
        session.commit()
        session.close()

    @classmethod
    def extract_data_dia(cls, ean: str):
        URL = 'https://www.dia.es/compra-online/search?text='

        html = req.get(URL + ean).text

        sopa = bs(html, 'html.parser')

        # Devuelve el precio
        price = sopa.find('p', class_='price')
        price_num_str = price.text.strip().split()[0]
        price_num = float(price_num_str.replace(',', '.'))
        price_simbol = price.text.strip().split()[1]

        # Devuelve el nombre
        name = sopa.find('span', class_='details')
        name = name.text.strip()

        # Devuelve la url del producto
        product_link = sopa.find('a', class_='productMainLink')
        product_href = product_link['href'].strip()
        product_url = f'https://www.dia.es{product_href}'

        if sopa:
            cls.save_product_dia(ean, name, price_num, price_simbol, product_url)
            return True
        return False

    @classmethod
    def extract_price_dia(cls, barcode):
        try:
            Supermercado.extract_data_dia(barcode)
            return True
        except Exception as e:
            logger.exception('Este producto no se vende en Dia')
            return False

    @classmethod
    def save_product_carrefour(cls, ean: str, product_name: str, price_num: float, price_simbol: str,
                               product_url: str):
        supcarr = Supermercado(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url,
            super='Carrefour'
        )

        session.add(supcarr)
        session.commit()
        session.close()

    @classmethod
    def extract_data_carrefour(cls, ean: str):
        # opciones del driver
        opciones = Options()

        # quita la bandera de ser robot
        opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
        opciones.add_experimental_option('useAutomationExtension', False)

        # No me abre la ventana
        # opciones.add_argument("--headless")
        # opciones.add_argument("--disable-gpu")

        # Abre una ventana de chrome
        driver = webdriver.Chrome(PATH, options=opciones)

        driver.get(f'https://www.carrefour.es/?q={ean}')

        time.sleep(3)

        price = driver.find_element(By.CLASS_NAME, "ebx-result-price__value")

        price_num_str = price.text.strip().split()[0]
        price_num = float(price_num_str.replace(',', '.'))
        price_simbol = price.text.strip().split()[1]

        # Devuelve el nombre
        name = driver.find_element(By.CLASS_NAME, "ebx-result-title")
        name = name.text.strip()

        # Devuelve la url del producto
        product_url = driver.find_element(By.CLASS_NAME, "ebx-result-link").get_attribute('href')

        if driver:
            cls.save_product_carrefour(ean, name, price_num, price_simbol, product_url)
            return True
        return False

    @classmethod
    def extract_price_carrefour(cls, barcode):
        try:
            Supermercado.extract_data_carrefour(barcode)
            return True
        except Exception as e:
            logger.info('Este producto no se vende en Carrefour')
            return False

    @classmethod
    def save_product_alcampo(cls, ean: str, product_name: str, price_num: float, price_simbol: str,
                             product_url: str):
        supalca = Supermercado(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url,
            super='Alcampo'
        )

        session.add(supalca)
        session.commit()
        session.close()

    @classmethod
    def extract_data_alcampo(cls, ean: str):
        # opciones del driver
        opciones = Options()

        # quita la bandera de ser robot
        opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
        opciones.add_experimental_option('useAutomationExtension', False)

        # No me abre la ventana
        # opciones.add_argument("--headless")
        # opciones.add_argument("--disable-gpu")

        # Abre una ventana de chrome
        driver = webdriver.Chrome(PATH, options=opciones)

        driver.get(f'https://www.alcampo.es/compra-online/search/?department=&text={ean}')

        time.sleep(3)

        price = driver.find_element(By.CLASS_NAME, "long-price")
        price_num_str = price.text.strip().split()[0]
        price_num = float(price_num_str.replace(',', '.'))
        price_simbol = price.text.strip().split()[1]

        # Devuelve el nombre
        name = driver.find_element(By.CLASS_NAME, "productName")
        name = name.text.strip()

        # Devuelve la url del producto
        product_url = driver.find_element(By.CLASS_NAME, "productMainLink").get_attribute('href')

        if driver:
            cls.save_product_alcampo(ean, name, price_num, price_simbol, product_url)
            return True
        return False

    @classmethod
    def extract_price_alcampo(cls, barcode):
        try:
            Supermercado.extract_data_alcampo(barcode)
            return True
        except Exception as e:
            logger.exception('Este producto no se vende en Alcampo')
            return False

    @classmethod
    def add_super_to_column(cls,supermarket, barcode: str):
        try:
            product = session.query(Products).filter_by(ean=barcode).first()
            shop_list = product.shop or ''  # Extraer el valor de la columna shop o usar una cadena vacía si es None
            if shop_list:
                shop_list += ', ' + supermarket  # Agregar el nuevo elemento a la cadena existente, separado por comas
            else:
                shop_list = supermarket  # Si no hay valores anteriores, usar solo el nuevo elemento
            product.shop = shop_list
            session.commit()
            logger.info(f'Valor actualizado exitosamente en {supermarket}.')
        except Exception as e:
            session.rollback()
            logger.exception(f'Error al actualizar el valor en {supermarket}: {str(e)}')
