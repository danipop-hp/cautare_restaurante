import re
import unicodedata
from urllib.parse import quote_plus

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import MenuItem, Restaurant

IMAGES = {
    "restaurant": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
    "fastFood": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
    "cafe": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=900&q=80",
    "pub": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=900&q=80",
    "desert": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=900&q=80",
    "hotel": "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=900&q=80",
    "steak": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=900&q=80",
}

RENAMES = {
    "LAncora": "L' Ancora",
    "LUlivo": "Restaurant L'Ulivo",
    "Restaurant LUlivo": "Restaurant L'Ulivo",
    "B owl by DorDePulpa": "B-owl by #DorDePulpa",
    "CASA DOBRO": "Casa Dobro",
    "Casa Crisan": "Crisan House",
    "Terasa Millennium": "Restaurant Millennium",
    "Centrul de evenimente GHR": "GHR Evenimente - Ghitta Hotel Restaurant",
    "Philia Events": "OAZIS PHILIA",
    "PizzaBaiaMarero": "PizzaBaiaMare.ro",
    "Rivulus Cafe": "Hotel Rivulus",
    "PIT STOP": "PIT STOP PIZZA",
    "La Sueta": "La Sueta Resurrection",
    "Restaurant Crenguta": "Restaurant Crenguta",
    "Spartan Restaurant": "Spartan Baia Mare",
    "Budapesta": "Restaurant Budapesta",
    "KFC": "KFC Baia Mare Vivo!",
    "KFC Value Centre": "KFC Baia Mare Value Center",
    "Sahara": "Sahara Pub",
    "Shadows Rock Bar": "Rockwave Tavern",
    "Sport Bar Artemis": "Artemis Bar",
    "Cafe Bar URSUS": "Cafe-Bar URSUS",
    "UpFlour": "Porto",
}

SOURCE_LOCATIONS = [
    "Acacia-Baia-Mare",
    "Andana-Pan-Baia-Mare",
    "Art-Cafe-Bar-Baia-Mare",
    "Bar-13-Baia-Mare",
    "Bar-Acasuca-Baia-Mare",
    "Barbarossa-Baia-Mare",
    "Bastion-Baia-Mare",
    "Bizo-Baia-Mare",
    "BOHO-Brasserie-Baia-Mare",
    "B-owl-by-DorDePulpa-Baia-Mare",
    "BRO-Restaurant-Baia-Mare",
    "Budapesta-Baia-Mare",
    "Buonissimo-Baia-Mare",
    "Cafe-Bar-URSUS-Baia-Mare",
    "Casa-Crisan-Baia-Mare",
    "CASA-DOBRO-Baia-Mare",
    "Castel-Transilvania-Baia-Mare",
    "Centrul-de-evenimente-GHR-Baia-Mare",
    "Cinquecento-Baia-Mare",
    "Cocktail-Mobile-Bar-Baia-Mare",
    "College-Pub-Baia-Mare",
    "Contiline-Club-Baia-Mare",
    "Damas-arabic-food-Baia-Mare",
    "Eben-Ezer-Baia-Mare",
    "Family-Restaurant-Baia-Mare",
    "Flavours-Baia-Mare-2",
    "FreshPlus-Baia-Mare",
    "Greenys-Baia-Mare",
    "Heaven-Juice-and-Smoothie-Bar-Baia-Mare",
    "Hotel-Europa-Baia-Mare-Baia-Mare",
    "Hotel-Mara-Baia-Mare",
    "Il-Padrino-Baia-Mare-3",
    "Karaffe-Baia-Mare",
    "KFC-Baia-Mare",
    "KFC-Value-Centre-Baia-Mare",
    "La-Creperie-Baia-Mare",
    "La-Cucina-Baia-Mare",
    "La-Gourmet-Baia-Mare",
    "La-Mircea-Baia-Mare",
    "LAncora-Baia-Mare",
    "La-Sueta-Baia-Mare",
    "La-Tour-Baia-Mare-Baia-Mare",
    "Le-Bistrot-Baia-Mare",
    "Log-Out-Baia-Mare",
    "Lumiere-Baia-Mare",
    "MOKI-Cafe-Baia-Mare",
    "Never-Old-Cafe-Bar-Baia-Mare",
    "Office-Pub-Baia-Mare-2",
    "Orient-Turkish-Bistro-Baia-Mare",
    "Pasta-Fresca-Baia-Mare-Baia-Mare",
    "Pastuccis-Pasta-Bar-Baia-Mare",
    "Peperosso-Baia-Mare",
    "Philia-Events-Baia-Mare",
    "Pick-up-Narghila-Baia-Mare-Baia-Mare",
    "PIT-STOP-Baia-Mare",
    "Pizza-Albina-Baia-Mare",
    "PizzaBaiaMarero-Baia-Mare",
    "Pizza-Buna-Pizza-Rimmini-Baia-Mare",
    "Pizza-Grande-Napoli-Baia-Mare",
    "Pizza-H-Baia-Mare",
    "Pizzeria-Colosseo-Baia-Mare",
    "Placintarie-Baia-Mare",
    "PRESSCO-Baia-Mare",
    "Rapido-Baia-Mare",
    "Restaurant-Crenguta-Baia-Mare",
    "Restaurant-LUlivo-Baia-Mare",
    "Restaurant-Michael-Pascale-Baia-Mare",
    "Restaurant-Parc-Athos-Baia-Mare",
    "Restaurant-Saffiya-Baia-Mare",
    "Restaurant-Tasty-Baia-Mare",
    "Rivulus-Cafe-Baia-Mare-2",
    "ROCCA-PUB-Baia-Mare-2",
    "Rustika-Baia-Mare",
    "Sahara-Baia-Mare",
    "Scottish-Pub-Baia-Mare",
    "Shadows-Rock-Bar-Baia-Mare",
    "Smart-Food-Baia-Mare",
    "Spartan-Restaurant-Baia-Mare",
    "Speedy-Fast-Food-Baia-Mare",
    "Sport-Bar-Artemis-Baia-Mare",
    "Supreme-Burger-Baia-Mare",
    "Terasa-Millennium-Baia-Mare-2",
    "The-Buffet-Baia-Mare",
    "The-Oak-Baia-Mare",
    "Tom-and-Jerry-Baia-Mare",
    "UpFlour-Baia-Mare",
    "vh-residence-Baia-Mare",
    "Vintage-Bar-Baia-Mare",
    "Zen-Lounge-Baia-Mare",
    "Zoom-Pub-Baia-Mare",
    {"nume": "Butcher's", "specific": "Steakhouse & grill", "buget": 120, "locatie": "Bd. Unirii 16, Baia Mare", "imagine": IMAGES["steak"], "cheie": "steak"},
    {"nume": "La Pastorel", "specific": "Romanesc", "buget": 70, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Riviera", "specific": "International & events", "buget": 100, "locatie": "Bd. Republicii 46, Baia Mare", "imagine": IMAGES["hotel"], "cheie": "hotel"},
    {"nume": "Mado Baia Mare", "specific": "Fast food", "buget": 45, "locatie": "Baia Mare", "imagine": IMAGES["fastFood"], "cheie": "fastFood"},
    {"nume": "Gigi", "specific": "Brunch & cafea", "buget": 30, "locatie": "Baia Mare", "imagine": IMAGES["cafe"], "cheie": "cafe"},
    {"nume": "ChocolArt Cake Factory", "specific": "Cofetarie artizanala", "buget": 30, "locatie": "Baia Mare", "imagine": IMAGES["desert"], "cheie": "desert"},
    {"nume": "Nomad Cafe", "specific": "Cafea de specialitate", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["cafe"], "cheie": "cafe"},
    {"nume": "Rox - Specialty Coffee -", "specific": "Cafea de specialitate", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["cafe"], "cheie": "cafe"},
    {"nume": "Mazo", "specific": "Brunch & coffee", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["cafe"], "cheie": "cafe"},
    {"nume": "Cofetarie Artizanala - LoveCake.ro", "specific": "Deserturi & torturi", "buget": 28, "locatie": "Baia Mare", "imagine": IMAGES["desert"], "cheie": "desert"},
    {"nume": "Tres Bien", "specific": "Bistro & fine dining", "buget": 85, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Casa Codreneasca", "specific": "Romanesc", "buget": 65, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Lezzet Fast Food", "specific": "Fast food", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["fastFood"], "cheie": "fastFood"},
    {"nume": "Pa Ograda Pizzeria", "specific": "Pizza", "buget": 45, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Chip&Dale", "specific": "Patiserie & pizza", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["desert"], "cheie": "desert"},
    {"nume": "Gran Gala", "specific": "Pizza & italian", "buget": 50, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "LibertyXI", "specific": "Pizza & pub", "buget": 45, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Pizza Plus", "specific": "Pizza", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Pizza Gemelli", "specific": "Pizza", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Pizzeria Zippi", "specific": "Pizza", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Restaurant Delfinul", "specific": "Romanesc", "buget": 60, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Restaurant Kaymak", "specific": "Turcesc", "buget": 70, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Restaurant Pronto", "specific": "Fast food & pizza", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["fastFood"], "cheie": "fastFood"},
    {"nume": "Restaurant Salsa", "specific": "International", "buget": 65, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Restaurantul Social & Catering ASSOC", "specific": "Catering & social", "buget": 55, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Astoria", "specific": "Restaurant", "buget": 60, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Bulevard", "specific": "Restaurant", "buget": 60, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Complex Europa", "specific": "Restaurant & evenimente", "buget": 85, "locatie": "Baia Mare", "imagine": IMAGES["hotel"], "cheie": "hotel"},
    {"nume": "La Palincie", "specific": "Romanesc", "buget": 65, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume":"UTCN cantina", "specific": "Romanesc", "buget": 20, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
]

def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    no_diacritics = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return no_diacritics.lower()


def clean_slug(slug: str) -> str:
    return re.sub(r"(-Baia-Mare(-\d+)?)+$", "", slug, flags=re.IGNORECASE).replace("-Romania", "")


def slug_to_name(slug: str) -> str:
    cleaned = clean_slug(slug)
    raw_name = re.sub(r"\s+", " ", cleaned.replace("-", " ")).strip()
    return RENAMES.get(raw_name, raw_name)


def determine_profile(name: str) -> dict[str, str | int]:
    text = normalize_text(name)

    if re.search(r"(butcher|steak)", text):
        return {"cheie": "steak", "specific": "Steakhouse & grill", "buget": 120, "imagine": IMAGES["steak"]}

    if re.search(
        r"(pizza|pizzeria|buonissimo|rapido|log out|pit stop|pizza h|pizza plus|pizza gemelli|zippi|rimmini|peperosso|spartan|kfc|burger|speedy|supreme|mado|freshplus|lezzet|porto|tom and jerry|chip and dale|placintarie|andana pan)",
        text,
    ):
        return {"cheie": "pizza", "specific": "Pizza & fast food", "buget": 45, "imagine": IMAGES["pizza"]}

    if re.search(
        r"(cafe|coffee|juice|smoothie|bar|pub|lounge|cocktail|ursus|moki|nomad|rox|gigi|mazo|vintage|zoom|office|college|sahara|contiline|artemis|rockwave|heaven)",
        text,
    ):
        return {"cheie": "cafe", "specific": "Cafe & bar", "buget": 35, "imagine": IMAGES["cafe"]}

    if re.search(r"(hotel|mara|europa|transilvania|ghr|evenimente|millennium|rivulus|castel|la tour|complex europa|riviera)", text):
        return {"cheie": "hotel", "specific": "Restaurant & evenimente", "buget": 95, "imagine": IMAGES["hotel"]}

    if re.search(r"(cofetarie|creperie|chocolart|lovecake|placintarie|cake|dessert|patiserie|chip and dale)", text):
        return {"cheie": "desert", "specific": "Deserturi & patiserie", "buget": 30, "imagine": IMAGES["desert"]}

    return {"cheie": "restaurant", "specific": "Restaurant", "buget": 70, "imagine": IMAGES["restaurant"]}


def generate_menu(profile_key: str) -> list[dict[str, str | int]]:
    if profile_key == "pizza":
        return [
            {"numeProdus": "Pizza Margherita", "pret": 34},
            {"numeProdus": "Pizza Quattro Stagioni", "pret": 44},
            {"numeProdus": "Limonada", "pret": 14},
        ]

    if profile_key == "cafe":
        return [
            {"numeProdus": "Cappuccino", "pret": 14},
            {"numeProdus": "Croissant", "pret": 12},
            {"numeProdus": "Cheesecake", "pret": 24},
        ]

    if profile_key == "desert":
        return [
            {"numeProdus": "Crepa cu ciocolata", "pret": 19},
            {"numeProdus": "Tarta de sezon", "pret": 22},
            {"numeProdus": "Espresso", "pret": 10},
        ]

    if profile_key == "hotel":
        return [
            {"numeProdus": "Starter al casei", "pret": 29},
            {"numeProdus": "Fel principal premium", "pret": 59},
            {"numeProdus": "Desert de casa", "pret": 24},
        ]

    if profile_key == "steak":
        return [
            {"numeProdus": "Ribeye Steak", "pret": 110},
            {"numeProdus": "Burger signature", "pret": 58},
            {"numeProdus": "Cartofi cu parmezan", "pret": 24},
        ]

    if profile_key == "fastFood":
        return [
            {"numeProdus": "Burger clasic", "pret": 32},
            {"numeProdus": "Cartofi prajiti", "pret": 16},
            {"numeProdus": "Bautura rece", "pret": 12},
        ]

    return [
        {"numeProdus": "Ciorba zilei", "pret": 24},
        {"numeProdus": "Fel principal", "pret": 46},
        {"numeProdus": "Desert de casa", "pret": 21},
    ]


def create_local(entry: str | dict[str, str | int]) -> dict[str, str | int | list[dict[str, str | int]]]:
    is_custom = isinstance(entry, dict)
    name = entry["nume"] if is_custom else slug_to_name(entry)
    profile = determine_profile(name)
    google_link = f"https://www.google.com/search?q={quote_plus(f'{name} Baia Mare')}"

    local = {
        "nume": name,
        "buget": int(entry["buget"]) if is_custom and "buget" in entry else int(profile["buget"]),
        "specific": str(entry["specific"]) if is_custom and "specific" in entry else str(profile["specific"]),
        "locatie": str(entry["locatie"]) if is_custom and "locatie" in entry else "Baia Mare",
        "linkOficial": str(entry["linkOficial"]) if is_custom and "linkOficial" in entry else google_link,
        "imagine": str(entry["imagine"]) if is_custom and "imagine" in entry else str(profile["imagine"]),
        "cheie": str(entry["cheie"]) if is_custom and "cheie" in entry else str(profile["cheie"]),
    }

    local["meniu"] = entry["meniu"] if is_custom and "meniu" in entry else generate_menu(str(local["cheie"]))
    return local


def build_restaurants_seed() -> list[dict[str, str | int | list[dict[str, str | int]]]]:
    unique_by_name: dict[str, dict[str, str | int | list[dict[str, str | int]]]] = {}

    for entry in SOURCE_LOCATIONS:
        local = create_local(entry)
        unique_by_name[str(local["nume"])] = local

    return sorted(unique_by_name.values(), key=lambda local: (int(local["buget"]), normalize_text(str(local["nume"]))))


RESTAURANTS_SEED = build_restaurants_seed()


def build_slug(name: str) -> str:
    normalized = unicodedata.normalize("NFD", name)
    no_diacritics = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    lowered = no_diacritics.lower()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", lowered)
    return re.sub(r"\s+", "-", cleaned).strip("-")


def seed_database(db: Session) -> None:
    existing_count = db.scalar(select(func.count(Restaurant.id)))
    if existing_count and existing_count > 0:
        db.query(MenuItem).delete()
        db.query(Restaurant).delete()
        db.commit()

    for restaurant_data in RESTAURANTS_SEED:
        restaurant = Restaurant(
            slug=build_slug(restaurant_data["nume"]),
            name=restaurant_data["nume"],
            specific=restaurant_data["specific"],
            avg_budget=float(restaurant_data["buget"]),
            location=restaurant_data["locatie"],
            official_link=restaurant_data.get("linkOficial"),
            image=restaurant_data["imagine"],
        )

        for item_data in restaurant_data["meniu"]:
            restaurant.menu_items.append(
                MenuItem(
                    name=item_data["numeProdus"],
                    price=float(item_data["pret"]),
                )
            )

        db.add(restaurant)

    db.commit()
