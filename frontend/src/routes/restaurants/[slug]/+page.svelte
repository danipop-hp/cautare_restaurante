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

<main>
  <a class="back" href="/">← Inapoi la lista</a>

  {#if isLoading}
    <p class="status">Se incarca detaliile...</p>
  {:else if error}
    <p class="status error">{error}</p>
  {:else if restaurant}
    <section class="hero">
      <img src={restaurant.imagine} alt={restaurant.nume} />
      <div>
        <h1>{restaurant.nume}</h1>
        <p class="meta">{restaurant.specific} · {restaurant.locatie}</p>
        <p class="pret">Buget mediu: {restaurant.buget} RON</p>
        {#if restaurant.linkOficial}
          <a class="btn" href={restaurant.linkOficial} target="_blank" rel="noopener noreferrer">
            Pagina oficiala
          </a>
        {/if}
      </div>
    </section>

    <section class="meniu">
      <h2>Meniu</h2>
      {#if restaurant.meniu && restaurant.meniu.length > 0}
        <ul>
          {#each restaurant.meniu as produs}
            <li>
              <span>{produs.numeProdus}</span>
              <strong>{produs.pret} RON</strong>
            </li>
          {/each}
        </ul>
      {:else}
        <p class="status">Nu exista meniu disponibil pentru acest restaurant.</p>
      {/if}
    </section>
  {/if}
</main>

<style>
  main {
    max-width: 980px;
    margin: 0 auto;
    padding: 32px 24px 48px;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    color: #1f2937;
  }

  .back {
    display: inline-block;
    margin-bottom: 16px;
    color: #f97316;
    text-decoration: none;
    font-weight: 600;
  }

  .hero {
    display: grid;
    grid-template-columns: 1.1fr 1fr;
    gap: 20px;
    background: #fff;
    padding: 16px;
    border-radius: 16px;
    box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
  }

  .hero img {
    width: 100%;
    height: 260px;
    object-fit: cover;
    border-radius: 12px;
  }

  .meta {
    color: #6b7280;
    margin: 4px 0;
  }

  .pret {
    font-weight: 600;
    margin: 8px 0 16px;
  }

  .btn {
    background: #f97316;
    color: #fff;
    padding: 10px 16px;
    border-radius: 10px;
    text-decoration: none;
    display: inline-block;
  }

  .meniu {
    margin-top: 28px;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 12px 0 0;
    display: grid;
    gap: 10px;
  }

  li {
    display: flex;
    justify-content: space-between;
    background: #fff7ed;
    padding: 10px 14px;
    border-radius: 10px;
  }

  .status {
    color: #6b7280;
  }

  .status.error {
    color: #b91c1c;
  }

  @media (max-width: 800px) {
    .hero {
      grid-template-columns: 1fr;
    }
  }
</style>
