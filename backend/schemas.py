from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RestaurantOut(BaseModel):
    id: int
    slug: str
    nume: str
    specific: str
    buget: float
    locatie: str
    imagine: str
    tags: list[str]
    website_url: str | None
    menu_url: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class RestaurantCreate(BaseModel):
    nume: str = Field(min_length=2, max_length=150)
    specific: str = Field(min_length=2, max_length=120)
    buget: float = Field(gt=0)
    locatie: str = Field(min_length=2, max_length=200)
    imagine: str = Field(min_length=1, max_length=400)
    tags: list[str] = Field(default_factory=list, max_length=20)
    website_url: str | None = Field(default=None, max_length=400)
    menu_url: str | None = Field(default=None, max_length=400)
    status: str = Field(default="active", pattern="^(active|inactive)$")


class RestaurantUpdate(RestaurantCreate):
    pass


class AdminLoginIn(BaseModel):
    email: str
    password: str


class AdminLoginOut(BaseModel):
    token: str
    role: str


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: str
    password: str


class LoginOut(BaseModel):
    token: str
    role: str
    name: str


class ProfileOut(BaseModel):
    name: str
    email: str
    budget_limit: float | None
    notifications_enabled: bool


class ProfileUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    budget_limit: float | None = Field(default=None, gt=0)
    notifications_enabled: bool | None = None


class FavoriteOut(BaseModel):
    id: int
    restaurant: RestaurantOut
    created_at: datetime


class HistoryOut(BaseModel):
    id: int
    restaurant: RestaurantOut
    accessed_at: datetime


class NotificationOut(BaseModel):
    id: int
    restaurant_id: int | None
    title: str
    message: str
    is_read: bool
    created_at: datetime
