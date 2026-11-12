<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authHeader, isAuthenticated, logout } from '$lib/auth';
  import { getApiBaseUrl } from '$lib/api';

  let profile = $state(null);
  let favorites = $state([]);
  let history = $state([]);
  let notifications = $state([]);
  let loading = $state(true);
  let error = $state('');
  let message = $state('');
  let unreadCount = $derived(notifications.filter((item) => !item.is_read).length);
  const api = () => getApiBaseUrl();

  async function load() {
    if (!isAuthenticated()) { goto('/login'); return; }
    const responses = await Promise.all(['me', 'me/favorites', 'me/history', 'me/notifications'].map((path) => fetch(`${api()}/${path}`, { headers: authHeader() })));
    if (responses.some((response) => response.status === 401)) { logout(); goto('/login'); return; }
    if (!responses.every((response) => response.ok)) { error = 'Nu am putut incarca datele contului.'; loading = false; return; }
    profile = await responses[0].json(); favorites = await responses[1].json(); history = await responses[2].json(); notifications = await responses[3].json(); loading = false;
  }
  async function saveProfile() {
    const response = await fetch(`${api()}/me`, { method: 'PUT', headers: { ...authHeader(), 'Content-Type': 'application/json' }, body: JSON.stringify(profile) });
    if (response.ok) { profile = await response.json(); message = 'Profil actualizat.'; } else error = 'Nu am putut salva profilul.';
  }
  async function readNotification(item) {
    if (!item.is_read) await fetch(`${api()}/me/notifications/${item.id}/read`, { method: 'POST', headers: authHeader() });
    item.is_read = true;
  }
  function signOut() { logout(); goto('/login'); }
  onMount(load);
</script>

<main class="page">
  <nav><a class="brand" href="/">Urban<span>Plate</span></a><a href="/">Cautare</a><a class="notifications-link" href="#notifications" aria-label={`Notificari necitite: ${unreadCount}`}>🔔{#if unreadCount > 0}<span class="badge">{unreadCount}</span>{/if}</a><button type="button" onclick={signOut}>Logout</button></nav>
  {#if loading}<p class="state">Loading...</p>{:else if error}<p class="state error">{error}</p>{:else}
    <header><p class="eyebrow">Asistentul tau culinar</p><h1>Profilul meu</h1><p>Pastreaza restaurantele si sursele oficiale pe care le-ai descoperit.</p></header>
    <section class="grid">
      <article class="card"><h2>Buget implicit</h2><label>Nume<input bind:value={profile.name} /></label><label>Buget maxim RON<input type="number" min="1" bind:value={profile.budget_limit} /></label><label class="check"><input type="checkbox" bind:checked={profile.notifications_enabled} /> Activeaza notificarile</label><button class="primary" type="button" onclick={saveProfile}>Salveaza profilul</button>{#if message}<p class="success">{message}</p>{/if}</article>
      <article class="card" id="notifications"><h2>🔔 Notificari ({unreadCount} necitite)</h2>{#each notifications as item}<button class:unread={!item.is_read} class="notification" type="button" onclick={() => readNotification(item)}><strong>{item.title}</strong><span>{item.message}</span><small>{item.is_read ? 'Citita' : 'Marcheaza ca citita'} · {new Date(item.created_at).toLocaleString('ro-RO')}</small></button>{:else}<p>Nu ai nicio notificare noua.</p>{/each}</article>
      <article class="card"><h2>Favorite ({favorites.length})</h2>{#each favorites as item}<a class="row" href={`/restaurants/${item.restaurant.slug}`}><strong>{item.restaurant.nume}</strong><span>{item.restaurant.buget} RON · {item.restaurant.specific}</span></a>{:else}<p>Nu ai restaurante favorite.</p>{/each}</article>
      <article class="card"><h2>Jurnal culinar</h2>{#each history as item}<div class="row"><a href={`/restaurants/${item.restaurant.slug}`}><strong>{item.restaurant.nume}</strong></a><span>Accesat la {new Date(item.accessed_at).toLocaleString('ro-RO')}</span><a href={item.restaurant.menu_url ?? item.restaurant.website_url} target="_blank" rel="noopener noreferrer">Reviziteaza</a></div>{:else}<p>Nu ai accesat inca nicio sursa oficiala.</p>{/each}</article>
    </section>
  {/if}
</main>

<style>
  :global(body){margin:0;background:#0f1117;color:#f8f3eb;font-family:system-ui,sans-serif}.page{max-width:1100px;margin:auto;padding:1rem 1.5rem 4rem}nav{display:flex;gap:1rem;align-items:center;padding:1rem 0;border-bottom:1px solid #30333d;flex-wrap:wrap}nav a{color:inherit;text-decoration:none}.brand{font-weight:700;font-size:1.3rem;margin-right:auto}.brand span{color:#ff6b3d}.notifications-link{position:relative;font-size:1.1rem}.badge{display:inline-flex;align-items:center;justify-content:center;min-width:1.2rem;height:1.2rem;margin-left:.2rem;background:#ff6b3d;color:#fff;border-radius:999px;font-size:.75rem;font-weight:700}nav button{background:none;color:inherit;border:1px solid #555;border-radius:8px;padding:.4rem .8rem}.eyebrow{color:#4cc9b0;text-transform:uppercase;letter-spacing:.1em}h1{font-size:clamp(2rem,5vw,4rem);margin:.2rem 0}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.card{background:#1b1e26;border:1px solid #30333d;border-radius:16px;padding:1.2rem}label{display:grid;gap:.3rem;color:#c0b7a9;margin-bottom:.8rem}input{background:#141720;color:#f8f3eb;border:1px solid #444;border-radius:8px;padding:.65rem}.check{display:flex;align-items:center;gap:.5rem}.check input{width:auto}.primary{background:#ff6b3d;color:#fff;border:0;border-radius:999px;padding:.7rem 1rem}.row{display:flex;flex-direction:column;gap:.2rem;padding:.7rem 0;border-bottom:1px solid #30333d;color:inherit;text-decoration:none}.row span,.notification span,.notification small{color:#c0b7a9;font-size:.9rem}.row a{color:#4cc9b0}.notification{display:grid;gap:.25rem;text-align:left;width:100%;padding:.7rem;background:none;color:inherit;border:0;border-bottom:1px solid #30333d;cursor:pointer}.notification.unread{background:#263936}.state{color:#c0b7a9}.error{color:#ff8c7a}.success{color:#4cc9b0}@media(max-width:700px){.grid{grid-template-columns:1fr}}
</style>
