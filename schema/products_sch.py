from pydantic import BaseModel


class ProductsBase(BaseModel):
    ean: int
    name: str
    shop: str
    brand: str
    image: str
    nutriscore: str

    class Config:
        orm_mode = True
