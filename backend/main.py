import secrets
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import inspect, or_, select, text
from sqlalchemy.orm import Session

from .auth_utils import generate_salt, hash_password, verify_password
from .database import Base, SessionLocal, engine
from .models import AuthToken, Favorite, Notification, Restaurant, RestaurantVisit, User, UserProfile
from .schemas import (
    AdminLoginIn, AdminLoginOut, FavoriteOut, HistoryOut, LoginIn, LoginOut,
    NotificationOut, ProfileOut, ProfileUpdateIn, RegisterIn, RestaurantCreate,
    RestaurantOut, RestaurantUpdate,
)
from .seed_data import build_slug, ensure_admin_user, seed_database

app = FastAPI(title="Urban Plate REST API", version="2.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
security = HTTPBearer(auto_error=False)


def migrate_restaurant_columns() -> None:
    columns = {column["name"] for column in inspect(engine).get_columns("restaurants")}
    with engine.begin() as connection:
        if "tags" not in columns:
            connection.execute(text("ALTER TABLE restaurants ADD COLUMN tags JSON"))
        if "menu_url" not in columns:
            connection.execute(text("ALTER TABLE restaurants ADD COLUMN menu_url VARCHAR(400)"))
        if "status" not in columns:
            connection.execute(text("ALTER TABLE restaurants ADD COLUMN status VARCHAR(30) DEFAULT 'active'"))
        if "official_link" not in columns and "website_url" in columns:
            connection.execute(text("ALTER TABLE restaurants ADD COLUMN official_link VARCHAR(400)"))
    visit_columns = {column["name"] for column in inspect(engine).get_columns("restaurant_visits")}
    if "accessed_at" not in visit_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE restaurant_visits ADD COLUMN accessed_at DATETIME"))
            connection.execute(text(
                "UPDATE restaurant_visits SET accessed_at = visited_at WHERE accessed_at IS NULL"
            ))


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    migrate_restaurant_columns()
    with SessionLocal() as db:
        seed_database(db)
        ensure_admin_user(db)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Autentificare necesara")
    token = db.scalar(select(AuthToken).where(AuthToken.token == credentials.credentials))
    user = db.get(User, token.user_id) if token else None
    if user is None:
        raise HTTPException(status_code=401, detail="Token invalid")
    return user


def current_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Acces rezervat administratorului")
    return user


def token_for(db: Session, user: User) -> str:
    token = secrets.token_urlsafe(32)
    db.add(AuthToken(token=token, user_id=user.id))
    db.commit()
    return token


def restaurant_out(restaurant: Restaurant) -> RestaurantOut:
    return RestaurantOut(
        id=restaurant.id, slug=restaurant.slug, nume=restaurant.name,
        specific=restaurant.specific, buget=restaurant.avg_budget,
        locatie=restaurant.location, imagine=restaurant.image,
        tags=restaurant.tags or [], website_url=restaurant.official_link,
        menu_url=restaurant.menu_url, status=restaurant.status or "active",
    )


def ensure_profile(db: Session, user: User) -> UserProfile:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.flush()
    return profile


def notify_restaurant_audience(db: Session, restaurant: Restaurant, message: str) -> None:
    history_ids = select(RestaurantVisit.user_id).where(RestaurantVisit.restaurant_id == restaurant.id)
    user_ids = set(db.scalars(history_ids).all())
    for user_id in user_ids:
        profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
        if profile is None or profile.notifications_enabled:
            db.add(Notification(
                user_id=user_id, restaurant_id=restaurant.id,
                title=f"Actualizare {restaurant.name}", message=message,
            ))


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/restaurants", response_model=list[RestaurantOut])
def list_restaurants(
    max_budget: float | None = Query(default=None, gt=0),
    specific: str | None = None,
    q: str | None = None,
    tag: str | None = None,
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[RestaurantOut]:
    statement = select(Restaurant).where(Restaurant.status == "active").order_by(
        Restaurant.avg_budget.asc(), Restaurant.name.asc()
    )
    if max_budget is not None:
        statement = statement.where(Restaurant.avg_budget <= max_budget)
    if specific:
        statement = statement.where(Restaurant.specific.ilike(f"%{specific.strip()}%"))
    if q:
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Restaurant.name.ilike(term), Restaurant.location.ilike(term)))
    restaurants = db.scalars(statement.limit(limit)).all()
    if tag:
        normalized = tag.strip().lower()
        restaurants = [item for item in restaurants if any(normalized in value.lower() for value in (item.tags or []))]
    return [restaurant_out(item) for item in restaurants]


@app.get("/api/restaurants/{restaurant_slug}", response_model=RestaurantOut)
def get_restaurant_by_slug(restaurant_slug: str, db: Session = Depends(get_db)) -> RestaurantOut:
    restaurant = db.scalar(select(Restaurant).where(Restaurant.slug == restaurant_slug))
    if restaurant is None or restaurant.status != "active":
        raise HTTPException(status_code=404, detail="Restaurantul nu a fost gasit")
    return restaurant_out(restaurant)


@app.post("/api/auth/register", response_model=LoginOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> LoginOut:
    email = payload.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Exista deja un cont cu acest email")
    salt = generate_salt()
    user = User(name=payload.name.strip(), email=email, password_salt=salt,
                password_hash=hash_password(payload.password, salt), role="client")
    db.add(user)
    db.flush()
    ensure_profile(db, user)
    db.commit()
    return LoginOut(token=token_for(db, user), role=user.role, name=user.name)


@app.post("/api/auth/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> LoginOut:
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user is None or not verify_password(payload.password, user.password_salt, user.password_hash):
        raise HTTPException(status_code=401, detail="Date de autentificare invalide")
    return LoginOut(token=token_for(db, user), role=user.role, name=user.name)


@app.get("/api/me", response_model=ProfileOut)
def get_profile(user: User = Depends(current_user), db: Session = Depends(get_db)) -> ProfileOut:
    profile = ensure_profile(db, user)
    db.commit()
    return ProfileOut(name=user.name, email=user.email, budget_limit=profile.budget_limit,
                      notifications_enabled=profile.notifications_enabled)


@app.put("/api/me", response_model=ProfileOut)
def update_profile(payload: ProfileUpdateIn, user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> ProfileOut:
    profile = ensure_profile(db, user)
    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.budget_limit is not None:
        profile.budget_limit = payload.budget_limit
    if payload.notifications_enabled is not None:
        profile.notifications_enabled = payload.notifications_enabled
    db.commit()
    return get_profile(user, db)


@app.get("/api/me/favorites", response_model=list[FavoriteOut])
def list_favorites(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[FavoriteOut]:
    rows = db.execute(select(Favorite, Restaurant).join(Restaurant).where(
        Favorite.user_id == user.id).order_by(Favorite.created_at.desc())).all()
    return [FavoriteOut(id=favorite.id, restaurant=restaurant_out(restaurant),
                        created_at=favorite.created_at) for favorite, restaurant in rows]


@app.post("/api/restaurants/{restaurant_id}/favorite", response_model=FavoriteOut, status_code=201)
def add_favorite(restaurant_id: int, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> FavoriteOut:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurantul nu a fost gasit")
    favorite = db.scalar(select(Favorite).where(Favorite.user_id == user.id,
                                                Favorite.restaurant_id == restaurant_id))
    if favorite is None:
        favorite = Favorite(user_id=user.id, restaurant_id=restaurant_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
    return FavoriteOut(id=favorite.id, restaurant=restaurant_out(restaurant),
                       created_at=favorite.created_at)


@app.delete("/api/restaurants/{restaurant_id}/favorite")
def remove_favorite(restaurant_id: int, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> dict[str, str]:
    favorite = db.scalar(select(Favorite).where(Favorite.user_id == user.id,
                                                Favorite.restaurant_id == restaurant_id))
    if favorite is None:
        raise HTTPException(status_code=404, detail="Restaurantul nu este la favorite")
    db.delete(favorite)
    db.commit()
    return {"status": "ok"}


@app.post("/api/restaurants/{restaurant_id}/access")
def record_official_access(restaurant_id: int, user: User = Depends(current_user),
                           db: Session = Depends(get_db)) -> dict[str, str]:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None or restaurant.status != "active":
        raise HTTPException(status_code=404, detail="Restaurantul nu a fost gasit")
    now = datetime.utcnow()
    db.add(RestaurantVisit(user_id=user.id, restaurant_id=restaurant_id,
                           visited_at=now, accessed_at=now))
    db.commit()
    return {"status": "recorded"}


@app.post("/api/restaurants/{restaurant_id}/visit")
def record_visit(restaurant_id: int, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> dict[str, str]:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None or restaurant.status != "active":
        raise HTTPException(status_code=404, detail="Restaurantul nu a fost gasit")
    now = datetime.utcnow()
    db.add(RestaurantVisit(user_id=user.id, restaurant_id=restaurant_id,
                           visited_at=now, accessed_at=now))
    db.commit()
    return {"status": "recorded"}


@app.get("/api/me/history", response_model=list[HistoryOut])
def get_history(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[HistoryOut]:
    rows = db.execute(select(RestaurantVisit, Restaurant).join(Restaurant).where(
        RestaurantVisit.user_id == user.id).order_by(RestaurantVisit.accessed_at.desc()).limit(100)).all()
    return [HistoryOut(id=visit.id, restaurant=restaurant_out(restaurant),
                       accessed_at=visit.accessed_at) for visit, restaurant in rows]


@app.get("/api/me/notifications", response_model=list[NotificationOut])
def get_notifications(user: User = Depends(current_user),
                      db: Session = Depends(get_db)) -> list[NotificationOut]:
    return [NotificationOut.model_validate(item, from_attributes=True) for item in db.scalars(
        select(Notification).where(Notification.user_id == user.id).order_by(
            Notification.created_at.desc()).limit(50)).all()]


@app.post("/api/me/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, user: User = Depends(current_user),
                           db: Session = Depends(get_db)) -> dict[str, str]:
    notification = db.scalar(select(Notification).where(
        Notification.id == notification_id, Notification.user_id == user.id))
    if notification is None:
        raise HTTPException(status_code=404, detail="Notificarea nu a fost gasita")
    notification.is_read = True
    db.commit()
    return {"status": "ok"}


def save_restaurant(db: Session, payload: RestaurantCreate, restaurant: Restaurant | None = None) -> Restaurant:
    if restaurant is None:
        restaurant = Restaurant(slug="", name="")
        db.add(restaurant)
    old_values = None if not restaurant.id else (
        restaurant.name, restaurant.specific, restaurant.avg_budget, restaurant.location,
        restaurant.image, restaurant.tags or [], restaurant.official_link,
        restaurant.menu_url, restaurant.status,
    )
    restaurant.name = payload.nume.strip()
    restaurant.slug = build_slug(restaurant.name) if not restaurant.id else restaurant.slug
    restaurant.specific = payload.specific.strip()
    restaurant.avg_budget = payload.buget
    restaurant.location = payload.locatie.strip()
    restaurant.image = payload.imagine.strip()
    restaurant.tags = [tag.strip() for tag in payload.tags if tag.strip()]
    restaurant.official_link = payload.website_url
    restaurant.menu_url = payload.menu_url
    restaurant.status = payload.status
    if old_values is not None:
        new_values = (
            restaurant.name, restaurant.specific, restaurant.avg_budget, restaurant.location,
            restaurant.image, restaurant.tags or [], restaurant.official_link,
            restaurant.menu_url, restaurant.status,
        )
        if old_values != new_values:
            budget_changed = old_values[2] != new_values[2]
            detail = f"bugetul mediu la {restaurant.avg_budget:g} RON" if budget_changed else "ofertele și detaliile"
            notify_restaurant_audience(
                db, restaurant,
                f"Restaurantul {restaurant.name} și-a actualizat {detail}!",
            )
    return restaurant


@app.post("/api/admin/login", response_model=AdminLoginOut)
def admin_login(payload: AdminLoginIn, db: Session = Depends(get_db)) -> AdminLoginOut:
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user is None or user.role != "admin" or not verify_password(payload.password, user.password_salt, user.password_hash):
        raise HTTPException(status_code=401, detail="Date de autentificare invalide")
    return AdminLoginOut(token=token_for(db, user), role=user.role)


@app.post("/api/admin/restaurants", response_model=RestaurantOut)
def create_restaurant(payload: RestaurantCreate, _: User = Depends(current_admin),
                      db: Session = Depends(get_db)) -> RestaurantOut:
    restaurant = save_restaurant(db, payload)
    db.flush()
    restaurant.slug = build_slug(restaurant.name)
    db.commit()
    db.refresh(restaurant)
    return restaurant_out(restaurant)


@app.put("/api/admin/restaurants/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(restaurant_id: int, payload: RestaurantUpdate, _: User = Depends(current_admin),
                      db: Session = Depends(get_db)) -> RestaurantOut:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurantul nu a fost gasit")
    save_restaurant(db, payload, restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant_out(restaurant)


@app.delete("/api/admin/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int, _: User = Depends(current_admin),
                      db: Session = Depends(get_db)) -> dict[str, str]:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurantul nu a fost gasit")
    db.delete(restaurant)
    db.commit()
    return {"status": "ok"}
