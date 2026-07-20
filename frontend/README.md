# Urban Plate Frontend (SvelteKit)

Frontend-ul consuma API-ul FastAPI de pe:

- `window.API_BASE_URL` daca este setat explicit.
- Altfel, construieste automat URL-ul pe baza host-ului paginii: `http://<host-curent>:8000/api`.

## Instalare

```sh
npm install
```

## Rulare local (dev)

```sh
npm run dev -- --host 127.0.0.1 --port 5173
```

Pentru acces din telefon (aceeasi retea Wi-Fi):

```sh
npm run dev -- --host 0.0.0.0 --port 5173
```

Deschide: http://127.0.0.1:5173

## Build

```sh
npm run build
npm run preview -- --host 0.0.0.0 --port 5173
```
