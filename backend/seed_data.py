import re
import unicodedata
from urllib.parse import quote_plus

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth_utils import generate_salt, hash_password
from .models import Restaurant, User

IMAGES = {
    "restaurant": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
    "fastFood": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
    "shaorma": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?auto=format&fit=crop&w=900&q=80",
    "brunch": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=900&q=80",
    "bar": "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=80",
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
    "B owl by DorDePulpa": "Bowl",
    "Barbarossa": "Barbarossa",
    "BOHO Brasserie": "Boho Braserie",
    "BRO Restaurant": "Bro Restaurant",
    "Buonissimo": "Bounissimo",
    "CASA DOBRO": "Casa Dobro",
    "Casa Crisan": "Casa Crisan",
    "Casa Codreneasca": "Casa Codrească",
    "Eben Ezer": "Eben-Ezer",
    "Flavours": "Flavours",
    "FreshPlus": "Fresh Plus",
    "Hotel Europa Baia Mare Baia Mare": "Hotel Europa",
    "Karaffe": "Karaffe",
    "Le Bistrot": "Le Bistrot",
    "Lumiere": "La Lumiere",
    "Mazo": "Mazo / Brunch and Coffee",
    "Bulevard": "La Bulevard",
    "La Palincie": "La Pălincie",
    "Pizza Buna Pizza Rimmini": "Pizza Rimini",
    "Restaurant Salsa": "Salsa",
    "Restaurantul Social & Catering ASSOC": "Social Catering ASOC",
    "Rivulus Cafe": "Hotel Rivulus",
    "Rox - Specialty Coffee -": "Rock Specialty Coffee",
    "Restaurant Millennium": "Restaurant Millennium",
    "Tom and Jerry": "Tom & Jerry",
    "Centrul de evenimente GHR": "GHR Evenimente - Ghitta Hotel Restaurant",
    "Philia Events": "OAZIS PHILIA",
    "PizzaBaiaMarero": "PizzaBaiaMare.ro",
    "PIT STOP": "PIT STOP PIZZA",
    "La Sueta": "La Sueta Resurrection",
    "Restaurant Crenguta": "Restaurant Crenguta",
    "Spartan Restaurant": "Spartan Baia Mare",
    "Budapesta": "Restaurant Budapesta",
    "KFC": "KFC Baia Mare Vivo!",
    "KFC Value Centre": "KFC Baia Mare Value Center",
    "Damas Arabic Food": "Damas Arabic Food",
    "Orient Turkish Bistro": "Orient Turkish Bistro",
    "Speedy Fast Food": "Speedy Fast Food",
    "Istanbul Kebap House": "Istanbul Kebap House",
    "Sahara": "Sahara Pub",
    "Sport Bar Artemis": "Artemis Bar",
    "Cafe Bar URSUS": "Cafe-Bar URSUS",
    "UpFlour": "Porto",
}

SOURCE_LOCATIONS = [
    "Acacia-Baia-Mare",
    "Andana-Pan-Baia-Mare",
    "Art-Cafe-Bar-Baia-Mare",
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
    "Smart-Food-Baia-Mare",
    "Spartan-Restaurant-Baia-Mare",
    "Speedy-Fast-Food-Baia-Mare",
    "Sport-Bar-Artemis-Baia-Mare",
    "Supreme-Burger-Baia-Mare",
    "Restaurant-Millennium-Baia-Mare-2",
    "The-Buffet-Baia-Mare",
    "The-Oak-Baia-Mare",
    "Tom-and-Jerry-Baia-Mare",
    "UpFlour-Baia-Mare",
    "Vintage-Bar-Baia-Mare",
    "Zoom-Pub-Baia-Mare",
    {"nume": "Danis Fast Food", "specific": "Shaorma, kebab, fast-food, turcesc", "buget": 30, "locatie": "Baia Mare", "imagine": IMAGES["shaorma"], "cheie": "shaorma"},
    {"nume": "Mesopotamia", "specific": "Shaorma, kebab, doner, fast-food", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["shaorma"], "cheie": "shaorma"},
    {"nume": "Istanbul Kebap House", "specific": "Shaorma & kebab", "buget": 30, "locatie": "Baia Mare", "imagine": IMAGES["shaorma"], "cheie": "shaorma"},
    {"nume": "Speedy Fast Food", "specific": "Shaorma, burger, fast-food, kebab", "buget": 30, "locatie": "Baia Mare", "imagine": IMAGES["shaorma"], "cheie": "shaorma"},
    {"nume": "Sultan Kebab / Doner", "specific": "Shaorma, kebab, turcesc, oriental, fast-food", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["shaorma"], "cheie": "shaorma"},
    {"nume": "Damas Arabic Food", "specific": "Shaorma & arabic food", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["shaorma"], "cheie": "shaorma"},
    {"nume": "Orient Turkish Bistro", "specific": "Shaorma & turcesc", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["shaorma"], "cheie": "shaorma"},
    {"nume": "Butcher's", "specific": "Steakhouse & grill", "buget": 120, "locatie": "Bd. Unirii 16, Baia Mare", "imagine": IMAGES["steak"], "cheie": "steak"},
    {"nume": "La Pastorel", "specific": "Romanesc", "buget": 70, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Riviera", "specific": "International & events", "buget": 100, "locatie": "Bd. Republicii 46, Baia Mare", "imagine": IMAGES["hotel"], "cheie": "hotel"},
    {"nume": "Mado Baia Mare", "specific": "Shaorma, doner, kebab, fast-food", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["shaorma"], "cheie": "shaorma"},
    {"nume": "ChocolArt Cake Factory", "specific": "Cofetarie artizanala (Torturi, Pachete cu mai multe prajituri)", "buget": 250, "locatie": "Baia Mare", "imagine": IMAGES["desert"], "cheie": "desert"},
    {"nume": "Nomad Cafe", "specific": "Cafea de specialitate", "buget": 20, "locatie": "Baia Mare", "imagine": IMAGES["cafe"], "cheie": "cafe"},
    {"nume": "Rox - Specialty Coffee -", "specific": "Cafea de specialitate", "buget": 25, "locatie": "Baia Mare", "imagine": IMAGES["cafe"], "cheie": "cafe"},
    {"nume": "Mazo", "specific": "Brunch & coffee", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["brunch"], "cheie": "brunch"},
    {"nume": "Cofetarie Artizanala - LoveCake.ro", "specific": "Deserturi & torturi", "buget": 25, "locatie": "Baia Mare", "imagine": IMAGES["desert"], "cheie": "desert"},
    {"nume": "Tres Bien", "specific": "Restaurant", "buget": 55, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant,__meniul-zilei__"},
    {"nume": "Casa Codreneasca", "specific": "Restaurant", "buget": 30, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Lezzet Fast Food", "specific": "International, pizza, fast-food", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["fastFood"], "cheie": "fastFood"},
    {"nume": "Pa Ograda Pizzeria", "specific": "Pizza", "buget": 45, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Chip&Dale", "specific": "Patiserie & pizza", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["desert"], "cheie": "desert"},
    {"nume": "Pizza Plus", "specific": "Pizza", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Pizza Gemelli", "specific": "Pizza", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Pizzeria Zippi", "specific": "Pizza", "buget": 40, "locatie": "Baia Mare", "imagine": IMAGES["pizza"], "cheie": "pizza"},
    {"nume": "Restaurant Delfinul", "specific": "Romanesc", "buget": 60, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Restaurant Kaymak", "specific": "Turcesc", "buget": 70, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Restaurant Pronto", "specific": "Restaurant, meniu-zilei (Există meniul zilei)", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["fastFood"], "cheie": "fastFood"},
    {"nume": "Restaurant Salsa", "specific": "International", "buget": 65, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Restaurantul Social & Catering ASSOC", "specific": "Catering & social", "buget": 35, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Astoria", "specific": "Restaurant", "buget": 60, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Bulevard", "specific": "Restaurant", "buget": 20, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant, __meniul_zilei__"},
    {"nume": "Complex Europa", "specific": "Restaurant & evenimente", "buget": 85, "locatie": "Baia Mare", "imagine": IMAGES["hotel"], "cheie": "hotel"},
    {"nume": "La Palincie", "specific": "Romanesc", "buget": 65, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume":"UTCN cantina", "specific": "Romanesc", "buget": 20, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant"},
    {"nume": "Casa Crisan", "specific": "International", "buget": 50, "locatie": "Baia Mare", "imagine": IMAGES["restaurant"], "cheie": "restaurant,__meniul_zilei__"},]

REMOVED_LOCALS = {
    "andana pan",
    "astoria",
    "bar 13",
    "bar acasa",
    "butcher's",
    "casa dobro",
    "greenys",
    "la mircea",
    "la pastorel",
    "la sueta resurrection",
    "pa ograda pizzeria",
    "peperosso",
    "placintarie",
    "pizza h",
    "riviera",
    "rock wave tavern",
    "sueta resurrection",
    "zen lounge",
}

LOCAL_OVERRIDES = {
    "acacia": {"buget": 70},
    "barbarossa": {"specific": "Internațional", "buget": 50, "cheie": "restaurant", "imagine": IMAGES["restaurant"]},
    "art cafe bar": {"buget": 20},
    "artemis bar": {"buget": 20},
    "bastion": {"buget": 50, "cheie": "desert"},
    "bizo": {"specific": "Brunch", "imagine": IMAGES["brunch"], "buget": 40, "cheie": "brunch"},
    "bounissimo": {"specific": "Restaurant, (MENIUL ZILEI)", "cheie": "restaurant", "imagine": IMAGES["restaurant"]},
    "bowl": {"specific": "Fast-food", "imagine": IMAGES["fastFood"], "cheie": "fastFood", "buget": 65},
    "boho braserie": {"specific": "Brunch, Restaurant", "imagine": IMAGES["brunch"], "cheie": "brunch", "buget": 30},
    "bro restaurant": {"specific": "Restaurant, (MENIUL ZILEI)", "buget": 35, "cheie": "restaurant"},
    "casa codrească": {"specific": "Restaurant", "buget": 35, "cheie": "restaurant"},
    "karaffe": {"buget": 55},
    "cinquecento": {"specific": "Restaurant, (MENIUL ZILEI)", "buget": 35, "cheie": "restaurant"},
    "college pub": {"buget": 15},
    "cocktail mobile bar": {"buget": 20},
    "eben-ezer": {"specific": "Cafe Bar, Cafenea", "imagine": IMAGES["cafe"], "cheie": "cafe", "buget": 20},
    "family restaurant": {"specific": "Restaurant, (MENIUL ZILEI)", "buget": 35, "cheie": "restaurant"},
    "flavours": {"buget": 50, "cheie": "pizza"},
    "fresh plus": {"specific": "Bar, Mâncare", "imagine": IMAGES["bar"], "cheie": "bar", "buget": 40 },
    "gran gala": {"specific": "Italian, Pizza, Restaurant", "buget": 55, "cheie": "pizza", "imagine": IMAGES["pizza"]},
    "hotel europa": {"specific": "Restaurant", "buget": 60, "cheie": "restaurant", "imagine": IMAGES["hotel"]},
    "hotel rivulus": {"specific": "Restaurant, (MENIUL ZILEI)", "buget": 50, "cheie": "restaurant", "imagine": IMAGES["hotel"]},
    "il padrino": {"specific": "Italian, Restaurant, Pizza, Pasta", "buget": 60, "cheie": "pizza"},
    "la creperie": {"specific": "Restaurant, Burger, Desert, Patiserie", "buget": 40, "cheie": "restaurant", "imagine": IMAGES["restaurant"]},
    "la bulevard": {"specific": "Restaurant, (MENIUL ZILEI)", "buget": 20, "cheie": "restaurant"},
    "la cucina": {"specific": "Italian, Restaurant", "cheie": "restaurant"},
    "la lumiere": {"specific": "Internațional", "buget": 70, "cheie": "restaurant", "imagine": IMAGES["restaurant"]},
    "la palincie": {"specific": "Internațional", "buget": 60, "cheie": "restaurant"},
    "le bistrot": {"specific": "Internațional", "cheie": "restaurant","buget": 60 ,"imagine": IMAGES["restaurant"]},
    "lezzet fast food": {"specific": "Internațional, Pizza, Fast-food"},
    "log out": {"specific": "Fast-food", "imagine": IMAGES["fastFood"], "cheie": "fastFood", "buget": 55},
    "mado baia mare": {"specific": "Shaorma, Doner, Kebab, Fast-food", "cheie": "shaorma"},
    "mazo / brunch and coffee": {"buget": 30, "specific": "Brunch, Coffee", "cheie": "brunch"},
    "office pub": {"specific": "Restaurant, (MENIUL ZILEI)", "buget": 30, "cheie": "restaurant", "imagine": IMAGES["restaurant"]},
    "pastucci's pasta bar": {"specific": "Paste, Restaurant", "buget": 40, "cheie": "restaurant"},
    "pizzeria zippi": {"specific": "Pizza, Restaurant, (MENIUL ZILEI)", "cheie": "pizza", "buget": 40},
    "pizza albina": {"specific": "Restaurant", "cheie": "restaurant"},
    "pizza rimini": {"specific": "Pizza", "buget": 55, "cheie": "pizza"},
    "porto": {"specific": "Restaurant, Pizza", "cheie": "restaurant"},
    "rapido": {"specific": "Internațional", "buget": 45, "cheie": "restaurant"},
    "restaurant pronto": {"specific": "Restaurant, (MENIUL ZILEI)", "cheie": "restaurant"},
    "restaurant salsa": {"specific": "Restaurant, (MENIUL ZILEI)", "buget": 30, "cheie": "restaurant"},
    "restaurant millennium": {"buget": 40, "cheie": "restaurant"},
    "rock specialty coffee": {"buget": 20},
    "rocca pub": {"buget": 20},
    "sahara pub": {"buget": 40, "imagine": IMAGES["pub"]},
    "scottish pub": {"specific": " Fast-food", "imagine": IMAGES["fastFood"], "buget": 55, "cheie": "fastFood"},
    "social catering asoc": {"specific": "Catering, Social, (MENIUL ZILEI)", "buget": 30, "cheie": "restaurant"},
    "spartan baia mare": {"specific": "Fast-food", "buget": 60, "cheie": "fastFood", "imagine": IMAGES["fastFood"]},
    "supreme burger": {"specific": "Fast-food", "imagine": IMAGES["fastFood"], "buget": 60, "cheie": "fastFood"},
    "salsa": {"specific": "Restaurant, (MENIUL ZILEI)", "buget": 30, "cheie": "restaurant"},
    "tom & jerry": {"specific": "Fast-food", "imagine": IMAGES["fastFood"], "buget": 55, "cheie": "fastFood"},
    "vintage bar": {"buget": 20},
    "zoom pub": {"buget": 25},
    "ghr evenimente - ghitta hotel restaurant": {"specific": "Restaurant, Evenimente", "buget": 80, "cheie": "hotel"},
    "complex europa": {"specific": "Restaurant, Evenimente", "buget": 80, "cheie": "hotel"},
}


def format_specific_text(value: str | list[str]) -> str:
    if isinstance(value, list):
        text = ", ".join(str(item) for item in value)
    else:
        text = str(value)

    text = re.sub(r"\brom[âa]nesc\b|\bromana\b", "Restaurant", text, flags=re.IGNORECASE)
    text = text.replace("(MENIUL ZILEI)", "__MENIUL_ZILEI__")

    clauses: list[str] = []
    for clause in re.split(r"\s*,\s*", text.strip()):
        if not clause:
            continue

        tokens = re.split(r"(\s+|&|/)", clause)
        formatted_tokens: list[str] = []
        for token in tokens:
            if token == "" or token.isspace() or token in {"&", "/"}:
                formatted_tokens.append(token)
                continue

            if token.isupper() and len(token) <= 5:
                formatted_tokens.append(token)
                continue

            subparts = []
            for part in token.split("-"):
                if not part:
                    subparts.append(part)
                    continue
                lowered = part.lower()
                subparts.append(lowered[:1].upper() + lowered[1:])
            formatted_tokens.append("-".join(subparts))

        clauses.append("".join(formatted_tokens))

    result = ", ".join(clauses)
    return result.replace("__MENIUL_ZILEI__", "(MENIUL ZILEI)")

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
        return {"cheie": "steak", "specific": "Steakhouse & Grill", "buget": 120, "imagine": IMAGES["steak"]}

    if re.search(r"(shaorma|shawarma|kebab|kebap|doner|gyros|turkish|turcesc|arabic food|orient|istanbul|speedy|danis|mesopotamia|sultan)", text):
        return {"cheie": "shaorma", "specific": "Shaorma & Kebab", "buget": 40, "imagine": IMAGES["shaorma"]}

    if re.search(
        r"(pizza|pizzeria|buonissimo|rapido|log out|pit stop|pizza h|pizza plus|pizza gemelli|zippi|rimmini|peperosso|spartan|kfc|burger|speedy|supreme|mado|freshplus|lezzet|porto|tom and jerry|chip and dale|placintarie|andana pan)",
        text,
    ):
        return {"cheie": "pizza", "specific": "Pizza & Fast-food", "buget": 45, "imagine": IMAGES["pizza"]}

    if re.search(r"(brunch|mic dejun|mazo|bistro)", text):
        return {"cheie": "brunch", "specific": "Brunch & Breakfast", "buget": 38, "imagine": IMAGES["brunch"]}

    if re.search(r"(bar|pub|lounge|cocktail|ursus|vintage|zoom|office|college|sahara|artemis)", text):
        return {"cheie": "bar", "specific": "Bar & Drinks", "buget": 20, "imagine": IMAGES["bar"]}

    if re.search(r"(cafe|coffee|juice|smoothie|moki|nomad|rox|heaven)", text):
        return {"cheie": "cafe", "specific": "Cafe & Bar", "buget": 20, "imagine": IMAGES["cafe"]}

    if re.search(r"(hotel|mara|europa|transilvania|ghr|evenimente|millennium|rivulus|castel|la tour|complex europa|riviera)", text):
        return {"cheie": "hotel", "specific": "Restaurant & Evenimente", "buget": 95, "imagine": IMAGES["hotel"]}

    if re.search(r"(cofetarie|creperie|chocolart|lovecake|placintarie|cake|dessert|patiserie|chip and dale)", text):
        return {"cheie": "desert", "specific": "Deserturi & Patiserie", "buget": 30, "imagine": IMAGES["desert"]}

    return {"cheie": "restaurant", "specific": "Restaurant", "buget": 70, "imagine": IMAGES["restaurant"]}


def create_local(entry: str | dict[str, str | int]) -> dict[str, str | int | list[str]] | None:
    is_custom = isinstance(entry, dict)
    name = entry["nume"] if is_custom else slug_to_name(entry)
    profile = determine_profile(name)
    google_link = f"https://www.google.com/search?q={quote_plus(f'{name} Baia Mare')}"
    normalized_name = normalize_text(str(name))

    if normalized_name in REMOVED_LOCALS:
        return None

    local = {
        "nume": name,
        "buget": int(entry["buget"]) if is_custom and "buget" in entry else int(profile["buget"]),
        "specific": str(entry["specific"]) if is_custom and "specific" in entry else str(profile["specific"]),
        "locatie": str(entry["locatie"]) if is_custom and "locatie" in entry else "Baia Mare",
        "linkOficial": str(entry["linkOficial"]) if is_custom and "linkOficial" in entry else google_link,
        "imagine": str(entry["imagine"]) if is_custom and "imagine" in entry else str(profile["imagine"]),
        "cheie": str(entry["cheie"]) if is_custom and "cheie" in entry else str(profile["cheie"]),
    }

    override = LOCAL_OVERRIDES.get(normalized_name)
    if override:
        local.update(override)

    local["specific"] = format_specific_text(str(local["specific"]))

    if "Evenimente" in str(local["specific"]):
        local["buget"] = 80

    local["tags"] = [tag.strip() for tag in str(local["cheie"]).replace("-", ",").split(",") if tag.strip()]
    return local


def build_restaurants_seed() -> list[dict[str, str | int | list[str]]]:
    unique_by_name: dict[str, dict[str, str | int | list[str]]] = {}

    for entry in SOURCE_LOCATIONS:
        local = create_local(entry)
        if local is None:
            continue
        unique_by_name[normalize_text(str(local["nume"]))] = local

    return sorted(unique_by_name.values(), key=lambda local: (int(local["buget"]), normalize_text(str(local["nume"]))))


RESTAURANTS_SEED = build_restaurants_seed()

ADMIN_SEED = {
    "name": "Daniel",
    "email": "admin@urbanplate.ro",
    "password": "Admin123!",
    "role": "admin",
}


def build_slug(name: str) -> str:
    normalized = unicodedata.normalize("NFD", name)
    no_diacritics = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    lowered = no_diacritics.lower()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", lowered)
    return re.sub(r"\s+", "-", cleaned).strip("-")


def seed_database(db: Session) -> None:
    existing_by_slug = {
        restaurant.slug: restaurant
        for restaurant in db.scalars(select(Restaurant)).all()
    }
    desired_slugs = {build_slug(str(restaurant_data["nume"])) for restaurant_data in RESTAURANTS_SEED}

    for slug, restaurant in list(existing_by_slug.items()):
        if slug not in desired_slugs:
            db.delete(restaurant)
            existing_by_slug.pop(slug, None)

    for restaurant_data in RESTAURANTS_SEED:
        slug = build_slug(restaurant_data["nume"])
        restaurant = existing_by_slug.get(slug)

        if restaurant is None:
            restaurant = Restaurant(slug=slug)
            db.add(restaurant)
            existing_by_slug[slug] = restaurant

        restaurant.name = str(restaurant_data["nume"])
        restaurant.specific = str(restaurant_data["specific"])
        restaurant.avg_budget = float(restaurant_data["buget"])
        restaurant.location = str(restaurant_data["locatie"])
        restaurant.official_link = restaurant_data.get("linkOficial")
        restaurant.menu_url = restaurant_data.get("linkOficial")
        restaurant.tags = restaurant_data.get("tags", [])
        restaurant.status = "active"
        restaurant.image = str(restaurant_data["imagine"])

    db.commit()


def ensure_admin_user(db: Session) -> None:
    existing = db.scalar(select(User).where(User.email == ADMIN_SEED["email"]))
    if existing is not None:
        return

    salt = generate_salt()
    password_hash = hash_password(ADMIN_SEED["password"], salt)
    admin_user = User(
        name=ADMIN_SEED["name"],
        email=ADMIN_SEED["email"],
        password_salt=salt,
        password_hash=password_hash,
        role=ADMIN_SEED["role"],
    )
    db.add(admin_user)
    db.commit()
