from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from .database import Base, SessionLocal, engine
from .models import Restaurant
from .schemas import MenuItemOut, RestaurantDetailOut, RestaurantOut
from .seed_data import seed_database

app = FastAPI(
    title="Urban Plate REST API",
    version="1.0.0",
    description="API pentru cautare restaurante in Baia Mare",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def map_restaurant_summary(restaurant: Restaurant) -> RestaurantOut:
    return RestaurantOut(
        id=restaurant.id,
        slug=restaurant.slug,
        nume=restaurant.name,
        specific=restaurant.specific,
        buget=restaurant.avg_budget,
        locatie=restaurant.location,
        linkOficial=restaurant.official_link,
        imagine=restaurant.image,
    )

def map_restaurant_detail(restaurant: Restaurant) -> RestaurantDetailOut:
    return RestaurantDetailOut(
        **map_restaurant_summary(restaurant).model_dump(),
        meniu=[
            MenuItemOut(numeProdus=item.name, pret=item.price)
            for item in restaurant.menu_items
        ],
    )

@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/api/restaurants", response_model=list[RestaurantOut])
def list_restaurants(
    max_budget: float | None = Query(default=None, gt=0),
    specific: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[RestaurantOut]:
    statement = select(Restaurant).order_by(Restaurant.avg_budget.asc(), Restaurant.name.asc())

    if max_budget is not None:
        statement = statement.where(Restaurant.avg_budget <= max_budget)

    if specific:
        statement = statement.where(Restaurant.specific.ilike(f"%{specific.strip()}%"))

    if q:
        text_query = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Restaurant.name.ilike(text_query),
                Restaurant.location.ilike(text_query),
            )
        )

    statement = statement.limit(limit)
    restaurants = db.scalars(statement).all()
    return [map_restaurant_summary(restaurant) for restaurant in restaurants]

@app.get("/api/restaurants/{restaurant_slug}", response_model=RestaurantDetailOut)
def get_restaurant_by_slug(restaurant_slug: str, db: Session = Depends(get_db)) -> RestaurantDetailOut:
    statement = (
        select(Restaurant)
        .options(selectinload(Restaurant.menu_items))
        .where(Restaurant.slug == restaurant_slug)
    )
    restaurant = db.scalars(statement).first()

    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return map_restaurant_detail(restaurant)
