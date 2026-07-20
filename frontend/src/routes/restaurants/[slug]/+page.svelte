<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { isAuthenticated, logout } from '$lib/auth';
  import { isAdminAuthenticated } from '$lib/adminAuth';
  import { getApiBaseUrl } from '$lib/api';

  let restaurant = $state(null);
  let isLoading = $state(false);
  let error = $state('');
  let isAuthed = $state(false);
  let isAdminAuthed = $state(false);

  const apiBaseUrl = () => getApiBaseUrl();

  function buildMapsLink(numeRestaurant, locatieRestaurant) {
    const interogare = encodeURIComponent(`${numeRestaurant} ${locatieRestaurant}`);
    return `https://www.google.com/maps/search/?api=1&query=${interogare}`;
  }

  async function incarcaRestaurant() {
    const slug = $page.params.slug;
    if (!slug) {
      error = 'Lipseste identificatorul restaurantului.';
      return;
    }
    
    isLoading = true;
    error = '';

    try {
      const raspuns = await fetch(`${apiBaseUrl()}/restaurants/${encodeURIComponent(slug)}`);
      if (!raspuns.ok) {
        if (raspuns.status === 404) {
          error = 'Restaurantul nu a fost gasit.';
        } else {
          error = `Eroare API: ${raspuns.status}`;
        }
        return;
      }
      restaurant = await raspuns.json();
    } catch (err) {
      console.error('Nu am putut incarca restaurantul:', err);
      error = 'Nu am putut incarca detaliile din backend.';
    } finally {
      isLoading = false;
    }
  }

  function refreshAuthState() {
    isAuthed = isAuthenticated();
    isAdminAuthed = isAdminAuthenticated();
  }

  function handleLogout() {
    logout();
    isAuthed = false;
    goto('/login');
  }

  onMount(() => {
    incarcaRestaurant();
    refreshAuthState();
  });
</script>

<nav class="navbar">
  <div class="logo">Urban<span>Plate</span></div>
  <ul class="nav-links">
    <li><a href="/#home">Acasa</a></li>
    <li><a href="/#menu">Cautare</a></li>
    <li><a href="/#contact">Contact</a></li>
    {#if isAuthed}
      <li><button class="link-btn" type="button" onclick={handleLogout}>Logout</button></li>
      {#if isAdminAuthed}
        <li><a href="/admin">Admin</a></li>
      {/if}
    {:else}
      <li><a href="/login">Login</a></li>
      <li><a href="/register">Register</a></li>
      {#if isAdminAuthed}
        <li><a href="/admin">Admin</a></li>
      {/if}
    {/if}
  </ul>
</nav>

<main class="detalii-main">
  <a class="btn site-btn detalii-btn" href="/#menu">Inapoi la cautare</a>

  {#if isLoading}
    <p class="mesaj-gol">Se incarca detaliile...</p>
  {:else if error}
    <p class="mesaj-gol mesaj-eroare">{error}</p>
  {:else if restaurant}
    {@const linkOficial = restaurant.linkOficial && restaurant.linkOficial.trim() !== ''
      ? restaurant.linkOficial
      : buildMapsLink(restaurant.nume, restaurant.locatie)}
    <section class="detalii-card">
      <h1>{restaurant.nume}</h1>
      <div class="detalii-tags">
        <span>Specific: {restaurant.specific}</span>
        <span>Locatie: {restaurant.locatie}</span>
      </div>
      <img class="detalii-imagine" src={restaurant.imagine} alt={restaurant.nume} />
      <a class="btn detalii-btn site-btn" href={linkOficial} target="_blank" rel="noopener noreferrer">
        Pagina oficiala
      </a>
      <h2>Meniu</h2>
      {#if restaurant.meniu && restaurant.meniu.length > 0}
        <ul class="lista-meniu">
          {#each restaurant.meniu as produs}
            <li>
              <span>{produs.numeProdus}</span>
              <strong>{produs.pret} RON</strong>
            </li>
          {/each}
        </ul>
      {:else}
        <p class="mesaj-gol">Nu exista meniu disponibil pentru acest restaurant.</p>
      {/if}
    </section>
  {/if}
</main>

<footer>
  <p>&copy; 2026 Urban Plate Baia Mare. Descopera localuri bune, in bugetul tau.</p>
</footer>

<style>
  :global(:root) {
    --bg: #0f1117;
    --ink: #f8f3eb;
    --muted: #c0b7a9;
    --accent: #ff6b3d;
    --accent-2: #4cc9b0;
    --accent-3: #f4d06f;
    --surface: #1b1e26;
    --surface-2: #141720;
    --border: rgba(248, 243, 235, 0.12);
    --shadow: 0 24px 60px rgba(8, 10, 15, 0.55);
  }

  :global(body) {
    margin: 0;
    font-family: "Space Grotesk", system-ui, sans-serif;
    line-height: 1.6;
    color: var(--ink);
    scroll-behavior: smooth;
    background: radial-gradient(circle at 12% 15%, rgba(76, 201, 176, 0.35) 0, transparent 45%),
      radial-gradient(circle at 85% 12%, rgba(255, 107, 61, 0.28) 0, transparent 45%),
      radial-gradient(circle at 50% 80%, rgba(244, 208, 111, 0.2) 0, transparent 55%),
      linear-gradient(180deg, #0f1117 0%, #121522 100%);
  }

  :global(a) {
    color: inherit;
  }

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.7rem 3%;
    background: rgba(15, 17, 23, 0.78);
    backdrop-filter: blur(12px);
    position: fixed;
    width: 100%;
    box-sizing: border-box;
    top: 0;
    z-index: 1000;
    border-bottom: 1px solid rgba(248, 243, 235, 0.08);
  }

  .logo {
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .logo span {
    color: var(--accent);
  }

  .nav-links {
    display: flex;
    flex-wrap: wrap;
    list-style: none;
    gap: 6px;
    margin: 0 0 0 auto;
    padding: 0;
    justify-content: flex-end;
  }

  .nav-links a {
    text-decoration: none;
    color: var(--ink);
    transition: color 0.25s ease;
    font-size: 0.9rem;
    white-space: nowrap;
    padding: 2px 4px;
    position: relative;
  }

  .nav-links a::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -6px;
    height: 2px;
    width: 100%;
    background: var(--accent);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.25s ease;
  }

  .link-btn {
    border: none;
    background: transparent;
    font: inherit;
    color: var(--ink);
    cursor: pointer;
    padding: 2px 4px;
    position: relative;
    font-size: 0.9rem;
    line-height: 1.1;
  }

  .link-btn::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -6px;
    height: 2px;
    width: 100%;
    background: var(--accent);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.25s ease;
  }

  .link-btn:hover::after {
    transform: scaleX(1);
  }

  @media (max-width: 520px) {
    .navbar {
      flex-wrap: wrap;
      gap: 6px;
    }

    .nav-links {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .nav-links a:hover {
    color: var(--accent);
  }

  .nav-links a:hover::after {
    transform: scaleX(1);
  }

  .detalii-main {
    min-height: 100vh;
    padding: 120px 8% 80px;
  }

  .detalii-card {
    max-width: 720px;
    margin: 24px auto 0;
    background: var(--surface);
    border: 1px solid rgba(28, 27, 26, 0.08);
    border-radius: 20px;
    padding: 30px;
    box-shadow: var(--shadow);
    animation: heroFade 0.8s ease forwards;
  }

  .detalii-card h1 {
    margin-bottom: 10px;
    font-family: "Fraunces", serif;
    font-size: clamp(2rem, 3.2vw, 2.6rem);
  }

  .detalii-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
  }

  .detalii-tags span {
    padding: 6px 12px;
    border-radius: 999px;
    background: var(--surface-2);
    color: var(--muted);
    font-size: 0.85rem;
  }

  .detalii-imagine {
    width: 100%;
    height: 260px;
    object-fit: cover;
    border-radius: 16px;
    margin-bottom: 18px;
  }

  .lista-meniu {
    list-style: none;
    padding: 0;
  }

  .lista-meniu li {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid rgba(28, 27, 26, 0.08);
  }

  .mesaj-gol {
    margin-top: 24px;
    font-weight: 600;
    color: var(--muted);
  }

  .mesaj-eroare {
    color: #b91c1c;
  }

  .btn {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), #ffb347);
    color: #1b1b1b;
    padding: 10px 18px;
    border-radius: 999px;
    text-decoration: none;
    font-weight: 600;
    box-shadow: 0 12px 28px rgba(255, 122, 61, 0.3);
  }

  .site-btn {
    background: #1f1d1b;
    margin-top: 12px;
    color: #fff;
  }

  .site-btn:hover {
    background: #111;
  }

  footer {
    background: #141210;
    color: #f3efe9;
    text-align: center;
    padding: 24px 16px;
  }

  @keyframes heroFade {
    from {
      opacity: 0;
      transform: translateY(12px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
