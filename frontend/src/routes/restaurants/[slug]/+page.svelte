<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  let restaurant = $state(null);
  let isLoading = $state(false);
  let error = $state('');

  const apiBaseUrl = () =>
    typeof window !== 'undefined' && window.API_BASE_URL
      ? window.API_BASE_URL
      : 'http://127.0.0.1:8000/api';

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

  onMount(() => {
    incarcaRestaurant();
  });
</script>

<nav class="navbar">
  <div class="logo">Urban<span>Plate</span></div>
  <ul class="nav-links">
    <li><a href="/#home">Acasa</a></li>
    <li><a href="/#menu">Cautare</a></li>
    <li class="nav-break"><a href="/#contact">Contact</a></li>
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
      <img class="detalii-imagine" src={restaurant.imagine} alt={restaurant.nume} />
      <p><strong>Specific:</strong> {restaurant.specific}</p>
      <p><strong>Locatie:</strong> {restaurant.locatie}</p>
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
  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 2%;
    background: #fff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
  }

  .logo {
    font-size: 1.2rem;
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

  .nav-links .nav-break {
    flex-basis: 100%;
    display: flex;
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
    color: #e67e22;
  }

  .detalii-main {
    min-height: 100vh;
    padding: 120px 10% 60px;
    background: #fafafa;
  }

  .detalii-card {
    max-width: 720px;
    margin: 24px auto 0;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 28px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
  }

  .detalii-card h1 {
    margin-bottom: 18px;
  }

  .detalii-imagine {
    width: 100%;
    height: 260px;
    object-fit: cover;
    border-radius: 10px;
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
    border-bottom: 1px solid #f0f0f0;
  }

  .mesaj-gol {
    margin-top: 24px;
    font-weight: 600;
    color: #666;
  }

  .mesaj-eroare {
    color: #b91c1c;
  }

  .btn {
    display: inline-block;
    background: #e67e22;
    color: #fff;
    padding: 10px 16px;
    border-radius: 5px;
    text-decoration: none;
  }

  .site-btn {
    background: #333;
    margin-top: 12px;
  }

  .site-btn:hover {
    background: #111;
  }

  footer {
    background: #333;
    color: #fff;
    text-align: center;
    padding: 20px;
  }
</style>
