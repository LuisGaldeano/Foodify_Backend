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


class NewProductSchema(BaseModel):
    recurrent: bool
    units: int


class PrintShoppingList(BaseModel):
    name: str
    shop: str
    price: float
