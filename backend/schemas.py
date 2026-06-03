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


class MenuItemIn(BaseModel):
    numeProdus: str
    pret: float


class RestaurantCreate(BaseModel):
    nume: str
    specific: str
    buget: float
    locatie: str
    linkOficial: str | None = None
    imagine: str
    meniu: list[MenuItemIn]


class RestaurantUpdate(BaseModel):
    nume: str | None = None
    specific: str | None = None
    buget: float | None = None
    locatie: str | None = None
    linkOficial: str | None = None
    imagine: str | None = None
    meniu: list[MenuItemIn] | None = None


class AdminLoginIn(BaseModel):
    email: str
    password: str


class AdminLoginOut(BaseModel):
    token: str
    role: str
