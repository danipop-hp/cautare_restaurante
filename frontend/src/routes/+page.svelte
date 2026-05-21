<script>
  let dateRestaurante = $state([]);
  let isLoading = $state(false);
  let error = $state('');
  let statusMessage = $state('Introdu un buget si apasa Cauta pentru a vedea restaurantele.');

  let bugetMaxim = $state('');
  let specific = $state('');
  let cautare = $state('');

  const apiBaseUrl = () =>
    typeof window !== 'undefined' && window.API_BASE_URL
      ? window.API_BASE_URL
      : 'http://127.0.0.1:8000/api';

  function buildMapsLink(numeRestaurant, locatieRestaurant) {
    const interogare = encodeURIComponent(`${numeRestaurant} ${locatieRestaurant}`);
    return `https://www.google.com/maps/search/?api=1&query=${interogare}`;
  }

  async function incarcaRestaurante() {
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
  </ul>
</nav>

<header id="home" class="hero">
  <div class="hero-content">
    <h1>Gaseste rapid cel mai potrivit restaurant din Baia Mare</h1>
    <p>Compara optiuni reale dupa buget, specific culinar si locatie.</p>
    <a href="#menu" class="btn">Incepe Cautarea</a>
  </div>
</header>

<section id="menu" class="menu-section">
  <h2 class="section-title">Motor de Cautare Restaurante Baia Mare</h2>

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
  </div>

  {#if isLoading}
    <p class="mesaj-gol">Se incarca restaurantele...</p>
  {:else if error}
    <p class="mesaj-gol mesaj-eroare">{error}</p>
  {:else}
    <div class="menu-container">
      {#each dateRestaurante as r}
        {@const linkRestaurant = r.linkOficial && r.linkOficial.trim() !== ''
          ? r.linkOficial
          : buildMapsLink(r.nume, r.locatie)}
        <article class="menu-item">
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
  <p>&copy; 2026 Urban Plate Baia Mare. Descopera localuri bune, in bugetul tau.</p>
</footer>

<style>
  :global(body) {
    margin: 0;
    font-family: "Poppins", sans-serif;
    line-height: 1.6;
    color: #333;
    scroll-behavior: smooth;
    background: #fff;
  }

  :global(a) {
    color: inherit;
  }

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 1%;
    background: #fff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: fixed;
    width: 100%;
    box-sizing: border-box;
    top: 0;
    z-index: 1000;
  }

  .logo {
    font-size: 1.3rem;
    font-weight: 600;
  }

  .logo span {
    color: #e67e22;
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
    color: #333;
    transition: color 0.3s;
    font-size: 0.85rem;
    white-space: nowrap;
    padding: 2px 4px;
  }

  .nav-links a:hover {
    color: #e67e22;
  }

  .hero {
    height: 80vh;
    background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
      url('https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=1350&q=80');
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: #fff;
    padding-top: 60px;
  }

  .hero h1 {
    font-size: 3rem;
    margin-bottom: 10px;
  }

  .hero-content {
    max-width: 720px;
    padding: 0 24px;
  }

  .btn {
    display: inline-block;
    background: #e67e22;
    color: #fff;
    padding: 10px 25px;
    text-decoration: none;
    border-radius: 5px;
    margin-top: 20px;
    border: none;
    cursor: pointer;
  }

  .menu-section {
    padding: 80px 10%;
    text-align: center;
  }

  .section-title {
    margin-bottom: 40px;
    font-size: 2.5rem;
  }

  .menu-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
    margin-bottom: 30px;
  }

  .menu-filters input {
    padding: 10px 14px;
    border: 1px solid #ddd;
    border-radius: 20px;
    min-width: 220px;
    outline: none;
  }

  .filter-btn {
    padding: 8px 20px;
    border: none;
    background: #f4f4f4;
    cursor: pointer;
    border-radius: 20px;
    transition: 0.3s;
  }

  .filter-btn:hover {
    background: #e67e22;
    color: #fff;
  }

  .menu-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
  }

  .menu-item {
    background: #fff;
    border: 1px solid #eee;
    padding: 20px;
    border-radius: 10px;
    transition: transform 0.3s;
  }

  .menu-item:hover {
    transform: translateY(-5px);
  }

  .restaurant-img {
    width: 100%;
    height: 160px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 12px;
  }

  .item-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 12px;
    justify-content: center;
  }

  .price {
    color: #e67e22;
    font-weight: 600;
    font-size: 1.1rem;
  }

  .site-btn {
    background: #333;
    margin-top: 12px;
    padding: 8px 16px;
  }

  .site-btn:hover {
    background: #111;
  }

  .mesaj-gol {
    margin-top: 24px;
    font-weight: 600;
    color: #666;
  }

  .mesaj-eroare {
    color: #b91c1c;
  }

  footer {
    background: #333;
    color: #fff;
    text-align: center;
    padding: 20px;
  }

  @media (max-width: 700px) {
    .hero h1 {
      font-size: 2.2rem;
    }
  }
</style>