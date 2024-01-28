from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from application.database.database import Base, session
from core.logging import logger


class Brands(Base):
    __tablename__ = "brand"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)

    products = relationship("Products", back_populates="brands")

    def __str__(self):
        return f"id= {self.id} - name= {self.name}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def get_brand(cls, brand_data: str) -> object:
        """
        Given a brand name, select it from the database
        :param brand_data: brand name
        :return: brand object
        """
        selected_brand = session.query(Brands).filter(Brands.name == brand_data).first()
        return selected_brand

    @classmethod
    def save_brand(cls, brand_data: str) -> object:
        """
        Given a brand, save it in the database
        :param brand_data: brand name
        :return: Brand object
        """

        saved_brand = cls.get_brand(brand_data=brand_data)
        if not saved_brand:
            brand = Brands(name=brand_data)
            try:
                session.add(brand)
                session.commit()
                return brand
            except Exception as e:
                session.rollback()
                logger.info(f"The following exception occurred: {e}")
                return f"Brand '{brand_data}' has not been successfully saved."
        elif saved_brand:
            return saved_brand

    @classmethod
    def update_brand(cls, old_brand_data: str, new_brand_data: str) -> str:
        """
        Given the old brand name and the new one, update the brand's name
        :param old_brand_data: old brand name
        :param new_brand_data: new brand name
        """
        brand_to_update = session.query(Brands).filter(Brands.name == old_brand_data).first()

        if brand_to_update:
            try:
                brand_to_update.name = new_brand_data
                session.commit()
                return f"Brand '{old_brand_data}' updated to '{new_brand_data}' successfully."
            except Exception as e:
                session.rollback()
                logger.info(f"The following exception occurred: {e}")
                return f"Brand '{old_brand_data}' has not been successfully updated."
        else:
            return f"Brand '{old_brand_data}' not found."

    @classmethod
    def delete_brand(cls, brand_data: str) -> str:
        """
        Given a brand, delete it from the database
        :param brand_data: brand name
        """
        brand_to_delete = session.query(Brands).filter(Brands.name == brand_data).first()

        if brand_to_delete:
            try:
                session.delete(brand_to_delete)
                session.commit()
                return f"Brand '{brand_data}' deleted successfully."
            except Exception as e:
                session.rollback()
                logger.info(f"The following exception occurred: {e}")
                return f"Brand '{brand_data}' has not been successfully deleted."
        else:
            return f"Brand '{brand_data}' not found."
