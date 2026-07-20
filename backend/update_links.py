import time
from googlesearch import search
from .database import SessionLocal
from .models import Restaurant


def update_restaurant_links():
    db = SessionLocal()
    try:
        restaurante = db.query(Restaurant).all()
        print(
            f"Am găsit {len(restaurante)} restaurante. Începem căutarea"
            " link-urilor..."
        )

        for r in restaurante:
            # Sărim peste restaurantele care au deja link valid
            if (
                hasattr(r, "website_url")
                and r.website_url
                and not r.website_url.startswith("https://www.google.com")
            ):
                continue

            query = f"{r.name} Baia Mare site oficial"
            try:
                for url in search(query, num_results=1):
                    if hasattr(r, "website_url"):
                        r.website_url = url
                    elif hasattr(r, "website"):
                        r.linkOficial = url

                    print(f"✅ Găsit pentru {r.name}: {url}")
                    break

                time.sleep(1.2)
            except Exception as e:
                print(f"⚠️ Eroare la {r.name}: {e}")

        db.commit()
        print(
            "🎉 Gata! Toate link-urile au fost actualizate în baza de date!"
        )
    finally:
        db.close()


if __name__ == "__main__":
    update_restaurant_links()