from pydantic import BaseModel, ConfigDict


class MenuItemOut(BaseModel):
    numeProdus: str
    pret: float


class RestaurantOut(BaseModel):
    id: int
    slug: str
    nume: str
    specific: str
    buget: float
    locatie: str
    linkOficial: str | None = None
    imagine: str

    model_config = ConfigDict(from_attributes=True)


class RestaurantDetailOut(RestaurantOut):
    meniu: list[MenuItemOut]
