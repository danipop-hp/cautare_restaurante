# Urban Plate Baia Mare

Proiectul include un backend REST API cu FastAPI + SQLite si un frontend SvelteKit conectat la API.

## Structura proiectului (stare curenta)

- `backend/main.py` - endpoint-uri REST (`/api/health`, `/api/restaurants`, `/api/restaurants/{slug}`)
- `backend/models.py` - modelele SQLAlchemy (`Restaurant`, `MenuItem`)
- `backend/database.py` - conexiunea la SQLite
- `backend/seed_data.py` - genereaza dataset-ul si populeaza baza de date la startup
- `backend/restaurante.db` - baza SQLite locala
- `frontend/src/routes/+page.svelte` - pagina principala + cautare dupa buget
- `frontend/src/routes/restaurants/[slug]/+page.svelte` - pagina de detalii restaurant
- `start_app.bat` - porneste backend + frontend in 2 ferestre

Observatie: seed-ul folosit in prezent este generat din `backend/seed_data.py`.

## 1. Instalare dependinte

```bash
pip install -r requirements.txt

cd frontend
npm install
```

## 2. Rulare rapida (recomandat)

Din radacina proiectului:

```bat
start_app.bat
```

Se deschid doua ferestre CMD:
- backend pe `http://127.0.0.1:8000`
- frontend pe `http://127.0.0.1:5173`

Deschide in browser:

```text
http://127.0.0.1:5173
```

## 3. Rulare manuala

CMD:

```bat
backend\run_backend.bat
frontend\start_frontend.bat
```

PowerShell:

```powershell
.\backend\run_backend.ps1
.\frontend\start_frontend.ps1
```

## 4. Endpoint-uri API

- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/api/restaurants`
- `http://127.0.0.1:8000/api/restaurants/{slug}`
- Swagger: `http://127.0.0.1:8000/docs`

## 5. Functionalitati implementate end-to-end

- cautare restaurante dupa buget (`GET /api/restaurants?max_budget=`)
- afisare rezultate in homepage doar dupa apasarea butonului `Cauta`
- pagina de detalii restaurant (`/restaurants/{slug}`)
- afisare meniu restaurant (`GET /api/restaurants/{slug}`)

Frontend-ul foloseste SvelteKit si consuma API-ul FastAPI in timp real.

## 6. Troubleshooting (Windows)

- daca `python` nu este recunoscut, foloseste `py` (scripturile `.bat` deja fac asta)
- daca PowerShell blocheaza `.ps1`, foloseste variantele `.bat` sau ruleaza:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
