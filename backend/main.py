import secrets

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from .auth_utils import verify_password
from .database import Base, SessionLocal, engine
from .models import AuthToken, MenuItem, Restaurant, User
from .schemas import (
    AdminLoginIn,
    AdminLoginOut,
    MenuItemOut,
    RestaurantCreate,
    RestaurantDetailOut,
    RestaurantOut,
    RestaurantUpdate,
)
from .seed_data import build_slug, ensure_admin_user, seed_database

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
        ensure_admin_user(db)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


security = HTTPBearer(auto_error=False)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing admin token")

    statement = (
        select(AuthToken)
        .options(selectinload(AuthToken.user))
        .where(AuthToken.token == credentials.credentials)
    )
    token_row = db.scalars(statement).first()

    if token_row is None or token_row.user is None:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    if token_row.user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return token_row.user

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


def ensure_unique_slug(db: Session, base_slug: str, exclude_id: int | None = None) -> str:
    if not base_slug:
        base_slug = secrets.token_hex(4)

    candidate = base_slug
    suffix = 1
    while True:
        statement = select(Restaurant.id).where(Restaurant.slug == candidate)
        if exclude_id is not None:
            statement = statement.where(Restaurant.id != exclude_id)
        if db.scalar(statement) is None:
            break
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
    return candidate


def apply_menu_items(restaurant: Restaurant, items: list[dict[str, float | str]]) -> None:
    restaurant.menu_items.clear()
    for item in items:
        restaurant.menu_items.append(
            MenuItem(
                name=str(item["numeProdus"]).strip(),
                price=float(item["pret"]),
            )
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


@app.post("/api/admin/login", response_model=AdminLoginOut)
def admin_login(payload: AdminLoginIn, db: Session = Depends(get_db)) -> AdminLoginOut:
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user is None or user.role != "admin":
        raise HTTPException(status_code=401, detail="Date de autentificare invalide")

    if not verify_password(payload.password, user.password_salt, user.password_hash):
        raise HTTPException(status_code=401, detail="Date de autentificare invalide")

    token_value = secrets.token_urlsafe(32)
    db.add(AuthToken(token=token_value, user_id=user.id))
    db.commit()

    return AdminLoginOut(token=token_value, role=user.role)


@app.post("/api/admin/logout")
def admin_logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing admin token")

    deleted = db.query(AuthToken).filter(AuthToken.token == credentials.credentials).delete()
    db.commit()

    if deleted == 0:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    return {"status": "ok"}


@app.post("/api/admin/restaurants", response_model=RestaurantDetailOut)
def create_restaurant(
    payload: RestaurantCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> RestaurantDetailOut:
    slug = ensure_unique_slug(db, build_slug(payload.nume))
    restaurant = Restaurant(
        slug=slug,
        name=payload.nume.strip(),
        specific=payload.specific.strip(),
        avg_budget=float(payload.buget),
        location=payload.locatie.strip(),
        official_link=payload.linkOficial,
        image=payload.imagine.strip(),
    )

    apply_menu_items(restaurant, [item.model_dump() for item in payload.meniu])
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return map_restaurant_detail(restaurant)


@app.put("/api/admin/restaurants/{restaurant_id}", response_model=RestaurantDetailOut)
def update_restaurant(
    restaurant_id: int,
    payload: RestaurantUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> RestaurantDetailOut:
    restaurant = db.scalars(
        select(Restaurant)
        .options(selectinload(Restaurant.menu_items))
        .where(Restaurant.id == restaurant_id)
    ).first()

    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if payload.nume is not None:
        restaurant.name = payload.nume.strip()
        restaurant.slug = ensure_unique_slug(db, build_slug(restaurant.name), exclude_id=restaurant.id)

    if payload.specific is not None:
        restaurant.specific = payload.specific.strip()

    if payload.buget is not None:
        restaurant.avg_budget = float(payload.buget)

    if payload.locatie is not None:
        restaurant.location = payload.locatie.strip()

    if payload.linkOficial is not None:
        restaurant.official_link = payload.linkOficial

    if payload.imagine is not None:
        restaurant.image = payload.imagine.strip()

    if payload.meniu is not None:
        apply_menu_items(restaurant, [item.model_dump() for item in payload.meniu])

    db.commit()
    db.refresh(restaurant)

    return map_restaurant_detail(restaurant)


@app.delete("/api/admin/restaurants/{restaurant_id}")
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> dict[str, str]:
    restaurant = db.scalar(select(Restaurant).where(Restaurant.id == restaurant_id))
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    db.delete(restaurant)
    db.commit()
    return {"status": "ok"}
