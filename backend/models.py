from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    specific: Mapped[str] = mapped_column(String(120), index=True)
    avg_budget: Mapped[float] = mapped_column(Float, index=True)
    location: Mapped[str] = mapped_column(String(200), index=True)
    official_link: Mapped[str | None] = mapped_column(String(300), nullable=True)
    image: Mapped[str] = mapped_column(String(400))

    menu_items: Mapped[list["MenuItem"]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    price: Mapped[float] = mapped_column(Float)
    
    restaurant: Mapped[Restaurant] = relationship(back_populates="menu_items")
