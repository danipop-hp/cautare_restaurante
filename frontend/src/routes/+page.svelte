Am înțeles greșit ce ai vrut să spui la început. Scuze pentru încurcătură!

Am repus verificarea `if (!isAuthenticated())` exact așa cum era în codul tău inițial. Acum, dacă utilizatorul nu este logat și apasă pe **Caută** sau pe oricare dintre filtrele rapide, va fi redirecționat direct la pagina de **`/login`**.

Iată fișierul complet, păstrând absolut tot din codul și designul tău inițial, plus doar butoanele de filtre rapide:

```svelte
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, logout } from '$lib/auth';
  import { isAdminAuthenticated } from '$lib/adminAuth';
  import { getApiBaseUrl } from '$lib/api';

  let dateRestaurante = $state([]);
  let isLoading = $state(false);
  let error = $state('');
  let statusMessage = $state('Introdu un buget si apasa Cauta pentru a vedea restaurantele.');

  let isAuthed = $state(false);
  let isAdminAuthed = $state(false);

  let bugetMaxim = $state('');
  let specific = $state('');
  let cautare = $state('');

  const apiBaseUrl = () => getApiBaseUrl();

  function buildMapsLink(numeRestaurant, locatieRestaurant) {
    const interogare = encodeURIComponent(`${numeRestaurant} ${locatieRestaurant}`);
    return `https://www.google.com/maps/search/?api=1&query=${interogare}`;
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

  function seteazaFiltruRapid(valoare) {
    if (cautare === valoare) {
      cautare = '';
    } else {
      cautare = valoare;
    }
    incarcaRestaurante();
  }

  onMount(() => {
    refreshAuthState();
  });

  async function incarcaRestaurante() {
    if (!isAuthenticated()) {
      goto('/login');
      return;
    }
    isLoading = true;
    error = '';
    statusMessage = '';

    const parametri = new URLSearchParams();
    parametri.set('limit', '500');

    const bugetVal = Number(bugetMaxim);
    const areBugetValid = !Number.isNaN(bugetVal) && bugetVal > 0;
    const specificVal = specific.trim();
    const cautareVal = cautare.trim();

    if (!areBugetValid && !specificVal && !cautareVal) {
      isLoading = false;
      dateRestaurante = [];
      statusMessage = 'Introdu un buget valid.';
      return;
    }

    if (areBugetValid) {
      parametri.set('max_budget', bugetVal.toString());
    }

    if (specificVal.length > 0) {
      parametri.set('specific', specificVal);
    }

    if (cautareVal.length > 0) {
      parametri.set('q', cautareVal);
    }

    const url = `${apiBaseUrl()}/restaurants?${parametri.toString()}`;

    try {
      const raspuns = await fetch(url);
      if (!raspuns.ok) {
        throw new Error(`Eroare API: ${raspuns.status}`);
      }
      const data = await raspuns.json();
      dateRestaurante = Array.isArray(data) ? data : [];
      if (dateRestaurante.length === 0) {
        statusMessage = 'Nu am gasit restaurante pentru filtrele curente.';
      }
    } catch (err) {
      console.error('Nu am putut incarca restaurantele:', err);
      error = 'Nu am putut incarca datele din backend.';
      dateRestaurante = [];
    } finally {
      isLoading = false;
    }
  }
</script>

<nav class="navbar">
  <div class="logo">Urban<span>Plate</span></div>
  <ul class="nav-links">
    <li><a href="#home">Acasa</a></li>
    <li><a href="#menu">Cautare</a></li>
    <li><a href="#contact">Contact</a></li>
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

<header id="home" class="hero">
  <div class="hero-content">
    <h1>Gaseste rapid cel mai potrivit restaurant din Baia Mare</h1>
    <p>Compara optiuni reale dupa buget, specific culinar si locatie.</p>
    <div class="hero-badges">
      <span>Live data</span>
      <span>Buget clar</span>
      <span>Detalii rapide</span>
    </div>
    <a href="#menu" class="btn">Incepe Cautarea</a>
  </div>
</header>

<section id="menu" class="menu-section">
  <h2 class="section-title">Motor de Cautare Restaurante Baia Mare</h2>
  <p class="section-subtitle">Filtreaza rapid si vezi doar optiunile care se potrivesc.</p>
  <div class="menu-filters">
    <input
      id="bugetMaxim"
      type="number"
      min="1"
      step="1"
      bind:value={bugetMaxim}
      placeholder="Buget maxim (RON)"
    />
    <input
      id="specific"
      type="text"
      bind:value={specific}
      placeholder="Specific (ex: Romanesc)"
    />
    <input id="cautare" type="text" bind:value={cautare} placeholder="Cautare (nume, locatie)" />
    <button class="filter-btn" onclick={incarcaRestaurante}>Cauta</button>

    <div class="preparate-rapide">
      <button 
        type="button" 
        class="tag-btn {cautare === 'burger' ? 'activ' : ''}" 
        onclick={() => seteazaFiltruRapid('burger')}
      >
        🍔 Burger
      </button>

      <button 
        type="button" 
        class="tag-btn {cautare === 'pizza' ? 'activ' : ''}" 
        onclick={() => seteazaFiltruRapid('pizza')}
      >
        🍕 Pizza
      </button>

      <button 
        type="button" 
        class="tag-btn {cautare === 'shaorma' ? 'activ' : ''}" 
        onclick={() => seteazaFiltruRapid('shaorma')}
      >
        🥙 Shaorma
      </button>

      <button 
        type="button" 
        class="tag-btn {cautare === 'paste' ? 'activ' : ''}" 
        onclick={() => seteazaFiltruRapid('paste')}
      >
        🍝 Paste
      </button>

      <button 
        type="button" 
        class="tag-btn {cautare === 'cafea' ? 'activ' : ''}" 
        onclick={() => seteazaFiltruRapid('cafea')}
      >
        ☕ Cafea / Brunch
      </button>

      {#if cautare || specific || bugetMaxim}
        <button 
          type="button" 
          class="reset-btn" 
          onclick={() => { cautare = ''; specific = ''; bugetMaxim = ''; dateRestaurante = []; statusMessage = 'Filtrele au fost resetate.'; }}
        >
          ✖ Reseteaza
        </button>
      {/if}
    </div>
  </div>

  {#if isLoading}
    <p class="mesaj-gol">Se incarca restaurantele...</p>
  {:else if error}
    <p class="mesaj-gol mesaj-eroare">{error}</p>
  {:else}
    <div class="menu-container">
      {#each dateRestaurante as r, i}
        {@const linkRestaurant = (r.linkOficial && r.linkOficial.trim() !== '') 
          ? r.linkOficial 
          : (r.website_url && r.website_url.trim() !== '') 
            ? r.website_url 
            : (r.website && r.website.trim() !== '') 
              ? r.website 
              : buildMapsLink(r.nume || r.name, r.locatie || 'Baia Mare')}
        <article class="menu-item" style={`--delay: ${i * 60}ms`}>
          <img class="restaurant-img" src={r.imagine} alt={r.nume} />
          <div class="item-info">
            <h3>{r.nume}</h3>
            <p>Specific: {r.specific}</p>
            <p>Locatie: {r.locatie}</p>
            <span class="price">Buget mediu: {r.buget} RON</span>
            <div class="item-actions">
              <a class="btn site-btn detalii-btn" href={`/restaurants/${r.slug}`}>Detalii</a>
              <a class="btn site-btn" href={linkRestaurant} target="_blank" rel="noopener noreferrer">
                Viziteaza
              </a>
            </div>
          </div>
        </article>
      {/each}
    </div>
    {#if dateRestaurante.length === 0}
      <p class="mesaj-gol">{statusMessage}</p>
    {/if}
  {/if}
</section>

<footer id="contact">
  <p>© 2026 Urban Plate Baia Mare. Descopera localuri bune, in bugetul tau.</p>
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
    font-size: 1.4rem;
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

  .nav-links a:hover {
    color: var(--accent);
  }

  .nav-links a:hover::after {
    transform: scaleX(1);
  }

  .hero {
    min-height: 86vh;
    background: radial-gradient(circle at 20% 20%, rgba(255, 122, 61, 0.35), transparent 45%),
      radial-gradient(circle at 80% 10%, rgba(15, 118, 110, 0.35), transparent 45%),
      linear-gradient(180deg, rgba(20, 18, 16, 0.9), rgba(20, 18, 16, 0.9)),
      url('https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=1350&q=80');
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: #fff;
    padding: 100px 16px 40px;
    position: relative;
    overflow: hidden;
  }

  .hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 35% 85%, rgba(242, 201, 76, 0.18), transparent 45%);
    pointer-events: none;
  }

  .hero h1 {
    font-family: "Fraunces", serif;
    font-size: clamp(2.6rem, 4vw, 4rem);
    margin-bottom: 12px;
    letter-spacing: -0.02em;
  }

  .hero-content {
    max-width: 680px;
    padding: 0 24px;
    text-align: center;
    animation: heroFade 0.9s ease forwards;
  }

  .hero-content p {
    color: rgba(255, 255, 255, 0.82);
  }

  .hero-badges {
    margin: 18px 0 6px;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }

  .hero-badges span {
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.2);
    font-size: 0.85rem;
    letter-spacing: 0.02em;
  }

  .btn {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), #ffb347);
    color: #1b1b1b;
    padding: 12px 26px;
    text-decoration: none;
    border-radius: 999px;
    margin-top: 20px;
    border: none;
    cursor: pointer;
    font-weight: 600;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 12px 30px rgba(255, 122, 61, 0.35);
  }

  .btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 36px rgba(255, 122, 61, 0.45);
  }

  .menu-section {
    padding: 90px 8% 110px;
    text-align: center;
    position: relative;
  }

  .section-title {
    margin-bottom: 10px;
    font-family: "Fraunces", serif;
    font-size: clamp(2rem, 3vw, 2.8rem);
  }

  .section-subtitle {
    margin: 0 auto 32px;
    max-width: 520px;
    color: var(--muted);
  }

  .menu-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    justify-content: center;
    margin-bottom: 36px;
    padding: 18px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(28, 27, 26, 0.08);
    box-shadow: 0 12px 30px rgba(28, 27, 26, 0.08);
  }

  .menu-filters input {
    padding: 12px 16px;
    border: 1px solid transparent;
    border-radius: 999px;
    min-width: 220px;
    outline: none;
    background: #fff;
    font-family: inherit;
    transition: border 0.2s ease, box-shadow 0.2s ease;
  }

  .menu-filters input:focus {
    border-color: rgba(255, 122, 61, 0.6);
    box-shadow: 0 0 0 3px rgba(255, 122, 61, 0.2);
  }

  .filter-btn {
    padding: 10px 22px;
    border: none;
    background: var(--accent-2);
    color: #fff;
    cursor: pointer;
    border-radius: 999px;
    transition: 0.3s;
    font-weight: 600;
  }

  .filter-btn:hover {
    filter: brightness(1.05);
    transform: translateY(-1px);
  }

  .preparate-rapide {
    display: flex;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(28, 27, 26, 0.1);
  }

  .tag-btn {
    background: #fff;
    border: 1px solid rgba(28, 27, 26, 0.12);
    color: #1f1d1b;
    padding: 8px 16px;
    border-radius: 999px;
    cursor: pointer;
    font-weight: 500;
    font-size: 0.88rem;
    transition: all 0.25s ease;
  }

  .tag-btn:hover {
    background: rgba(255, 107, 61, 0.1);
    border-color: var(--accent);
  }

  .tag-btn.activ {
    background: var(--accent-2);
    color: #fff;
    border-color: var(--accent-2);
    font-weight: 600;
  }

  .reset-btn {
    background: transparent;
    border: none;
    color: #b91c1c;
    cursor: pointer;
    font-weight: 600;
    padding: 6px 12px;
    font-size: 0.85rem;
  }

  .menu-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 22px;
  }

  .menu-item {
    background: var(--surface);
    border: 1px solid rgba(28, 27, 26, 0.08);
    padding: 18px;
    border-radius: 18px;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    text-align: left;
    box-shadow: 0 12px 24px rgba(15, 12, 10, 0.08);
    animation: cardRise 0.6s ease forwards;
    opacity: 0;
    transform: translateY(18px);
    animation-delay: var(--delay, 0ms);
  }

  .menu-item:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow);
  }

  .restaurant-img {
    width: 100%;
    height: 170px;
    object-fit: cover;
    border-radius: 14px;
    margin-bottom: 12px;
    transition: transform 0.3s ease;
  }

  .menu-item:hover .restaurant-img {
    transform: scale(1.03);
  }

  .item-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 12px;
  }

  .price {
    color: var(--accent-2);
    font-weight: 600;
    font-size: 1.05rem;
  }

  .site-btn {
    background: #1f1d1b;
    margin-top: 12px;
    padding: 8px 16px;
    color: #fff;
  }

  .site-btn:hover {
    background: #0f0e0d;
  }

  .mesaj-gol {
    margin-top: 24px;
    font-weight: 600;
    color: var(--muted);
  }

  .mesaj-eroare {
    color: #b91c1c;
  }

  footer {
    background: #141210;
    color: #f3efe9;
    text-align: center;
    padding: 24px 16px;
  }

  @media (max-width: 700px) {
    .hero h1 {
      font-size: 2.2rem;
    }

    .menu-filters {
      padding: 14px;
    }
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

  @keyframes cardRise {
    from {
      opacity: 0;
      transform: translateY(18px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>

```