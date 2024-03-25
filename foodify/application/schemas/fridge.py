from datetime import datetime

from pydantic import BaseModel


class FridgeBase(BaseModel):
    date_in: datetime
    date_out: datetime
    unit_actual: int
    product_name: str


class UpdateFridgeProduct(BaseModel):
    old_product_data: str
    new_product_data: str
