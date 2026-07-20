<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { clearAdminSession, getAdminToken, isAdminAuthenticated } from '$lib/adminAuth';
  import { getApiBaseUrl } from '$lib/api';

  let restaurants = $state([]);
  let selectedRestaurant = $state(null);
  let menuInput = $state('');
  let isListLoading = $state(false);
  let isDetailLoading = $state(false);
  let showDetailLoading = $state(false);
  let detailLoadingTimer = $state(null);
  let isActionLoading = $state(false);
  let error = $state('');
  let success = $state('');

  const isFormLocked = $derived(showDetailLoading || isActionLoading);

  let form = $state({
    nume: '',
    specific: '',
    buget: '',
    locatie: '',
    linkOficial: '',
    imagine: ''
  });

  const apiBaseUrl = () => getApiBaseUrl();


  function authHeader() {
    const token = getAdminToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  function resetForm() {
    selectedRestaurant = null;
    form = {
      nume: '',
      specific: '',
      buget: '',
      locatie: '',
      linkOficial: '',
      imagine: ''
    };
    menuInput = '';
  }

  function buildMenuInput(meniu) {
    return meniu.map((item) => `${item.numeProdus}|${item.pret}`).join('\n');
  }

  function parseMenuInput(raw) {
    return raw
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [numeProdus, pretRaw] = line.split('|').map((part) => part.trim());
        const pretValue = pretRaw ? String(pretRaw).replace(',', '.') : '';
        const pret = pretValue ? Number(pretValue) : Number.NaN;
        return { numeProdus: numeProdus || '', pret };
      })
      .filter((item) => item.numeProdus && !Number.isNaN(item.pret));
  }

  async function loadRestaurants() {
    isListLoading = true;
    error = '';

    try {
      const response = await fetch(`${apiBaseUrl()}/restaurants?limit=500`);
      if (!response.ok) {
        throw new Error(`Eroare API: ${response.status}`);
      }
      const data = await response.json();
      restaurants = Array.isArray(data) ? data : [];
    } catch (err) {
      console.error('Nu am putut incarca restaurantele:', err);
      error = 'Nu am putut incarca lista de restaurante.';
    } finally {
      isListLoading = false;
    }
  }

  async function selectRestaurant(slug) {
    if (!slug) {
      return;
    }

    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    isDetailLoading = true;
    if (detailLoadingTimer) {
      clearTimeout(detailLoadingTimer);
    }
    detailLoadingTimer = setTimeout(() => {
      showDetailLoading = true;
    }, 150);
    error = '';
    success = '';

    try {
      const response = await fetch(`${apiBaseUrl()}/restaurants/${encodeURIComponent(slug)}`);
      if (!response.ok) {
        throw new Error(`Eroare API: ${response.status}`);
      }

      const data = await response.json();
      selectedRestaurant = data;
      form = {
        nume: data.nume ?? '',
        specific: data.specific ?? '',
        buget: String(data.buget ?? ''),
        locatie: data.locatie ?? '',
        linkOficial: data.linkOficial ?? '',
        imagine: data.imagine ?? ''
      };
      menuInput = data.meniu ? buildMenuInput(data.meniu) : '';
    } catch (err) {
      console.error('Nu am putut incarca restaurantul:', err);
      error = 'Nu am putut incarca restaurantul selectat.';
    } finally {
      isDetailLoading = false;
      if (detailLoadingTimer) {
        clearTimeout(detailLoadingTimer);
        detailLoadingTimer = null;
      }
      showDetailLoading = false;
    }
  }

  async function saveRestaurant() {
    error = '';
    success = '';

    if (!form.nume.trim() || !form.specific.trim() || !form.locatie.trim() || !form.imagine.trim()) {
      error = 'Completeaza campurile obligatorii.';
      return;
    }

    const buget = Number(form.buget);
    if (Number.isNaN(buget) || buget <= 0) {
      error = 'Bugetul trebuie sa fie un numar valid.';
      return;
    }

    const meniu = parseMenuInput(menuInput);
    if (meniu.length === 0) {
      error = 'Adauga cel putin un produs in meniu.';
      return;
    }

    const payload = {
      nume: form.nume.trim(),
      specific: form.specific.trim(),
      buget,
      locatie: form.locatie.trim(),
      linkOficial: form.linkOficial.trim() || null,
      imagine: form.imagine.trim(),
      meniu
    };

    isActionLoading = true;

    try {
      const url = selectedRestaurant
        ? `${apiBaseUrl()}/admin/restaurants/${selectedRestaurant.id}`
        : `${apiBaseUrl()}/admin/restaurants`;

      const response = await fetch(url, {
        method: selectedRestaurant ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeader()
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          clearAdminSession();
          goto('/admin/login');
          return;
        }
        throw new Error(`Eroare API: ${response.status}`);
      }

      const saved = await response.json();
      success = selectedRestaurant ? 'Restaurant actualizat.' : 'Restaurant creat.';
      await loadRestaurants();
      selectedRestaurant = saved;
      menuInput = saved.meniu ? buildMenuInput(saved.meniu) : '';
    } catch (err) {
      console.error('Nu am putut salva restaurantul:', err);
      error = 'Nu am putut salva restaurantul.';
    } finally {
      isActionLoading = false;
    }
  }

  async function deleteRestaurant() {
    if (!selectedRestaurant) {
      return;
    }

    const confirmDelete = window.confirm('Stergi restaurantul selectat?');
    if (!confirmDelete) {
      return;
    }

    isActionLoading = true;
    error = '';
    success = '';

    try {
      const response = await fetch(`${apiBaseUrl()}/admin/restaurants/${selectedRestaurant.id}`, {
        method: 'DELETE',
        headers: {
          ...authHeader()
        }
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          clearAdminSession();
          goto('/admin/login');
          return;
        }
        throw new Error(`Eroare API: ${response.status}`);
      }

      success = 'Restaurant sters.';
      resetForm();
      await loadRestaurants();
    } catch (err) {
      console.error('Nu am putut sterge restaurantul:', err);
      error = 'Nu am putut sterge restaurantul.';
    } finally {
      isActionLoading = false;
    }
  }

  async function handleLogout() {
    try {
      await fetch(`${apiBaseUrl()}/admin/logout`, {
        method: 'POST',
        headers: {
          ...authHeader()
        }
      });
    } catch (err) {
      console.error('Logout admin a esuat:', err);
    } finally {
      clearAdminSession();
      goto('/admin/login');
    }
  }

  onMount(() => {
    if (!isAdminAuthenticated()) {
      goto('/admin/login');
      return;
    }
    loadRestaurants();
  });
</script>

<nav class="navbar">
  <div class="logo">Urban<span>Plate</span> Admin</div>
  <ul class="nav-links">
    <li><a href="/">Site public</a></li>
    <li><button class="link-btn" type="button" on:click={handleLogout}>Logout</button></li>
  </ul>
</nav>

<main class="admin-main">
  <header class="admin-hero">
    <div>
      <h1>Panou administrare restaurante</h1>
      <p>Adauga, modifica si sterge restaurante. Actualizarile se reflecta imediat in cautare.</p>
    </div>
    <button class="btn" type="button" on:click={resetForm}>Restaurant nou</button>
  </header>

  {#if error}
    <p class="message error">{error}</p>
  {/if}
  {#if success}
    <p class="message success">{success}</p>
  {/if}

  <section class="admin-grid">
    <aside class="list-panel">
      <h2>Lista restaurante</h2>
      {#if isListLoading}
        <p class="muted">Se incarca lista...</p>
      {:else if restaurants.length === 0}
        <p class="muted">Nu exista restaurante in baza de date.</p>
      {:else}
        <ul class="restaurant-list">
          {#each restaurants as r}
            <li>
              <button
                class:selected={selectedRestaurant && selectedRestaurant.id === r.id}
                type="button"
                on:click={() => selectRestaurant(r.slug)}
              >
                <span>{r.nume}</span>
                <small>{r.specific}</small>
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </aside>

    <section class="form-panel" class:form-locked={isFormLocked}>
      <h2>{selectedRestaurant ? 'Editeaza restaurant' : 'Adauga restaurant'}</h2>
      {#if showDetailLoading}
        <div class="panel-overlay" aria-hidden="true">
          <span>Se incarca detaliile...</span>
        </div>
      {/if}
      <form class="admin-form" on:submit|preventDefault={saveRestaurant}>
        <div class="grid">
          <label>
            Nume restaurant
            <input type="text" bind:value={form.nume} placeholder="Nume" required />
          </label>
          <label>
            Specific
            <input type="text" bind:value={form.specific} placeholder="Specific" required />
          </label>
          <label>
            Buget mediu (RON)
            <input
              type="number"
              min="1"
              step="1"
              bind:value={form.buget}
              placeholder="80"
              required
            />
          </label>
          <label>
            Locatie
            <input type="text" bind:value={form.locatie} placeholder="Baia Mare" required />
          </label>
          <label>
            Link oficial
            <input type="text" bind:value={form.linkOficial} placeholder="https://..." />
          </label>
          <label>
            Imagine (URL)
            <input type="text" bind:value={form.imagine} placeholder="https://..." required />
          </label>
        </div>

        <label class="menu-label">
          Meniu (linie noua: Produs|Pret)
          <textarea rows="6" bind:value={menuInput} placeholder="Pizza Margherita|34"></textarea>
        </label>

        <div class="form-actions">
          <button class="btn" type="submit" disabled={isActionLoading}>
            {selectedRestaurant ? 'Salveaza modificari' : 'Creeaza restaurant'}
          </button>
          {#if selectedRestaurant}
            <button class="btn danger" type="button" on:click={deleteRestaurant} disabled={isActionLoading}>
              Sterge restaurant
            </button>
          {/if}
        </div>
      </form>
    </section>
  </section>
</main>

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
    background: radial-gradient(circle at 12% 15%, rgba(76, 201, 176, 0.35) 0, transparent 45%),
      radial-gradient(circle at 85% 12%, rgba(255, 107, 61, 0.28) 0, transparent 45%),
      radial-gradient(circle at 50% 80%, rgba(244, 208, 111, 0.2) 0, transparent 55%),
      linear-gradient(180deg, #0f1117 0%, #121522 100%);
  }

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.7rem 3%;
    background: rgba(15, 17, 23, 0.78);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 1000;
    border-bottom: 1px solid rgba(248, 243, 235, 0.08);
  }

  .logo {
    font-size: 1.2rem;
    font-weight: 700;
  }

  .logo span {
    color: var(--accent);
  }

  .nav-links {
    display: flex;
    list-style: none;
    gap: 12px;
    margin: 0;
    padding: 0;
  }

  .nav-links a,
  .link-btn {
    text-decoration: none;
    color: var(--ink);
    font-size: 0.9rem;
    padding: 2px 4px;
    position: relative;
    transition: color 0.25s ease;
  }

  .link-btn {
    border: none;
    background: transparent;
    cursor: pointer;
  }

  .nav-links a::after,
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

  .nav-links a:hover,
  .link-btn:hover {
    color: var(--accent);
  }

  .nav-links a:hover::after,
  .link-btn:hover::after {
    transform: scaleX(1);
  }

  .admin-main {
    padding: 40px 6% 90px;
  }

  .admin-hero {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .admin-hero h1 {
    font-family: "Fraunces", serif;
    margin: 0 0 6px;
  }

  .admin-hero p {
    margin: 0;
    color: var(--muted);
  }

  .admin-grid {
    display: grid;
    grid-template-columns: minmax(240px, 1fr) 2fr;
    gap: 22px;
  }

  .list-panel,
  .form-panel {
    background: var(--surface);
    border: 1px solid rgba(248, 243, 235, 0.08);
    border-radius: 18px;
    padding: 20px;
    box-shadow: var(--shadow);
    position: relative;
  }

  .restaurant-list {
    list-style: none;
    margin: 16px 0 0;
    padding: 0;
    display: grid;
    gap: 10px;
  }

  .restaurant-list button {
    width: 100%;
    text-align: left;
    background: var(--surface-2);
    border: 1px solid transparent;
    color: var(--ink);
    padding: 12px 14px;
    border-radius: 12px;
    cursor: pointer;
    display: grid;
    gap: 4px;
  }

  .restaurant-list button.selected {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px rgba(255, 107, 61, 0.4);
  }

  .restaurant-list small {
    color: var(--muted);
  }

  .admin-form {
    display: grid;
    gap: 16px;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
  }

  label {
    display: grid;
    gap: 6px;
    font-weight: 600;
  }

  input,
  textarea {
    border-radius: 12px;
    border: 1px solid rgba(248, 243, 235, 0.12);
    background: var(--surface-2);
    color: var(--ink);
    padding: 0.75rem 0.9rem;
    font-size: 0.95rem;
  }

  textarea {
    resize: vertical;
  }

  .menu-label {
    display: grid;
    gap: 6px;
  }

  .panel-overlay {
    position: absolute;
    inset: 52px 20px 20px;
    background: rgba(15, 17, 23, 0.82);
    border-radius: 14px;
    display: grid;
    place-items: center;
    color: var(--muted);
    font-weight: 600;
    text-align: center;
    pointer-events: none;
  }

  .form-locked .admin-form {
    opacity: 0.9;
    pointer-events: none;
  }

  .form-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .btn {
    border: none;
    border-radius: 999px;
    padding: 0.7rem 1.4rem;
    font-weight: 600;
    background: var(--accent);
    color: #fff;
    cursor: pointer;
  }

  .btn.danger {
    background: #d64545;
  }

  .message {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 16px;
  }

  .message.error {
    background: #ffe4e1;
    color: #b42318;
  }

  .message.success {
    background: rgba(76, 201, 176, 0.18);
    color: #d1fae5;
  }

  .muted {
    color: var(--muted);
  }

  @media (max-width: 920px) {
    .admin-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
