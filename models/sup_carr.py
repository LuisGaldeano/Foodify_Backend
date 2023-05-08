from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options

PATH = ChromeDriverManager().install()  # instala driver de chrome


class SupCarr(Base):  # Supermercado Carrefour
    __tablename__ = 'supcarr'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(255))
    price_num = Column(Float)
    price_simbol = Column(String(40))
    product_url = Column(String(255))

    ean_id = Column(BigInteger, ForeignKey("products.ean"))
    supcarr = relationship("Products")

    def __str__(self):
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"


    @classmethod
    def offs_save_product_carr(cls, db: Session, ean: str, product_name: str, price_num: float, price_simbol: str, product_url: str):
        supcarr = SupCarr(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url
        )

        db.add(supcarr)
        db.commit()
        db.close()

    @classmethod
    def extract_data(cls,db: Session, ean: str):
        # opciones del driver
        opciones = Options()

        # quita la bandera de ser robot
        opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
        opciones.add_experimental_option('useAutomationExtension', False)

        # No me abre la ventana
        opciones.add_argument("--headless")
        opciones.add_argument("--disable-gpu")

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
            cls.offs_save_product_carr(db, ean, name, price_num, price_simbol, product_url)
            return True
        return False





