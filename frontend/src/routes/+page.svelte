<script>
  import { onMount } from 'svelte';

  let dateRestaurante = $state([]);
  let isLoading = $state(false);
  let error = $state('');

  let bugetMaxim = $state('');
  let bugetMinim = $state('');
  let specific = $state('');
  let cautare = $state('');

  const apiBaseUrl = () =>
    typeof window !== 'undefined' && window.API_BASE_URL
      ? window.API_BASE_URL
      : 'http://127.0.0.1:8000/api';

  async function incarcaRestaurante() {
    isLoading = true;
    error = '';

    const parametri = new URLSearchParams();
    parametri.set('limit', '500');

    const bugetVal = Number(bugetMaxim);
    if (!Number.isNaN(bugetVal) && bugetVal > 0) {
      parametri.set('max_budget', bugetVal.toString());
    }

    if (specific.trim().length > 0) {
      parametri.set('specific', specific.trim());
    }

    if (cautare.trim().length > 0) {
      parametri.set('q', cautare.trim());
    }

    const url = `${apiBaseUrl()}/restaurants?${parametri.toString()}`;

    try {
      const raspuns = await fetch(url);
      if (!raspuns.ok) {
        throw new Error(`Eroare API: ${raspuns.status}`);
      }
      const data = await raspuns.json();
      dateRestaurante = Array.isArray(data) ? data : [];
    } catch (err) {
      console.error('Nu am putut incarca restaurantele:', err);
      error = 'Nu am putut incarca datele din backend.';
      dateRestaurante = [];
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    incarcaRestaurante();
  });
</script>

<main>
  <header class="hero">
    <div>
      <p class="kicker">Urban Plate</p>
      <h1>Restaurante in Baia Mare</h1>
      <p class="subtext">Cauta dupa buget, specific sau cuvinte cheie.</p>
    </div>
  </header>
  <section class="filtre">
    <div class="camp">
      <label for="bugetMaxim">Buget maxim</label>
      <input
        id="bugetMaxim"
        type="number"
        min="1"
        step="1"
        bind:value={bugetMaxim}
        placeholder="ex: 60"
      />
    </div>
    <div class="camp">
      <label for="specific">Specific</label>
      <input id="specific" type="text" bind:value={specific} placeholder="ex: Romanesc" />
    </div>
    <div class="camp">
      <label for="cautare">Cautare</label>
      <input id="cautare" type="text" bind:value={cautare} placeholder="nume, locatie" />
    </div>
    <button class="btn" onclick={incarcaRestaurante}>Cauta</button>
  </section>
  
  {#if isLoading}
    <p class="status">Se incarca restaurantele...</p>
  {:else if error}
    <p class="status error">{error}</p>
  {:else if dateRestaurante.length === 0}
    <p class="status">Nu am gasit restaurante pentru filtrele curente.</p>
  {:else}
    <section class="lista">
      {#each dateRestaurante as r}
        <article class="card">
          <img src={r.imagine} alt={r.nume} />
          <div class="card-body">
            <h3>{r.nume}</h3>
            <p class="meta">{r.specific} · {r.locatie}</p>
            <p class="pret">Buget mediu: {r.buget} RON</p>
            <div class="actiuni">
              <a class="btn ghost" href={`/restaurants/${r.slug}`}>Detalii</a>
              {#if r.linkOficial}
                <a class="btn" href={r.linkOficial} target="_blank" rel="noopener noreferrer">
                  Pagina oficiala
                </a>
              {/if}
            </div>
          </div>
        </article>
      {/each}
    </section>
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    color: #1f2937;
    background: radial-gradient(circle at top left, #fef3c7, #fff 55%);
  }

  main {
    padding: 32px 24px 48px;
    max-width: 1100px;
    margin: 0 auto;
  }

  .hero {
    display: grid;
    gap: 8px;
    margin-bottom: 24px;
  }

  .kicker {
    text-transform: uppercase;
    letter-spacing: 0.2em;
    font-size: 0.75rem;
    color: #b45309;
    margin: 0;
  }

  h1 {
    margin: 0;
    font-size: 2.2rem;
    color: #111827;
  }

  .subtext {
    margin: 0;
    color: #4b5563;
  }

  .filtre {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    align-items: end;
    background: #fff7ed;
    padding: 16px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  }

  .camp {
    display: grid;
    gap: 6px;
  }

  label {
    font-size: 0.85rem;
    color: #78350f;
  }

  input {
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid #fcd34d;
    background: #fff;
  }

  .btn {
    background: #f97316;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    cursor: pointer;
    font-weight: 600;
  }

  .btn.ghost {
    background: #fff;
    color: #f97316;
    border: 1px solid #f97316;
  }

  .status {
    margin-top: 24px;
    color: #6b7280;
  }

  .status.error {
    color: #b91c1c;
  }

  .lista {
    margin-top: 24px;
    display: grid;
    gap: 20px;
  }

  .card {
    display: grid;
    grid-template-columns: 160px 1fr;
    gap: 16px;
    padding: 16px;
    border-radius: 16px;
    background: #fff;
    box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
  }

  .card img {
    width: 100%;
    height: 120px;
    object-fit: cover;
    border-radius: 12px;
  }

  .card-body {
    display: grid;
    gap: 6px;
  }

  .meta {
    color: #6b7280;
    margin: 0;
  }

  .pret {
    font-weight: 600;
    color: #111827;
    margin: 0;
  }

  .actiuni {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 8px;
  }

  @media (max-width: 700px) {
    .card {
      grid-template-columns: 1fr;
    }
  }
</style>