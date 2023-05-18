from datetime import datetime
from database.database import Base, session
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Float, DateTime
from sqlalchemy.orm import relationship


class Fridge(Base):
    __tablename__ = 'fridge'
    fridge_id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)

    ean_id = Column(BigInteger, ForeignKey("products.ean"))
    fridge = relationship("Products")

    def __str__(self):
        return f"id= {self.fridge_id}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def fridge_save_product(cls, product_data: dict):
        product = Fridge(
            ean_id=product_data['code'],

        )

        session.add(product)
        session.commit()
        session.close()
