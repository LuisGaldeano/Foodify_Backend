from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup as bs
import requests as req
from selenium.webdriver.chrome.options import Options
from datetime import datetime

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
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def save_product_dia(cls, db: Session, ean: str, product_name: str, price_num: float, price_simbol: str,
                              product_url: str):
        supdia = Supermercado(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url,
            super='Dia'

        )

        db.add(supdia)
        db.commit()
        db.close()

    @classmethod
    def extract_data_dia(cls, db: Session, ean: str):
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
            cls.save_product_dia(db, ean, name, price_num, price_simbol, product_url)
            return True
        return False

    @classmethod
    def extract_price_dia(cls, db: Session, barcode):
        try:
            Supermercado.extract_data_dia(db, barcode)
            return True
        except Exception as e:
            print('Este producto no se vende en Dia')
            return False

    @classmethod
    def save_product_carrefour(cls, db: Session, ean: str, product_name: str, price_num: float, price_simbol: str,
                               product_url: str):
        supcarr = Supermercado(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url,
            super='Carrefour'
        )

        db.add(supcarr)
        db.commit()
        db.close()


    @classmethod
    def extract_data_carrefour(cls, db: Session, ean: str):
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

        time.sleep(4)

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
            cls.save_product_carrefour(db, ean, name, price_num, price_simbol, product_url)
            return True
        return False

    @classmethod
    def extract_price_carrefour(cls, db: Session, barcode):
        try:
            Supermercado.extract_data_carrefour(db, barcode)
            return True
        except Exception as e:
            print('Este producto no se vende en Carrefour')
            return False

    @classmethod
    def save_product_alcampo(cls, db: Session, ean: str, product_name: str, price_num: float, price_simbol: str,
                               product_url: str):
        supalca = Supermercado(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url,
            super='Alcampo'
        )

        db.add(supalca)
        db.commit()
        db.close()

    @classmethod
    def extract_data_alcampo(cls, db: Session, ean: str):
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
            cls.save_product_alcampo(db, ean, name, price_num, price_simbol, product_url)
            return True
        return False

    @classmethod
    def extract_price_alcampo(cls, db: Session, barcode):
        try:
            Supermercado.extract_data_alcampo(db, barcode)
            return True
        except Exception as e:
            print('Este producto no se vende en Alcampo')
            return False
