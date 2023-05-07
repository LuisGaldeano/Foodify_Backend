from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
import requests as req
from bs4 import BeautifulSoup as bs


class SupDia(Base):  # Supermercado Día
    __tablename__ = 'supdia'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(255))
    price_num = Column(Float)
    price_simbol = Column(String(40))
    product_url = Column(String(255))

    ean_id = Column(BigInteger, ForeignKey("products.ean"))
    supdia = relationship("Products")

    def __str__(self):
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def offs_save_product_dia(cls, db: Session, ean: str, product_name: str, price_num: float, price_simbol: str, product_url: str):
        supdia = SupDia(
            ean_id=ean,
            product_name=product_name,
            price_num=price_num,
            price_simbol=price_simbol,
            product_url=product_url
        )

        db.add(supdia)
        db.commit()
        db.close()

    @classmethod
    def extract_data(cls,db: Session, ean: str):
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
            cls.offs_save_product_dia(db, ean, name, price_num, price_simbol, product_url)
            return True
        return False

