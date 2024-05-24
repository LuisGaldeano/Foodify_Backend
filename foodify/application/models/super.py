import os
import time

import requests as req
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from webdriver_manager.firefox import GeckoDriverManager

from application.database.database import Base
from application.models.product_super_relationship import ProductSuperRelationship
from core.logging import logger


def download_path():
    try:
        PATH = GeckoDriverManager().install()
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)
        return PATH
    except Exception as e:
        print(f"Error al obtener la versión de GeckoDriver: {e}")
    finally:
        if "driver" in locals():
            logger.info("Removing driver")
            driver.quit()


PATH = download_path()  # TODO REVIEW THIS


class Supermarket(Base):  # Supermercado Día
    DIA, CARREFOUR, ALCAMPO = "dia", "carrefour", "alcampo"
    AVAILABLE_SUPERS = [
        (DIA, "Dia"),
        (CARREFOUR, "Carrefour"),
        (ALCAMPO, "Alcampo"),
    ]
    __tablename__ = "supermarket"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(ChoiceType(AVAILABLE_SUPERS))
    url_scrapper = Column(String(255))
    url_chart = Column(String(255))

    shoppinglists = relationship("ShoppingList", back_populates="supers")

    productsuprel = relationship("ProductSuperRelationship", back_populates="supers")

    def __str__(self):
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def get_supermarket(cls, db, super_data: str) -> object:
        supermarket = db.query(Supermarket).filter_by(name=super_data).first()
        return supermarket

    @classmethod
    def save_supermarket(
        cls, db, super_data: str, url_scrapper: str, url_cart: str
    ) -> object:
        """
        Given a super, save it in the database
        :param super_data: super name
        :param url_scrapper: supermarket's scrapper url
        :param url_cart: supermarket's cart url
        :return: supermarket object
        """
        saved_supermarket = cls.get_supermarket(super_data=super_data, db=db)
        if not saved_supermarket:
            supermarket = Supermarket(
                name=super_data, url_scrapper=url_scrapper, url_chart=url_cart
            )
            try:
                db.add(supermarket)
                db.commit()
                return supermarket
            except Exception as e:
                db.rollback()
                logger.info(f"The following exception occurred: {e}")
                return f"Supermarket '{super_data}' has not been successfully saved."
        elif saved_supermarket:
            return saved_supermarket

    @classmethod
    def update_supermarket(
        cls, db, old_supermarket_data: str, new_supermarket_data: str
    ) -> str:
        """
        Given the old supermarket name and the new one, update the supermarket's name
        :param old_supermarket_data: old supermarket name
        :param new_supermarket_data: new supermarket name
        """
        supermarket_to_update = (
            db.query(Supermarket).filter(Supermarket.name == old_supermarket_data).first()
        )
        if supermarket_to_update:
            try:
                supermarket_to_update.name = new_supermarket_data
                db.commit()
                return f"Supermarket '{old_supermarket_data}' updated to '{new_supermarket_data}' successfully."
            except Exception as e:
                db.rollback()
                logger.info(f"The following exception occurred: {e}")
                return f"Supermarket '{old_supermarket_data}' has not been successfully updated."
        else:
            return f"Supermarket '{old_supermarket_data}' not found."

    @classmethod
    def delete_supermarket(cls, db, supermarket_data: str) -> str:
        """
        Given a supermarket, delete it from the database
        :param supermarket_data: supermarket name
        """
        supermarket_to_delete = (
            db.query(Supermarket).filter(Supermarket.name == supermarket_data).first()
        )

        if supermarket_to_delete:
            try:
                db.delete(supermarket_to_delete)
                db.commit()
                return f"Supermarket '{supermarket_data}' deleted successfully."
            except Exception as e:
                db.rollback()
                logger.info(f"The following exception occurred: {e}")
                return (
                    f"Supermarket '{supermarket_data}' has not been successfully deleted."
                )
        else:
            return f"Supermarket '{supermarket_data}' not found."

    @classmethod
    def extract_prices_supermarkets(cls, db, ean, product_added):
        """
        Extrae los precios de los supermercados disponibles mediante web scraping
        para un determinado código EAN de producto.

        :param ean: El código EAN del producto.
        :param product_added: El producto agregado a la lista.
        :return: None
        """
        # Para cada supermercado en la lista de supermercados disponibles hago web scrapping
        for supermarket, _ in cls.AVAILABLE_SUPERS:
            if supermarket == cls.DIA:
                # Get or create super and return a super object
                url_dia = os.getenv("DIA_URL")
                url_chart_dia = os.getenv("DIA_URL_CHART")
                super_market_dia = cls.save_supermarket(
                    db=db,
                    super_data=cls.DIA,
                    url_scrapper=url_dia,
                    url_cart=url_chart_dia,
                )

                # Intenta descargar los precios mediante web strapping
                try:
                    Supermarket.extract_and_save_data_dia(
                        ean=ean,
                        super_market_dia=super_market_dia,
                        product_added=product_added,
                    )
                except Exception as e:
                    logger.exception("Este producto no se vende en Dia.")
                    logger.exception(f"Exception {e}")

            if supermarket == cls.CARREFOUR:
                # Get or create super and return a super object
                url_carrefour = os.getenv("CARREFOUR_URL")
                url_chart_carrefour = os.getenv("CARREFOUR_URL_CHART")
                super_market_carrefour = cls.save_supermarket(
                    db=db,
                    super_data=cls.CARREFOUR,
                    url_scrapper=url_carrefour,
                    url_cart=url_chart_carrefour,
                )

                try:
                    Supermarket.extract_and_save_data_carrefour(
                        ean=ean,
                        super_market_carrefour=super_market_carrefour,
                        product_added=product_added,
                    )
                except Exception as e:
                    logger.exception("Este producto no se vende en Carrefour")
                    logger.exception(f"Exception {e}")

            if supermarket == cls.ALCAMPO:
                # Get or create super and return a super object
                url_alcampo = os.getenv("ALCAMPO_URL")
                url_chart_alcampo = os.getenv("ALCAMPO_URL_CHART")
                super_market_alcampo = cls.save_supermarket(
                    db=db,
                    super_data=cls.ALCAMPO,
                    url_scrapper=url_alcampo,
                    url_cart=url_chart_alcampo,
                )

                try:
                    Supermarket.extract_and_save_data_alcampo(
                        ean=ean,
                        super_market_alcampo=super_market_alcampo,
                        product_added=product_added,
                    )
                except Exception as e:
                    logger.exception("Este producto no se vende en Carrefour")
                    logger.exception(f"Exception {e}")

    @classmethod
    def extract_and_save_data_dia(cls, ean: int, super_market_dia, product_added):
        """
        Extrae y guarda los datos de precios del supermercado Día para un determinado código EAN de producto.

        :param ean: El código EAN del producto.
        :param super_market_dia: El objeto Supermarket correspondiente al supermercado Día.
        :param product_added: El producto agregado a la lista.
        :raises Exception: Si no se encuentra el precio del producto en el supermercado Día.
        :return: None
        """
        logger.info("Downloading Dia prices")
        try:
            ean = str(ean)

            # Extract the prices using beautiful soup
            html = req.get(super_market_dia.url_scrapper + ean).text
            sopa = bs(html, "html.parser")

            # Devuelve el precio
            price = sopa.find("p", class_="search-product-card__active-price")
            price_num_str = price.text.strip().split()[0]
            price_num = float(price_num_str.replace(",", "."))
            price_currency = price_num_str[1]

            if not price:
                raise Exception(
                    f"Price not found for product '{product_added.id}' in Dia"
                )

            ProductSuperRelationship.save_new_relation(
                price_num, price_currency, super_market_dia.id, product_added
            )
        except Exception as ex:
            logger.exception(f"Exception {ex}")
            raise Exception(f"El producto '{product_added.id}' no se vende en Día")

    @classmethod
    def extract_and_save_data_carrefour(
        cls, ean: str, super_market_carrefour, product_added
    ):
        """
        Extrae y guarda los datos de precios del supermercado Carrefour para un determinado código EAN de producto.

        :param ean: El código EAN del producto.
        :param super_market_carrefour: El objeto Supermarket correspondiente al supermercado Carrefour.
        :param product_added: El producto agregado a la lista.
        :raises Exception: Si no se encuentra el precio del producto en el supermercado Carrefour.
        :return: None
        """
        logger.info("Downloading Carrefour prices")
        # opciones del driver
        opciones = Options()

        # quita la bandera de ser robot
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option("useAutomationExtension", False)

        # Trae la URL
        url = super_market_carrefour.url_scrapper

        # No me abre la ventana
        # opciones.add_argument("--headless")
        # opciones.add_argument("--disable-gpu")

        # Abre una ventana de chrome
        driver = webdriver.Chrome(PATH, options=opciones)

        driver.get(f"{url}{ean}")

        time.sleep(3)

        price = driver.find_element(By.CLASS_NAME, "ebx-result-price__value")

        price_num_str = price.text.strip().split()[0]
        price_num = float(price_num_str.replace(",", "."))
        price_currency = price.text.strip().split()[1]

        if not price:
            raise Exception(
                f"Price not found for product '{product_added.id}' in Carrefour"
            )

        ProductSuperRelationship.save_new_relation(
            price_num, price_currency, super_market_carrefour.id, product_added
        )

    @classmethod
    def extract_and_save_data_alcampo(cls, ean, super_market_alcampo, product_added):
        """
        Extrae y guarda los datos de precios del supermercado Alcampo para un determinado código EAN de producto.

        :param ean: El código EAN del producto.
        :param super_market_alcampo: El objeto Supermarket correspondiente al supermercado Alcampo.
        :param product_added: El producto agregado a la lista.
        :raises Exception: Si no se encuentra el precio del producto en el supermercado Alcampo.
        :return: None
        """
        logger.info("Downloading Alcampo prices")
        # opciones del driver
        opciones = Options()

        # quita la bandera de ser robot
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option("useAutomationExtension", False)

        # Trae la URL
        url = super_market_alcampo.url_scrapper

        # No me abre la ventana
        # opciones.add_argument("--headless")
        # opciones.add_argument("--disable-gpu")

        # Abre una ventana de chrome
        driver = webdriver.Chrome(PATH, options=opciones)

        driver.get(f"{url}{ean}")

        time.sleep(3)

        price = driver.find_element(By.CLASS_NAME, "long-price")
        price_num_str = price.text.strip().split()[0]
        price_num = float(price_num_str.replace(",", "."))
        price_currency = price.text.strip().split()[1]

        if not price:
            raise Exception(
                f"Price not found for product '{product_added.id}' in Alcampo"
            )

        ProductSuperRelationship.save_new_relation(
            price_num, price_currency, super_market_alcampo.id, product_added
        )
