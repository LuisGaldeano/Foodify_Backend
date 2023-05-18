from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class ShoppingList(Base):  # Supermercado Día
    __tablename__ = 'shoppingList'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(255))
    price_num = Column(Float)
    price_simbol = Column(String(40))
    product_url = Column(String(255))
    date = Column(DateTime, default=datetime.utcnow)
    super = Column(String(255))

    ean_id = Column(BigInteger, ForeignKey("products.ean"))
    # product = relationship("Products", back_populates="shopping_list")

    def __str__(self):
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"