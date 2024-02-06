from datetime import datetime
from sqlalchemy import BigInteger, Column, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship
from application.database.database import Base
from application.models import Supermarket
from application.models.products import Products
from core.logging import logger


class Fridge(Base):
    __tablename__ = "fridge"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_in = Column(Date, default=datetime.utcnow)
    date_out = Column(Date)
    unit_actual = Column(Integer)

    product_id = Column(BigInteger, ForeignKey("products.id"))
    products = relationship("Products", back_populates="fridge")

    def __str__(self):
        return f"id= {self.id}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def save_fridge_product(cls, db, product_added: object) -> None:
        try:
            unit_actual = db.query(Fridge.unit_actual).filter(Fridge.product_id == product_added.id) \
                .order_by(Fridge.id.desc()).limit(1).scalar()
            units_per_package = db.query(Products.unit_packaging).filter(Products.id == product_added.id).scalar()
            if unit_actual is None:
                new_unit_actual = units_per_package
            else:
                new_unit_actual = unit_actual + units_per_package

            fridge_entry = Fridge(product_id=product_added.id, unit_actual=new_unit_actual)

            db.add(fridge_entry)
            db.commit()
            logger.info("Saved in fridge")
        except Exception as e:
            db.rollback()
            logger.info(f"The following exception occurred: {e}")

    @classmethod
    def get_fridge_products(cls, db):
        all_products_in_fridge = db.query(Fridge).all()
        products = []
        for product_in_fridge in all_products_in_fridge:
            name = db.query(Products.name).filter(Products.id == product_in_fridge.product_id).first()
            date_in = product_in_fridge.date_in
            unit_actual = product_in_fridge.unit_actual
            if unit_actual != 0:
                product_data = {
                    "name": name[0],
                    "unit_actual": unit_actual,
                    "date_in": date_in.isoformat()
                }
                products.append(product_data)
        return products

    @classmethod
    def update_fridge_products(cls, db, old_product_data: str, new_product_data: str) -> str:
        """
        Given the old product name and the new one, update the product's name
        :param old_product_data: old supermarket name
        :param new_product_data: new supermarket name
        """
        product_to_update = db.query(Products).filter(Products.name == old_product_data).first()
        if product_to_update:
            try:
                product_to_update.name = new_product_data
                db.commit()
                return f"Supermarket '{old_product_data}' updated to '{new_product_data}' successfully."
            except Exception as e:
                db.rollback()
                logger.info(f"The following exception occurred: {e}")
                return f"Supermarket '{old_product_data}' has not been successfully updated."
        else:
            return f"Supermarket '{old_product_data}' not found."

    @classmethod
    def delete_fridge_product(cls, db, product_data: str) -> str:
        """
        Given a , fridge_product delete it from the database
        :param supermarket_data: supermarket name
        """
        product_to_delete = db.query(Supermarket).filter(Supermarket.name == product_data).first()

        if product_to_delete:
            try:
                db.delete(product_to_delete)
                db.commit()
                return f"Supermarket '{product_data}' deleted successfully."
            except Exception as e:
                db.rollback()
                logger.info(f"The following exception occurred: {e}")
                return f"Supermarket '{product_data}' has not been successfully deleted."
        else:
            return f"Supermarket '{product_data}' not found."
