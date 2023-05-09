from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.sql.expression import func
from models.products import Products
from database.database import session

PATH = ChromeDriverManager().install()  # instala driver de chrome


class SupAlca(Base):  # Supermercado Carrefour
    __tablename__ = 'supalca'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(255))
    price_num = Column(Float)
    price_simbol = Column(String(40))
    product_url = Column(String(255))

    ean_id = Column(BigInteger, ForeignKey("products.ean"))
    supalca = relationship("Products")

    def __str__(self):
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"


    @classmethod
    def offs_save_product_alca(cls, db: Session, ean: str, product_name: str, price_num: float, price_simbol: str, product_url: str):
        supalca = SupAlca(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url
        )

        db.add(supalca)
        db.commit()
        db.close()

    @classmethod
    def extract_data(cls, db: Session, ean: str):
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
            cls.offs_save_product_alca(db, ean, name, price_num, price_simbol, product_url)
            return True
        return False

    @classmethod
    def supalca_extract_price(cls, db: Session, barcode):
        try:
            reg = SupAlca.extract_data(session, barcode)
            if reg:
                product = session.query(Products).filter_by(ean=barcode).first()
                product.shop = func.concat(product.shop, 'alcampo')
                try:
                    # Confirmar los cambios en la sesión
                    session.commit()
                    print('Valor actualizado exitosamente en Alcampo.')
                except InvalidRequestError as e:
                    # Manejar errores
                    session.rollback()
                    print(f'Error al actualizar el valor: {str(e)}')
            else:
                print('No está en Alcampo')

        except Exception as e:
            print('No lo registro en Alcampo')
            print(e)