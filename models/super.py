import logging
import os

import setting.logging as log
from sqlalchemy_utils import ChoiceType
from database.database import Base, session
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
from models import Products, ProductSuperRelationship


log.configure_logging()
logger = logging.getLogger(__name__)

PATH = ChromeDriverManager().install()  # instala driver de chrome


class Supermarket(Base):  # Supermercado Día
    DIA, CARREFOUR, ALCAMPO = 'dia', 'carrefour', 'alcampo'
    AVAILABLE_SUPERS = [
        (DIA, 'Dia'),
        (CARREFOUR, 'Carrefour'),
        (ALCAMPO, 'Alcampo'),
    ]
    __tablename__ = 'supermarket'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(ChoiceType(AVAILABLE_SUPERS))
    url_scrapper = Column(String(255))

    shoppinglists = relationship("ShoppingList", back_populates="supers")

    productsuprel = relationship("ProductSuperRelationship", back_populates="supers")


    def __str__(self):
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def add_new_super(cls, name_super: str, url: str):
        supermarket = Supermarket(
            name=name_super,
            url_scrapper=url
        )

        session.add(supermarket)
        session.commit()



    @classmethod
    def extract_prices_supermarkets(cls, ean, product_added):
        # Para cada supermercado en la lista de supermercados disponibles hago web scrapping
        for supermarket, _ in cls.AVAILABLE_SUPERS:
            if supermarket == cls.DIA:
                # Get or create super and return a super object
                url_dia = os.getenv("DIA_URL")
                super_market_dia = cls.get_or_create(name=cls.DIA, url_scrapper=url_dia)

                # Intenta descargar los precios mediante web strapping
                try:
                    Supermarket.extract_and_save_data_dia(ean=ean, super_market_dia=super_market_dia, product_added=product_added)
                except Exception as e:
                    logger.exception('Este producto no se vende en Dia')

            if supermarket == cls.CARREFOUR:
                # Get or create super and return a super object
                url_carrefour = os.getenv("CARREFOUR_URL")
                super_market_carrefour = cls.get_or_create(name=cls.CARREFOUR, url_scrapper=url_carrefour)

                try:
                    Supermarket.extract_and_save_data_carrefour(ean=ean, super_market_carrefour=super_market_carrefour, product_added=product_added)
                except Exception as e:
                    logger.exception('Este producto no se vende en Carrefour')

            if supermarket == cls.ALCAMPO:
                # Get or create super and return a super object
                url_alcampo = os.getenv("ALCAMPO_URL")
                super_market_alcampo = cls.get_or_create(name=cls.ALCAMPO, url_scrapper=url_alcampo)

                try:
                    Supermarket.extract_and_save_data_alcampo(ean=ean, super_market_alcampo=super_market_alcampo, product_added=product_added)
                except Exception as e:
                    logger.exception('Este producto no se vende en Carrefour')


    @classmethod
    def save_product_dia(cls, product_name: str, product_url: str):
        supdia = Supermarket(
            product_name=product_name,
            product_url=product_url
        )

        session.add(supdia)
        session.commit()


    @classmethod
    def extract_and_save_data_dia(cls, ean: int, super_market_dia, product_added):
        logger.info('Downloading Dia prices')
        try:
            ean = str(ean)

            # Extract the prices using beautiful soup
            html = req.get(super_market_dia.url_scrapper + ean).text
            sopa = bs(html, 'html.parser')

            # Devuelve el precio
            price = sopa.find('p', class_='search-product-card__active-price')
            price_num_str = price.text.strip().split()[0]
            price_num = float(price_num_str.replace(',', '.'))
            price_currency = price_num_str[1]

            if not price:
                raise Exception(f"Price not found for product '{product_added.id}' in Dia")

            ProductSuperRelationship.save_new_relation(price_num, price_currency, super_market_dia.id, product_added)
        except Exception as ex:
            raise Exception(f"El producto '{product_added.id}' no se vende en Día")

    @classmethod
    def save_product_carrefour(cls, product_name: str, product_url: str):
        supcarr = Supermarket(
            product_name=product_name,
            product_url=product_url
        )

        session.add(supcarr)
        session.commit()

    @classmethod
    def extract_and_save_data_carrefour(cls, ean: str, super_market_carrefour, product_added):
        logger.info('Downloading Carrefour prices')
        # opciones del driver
        opciones = Options()

        # quita la bandera de ser robot
        opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
        opciones.add_experimental_option('useAutomationExtension', False)

        # Trae la URL
        url = super_market_carrefour.url_scrapper

        # No me abre la ventana
        # opciones.add_argument("--headless")
        # opciones.add_argument("--disable-gpu")

        # Abre una ventana de chrome
        driver = webdriver.Chrome(PATH, options=opciones)

        driver.get(f'{url}{ean}')

        time.sleep(3)

        price = driver.find_element(By.CLASS_NAME, "ebx-result-price__value")

        price_num_str = price.text.strip().split()[0]
        price_num = float(price_num_str.replace(',', '.'))
        price_currency = price.text.strip().split()[1]

        if not price:
            raise Exception(f"Price not found for product '{product_added.id}' in Carrefour")

        ProductSuperRelationship.save_new_relation(price_num, price_currency, super_market_carrefour.id, product_added)


    @classmethod
    def extract_price_carrefour(cls, barcode):
        try:
            Supermarket.extract_and_save_data_carrefour(barcode)
            return True
        except Exception as e:
            logger.info('Este producto no se vende en Carrefour')
            return False

    @classmethod
    def save_product_alcampo(cls, product_name: str, product_url: str):
        supalca = Supermarket(
            product_name=product_name,
            product_url=product_url
        )

        session.add(supalca)
        session.commit()

    @classmethod
    def extract_and_save_data_alcampo(cls, ean, super_market_alcampo, product_added):
        logger.info('Downloading Alcampo prices')
        # opciones del driver
        opciones = Options()

        # quita la bandera de ser robot
        opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
        opciones.add_experimental_option('useAutomationExtension', False)

        # Trae la URL
        url = super_market_alcampo.url_scrapper

        # No me abre la ventana
        # opciones.add_argument("--headless")
        # opciones.add_argument("--disable-gpu")

        # Abre una ventana de chrome
        driver = webdriver.Chrome(PATH, options=opciones)

        driver.get(f'{url}{ean}')

        time.sleep(3)

        price = driver.find_element(By.CLASS_NAME, "long-price")
        price_num_str = price.text.strip().split()[0]
        price_num = float(price_num_str.replace(',', '.'))
        price_currency = price.text.strip().split()[1]

        if not price:
            raise Exception(f"Price not found for product '{product_added.id}' in Alcampo")

        ProductSuperRelationship.save_new_relation(price_num, price_currency, super_market_alcampo.id, product_added)

    @classmethod
    def extract_price_alcampo(cls, barcode):
        try:
            Supermarket.extract_and_save_data_alcampo(barcode)
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
