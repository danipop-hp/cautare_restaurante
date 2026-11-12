<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { clearAdminSession, getAdminToken, isAdminAuthenticated } from '$lib/adminAuth';
  import { getApiBaseUrl } from '$lib/api';

  let restaurants = $state([]);
  let selected = $state(null);
  let loading = $state(true);
  let saving = $state(false);
  let error = $state('');
  let message = $state('');
  let form = $state({ nume: '', specific: '', buget: '', locatie: '', imagine: '', tags: '', website_url: '', menu_url: '', status: 'active' });
  const api = () => getApiBaseUrl();
  const headers = () => ({ Authorization: `Bearer ${getAdminToken()}` });

  function reset() {
    selected = null;
    form = { nume: '', specific: '', buget: '', locatie: '', imagine: '', tags: '', website_url: '', menu_url: '', status: 'active' };
  }
  function selectRestaurant(item) {
    selected = item;
    form = { ...item, tags: (item.tags ?? []).join(', '), website_url: item.website_url ?? '', menu_url: item.menu_url ?? '' };
  }
  async function load() {
    loading = true;
    const response = await fetch(`${api()}/restaurants?limit=1000`);
    if (response.ok) restaurants = await response.json();
    else error = 'Nu am putut incarca restaurantele.';
    loading = false;
  }
  async function save() {
    saving = true; error = ''; message = '';
    const payload = { ...form, buget: Number(form.buget), tags: form.tags.split(',').map((tag) => tag.trim()).filter(Boolean), website_url: form.website_url || null, menu_url: form.menu_url || null };
    const response = await fetch(selected ? `${api()}/admin/restaurants/${selected.id}` : `${api()}/admin/restaurants`, {
      method: selected ? 'PUT' : 'POST',
      headers: { ...headers(), 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (response.status === 401 || response.status === 403) { clearAdminSession(); goto('/admin/login'); return; }
    if (!response.ok) { error = 'Datele restaurantului sunt invalide.'; saving = false; return; }
    message = selected ? 'Restaurant actualizat.' : 'Restaurant creat.';
    reset(); await load(); saving = false;
  }
  async function remove() {
    if (!selected || !window.confirm('Stergi restaurantul selectat?')) return;
    const response = await fetch(`${api()}/admin/restaurants/${selected.id}`, { method: 'DELETE', headers: headers() });
    if (response.ok) { message = 'Restaurant sters.'; reset(); await load(); }
  }
  onMount(() => { if (!isAdminAuthenticated()) goto('/admin/login'); else load(); });
</script>

<main class="admin">
  <header><div><p class="eyebrow">UrbanPlate</p><h1>Administrare restaurante</h1><p>Gestioneaza doar datele de descoperire si linkurile oficiale.</p></div><button type="button" onclick={() => { clearAdminSession(); goto('/admin/login'); }}>Logout</button></header>
  {#if error}<p class="error">{error}</p>{/if}{#if message}<p class="success">{message}</p>{/if}
  <section class="layout">
    <article class="card">
      <div class="card-head"><h2>{selected ? 'Editeaza restaurant' : 'Adauga restaurant'}</h2><button type="button" onclick={reset}>Nou</button></div>
      <div class="fields">
        <label>Nume<input bind:value={form.nume} required /></label>
        <label>Specific culinar<input bind:value={form.specific} required /></label>
        <label>Buget mediu RON<input type="number" min="1" bind:value={form.buget} required /></label>
        <label>Adresa<input bind:value={form.locatie} required /></label>
        <label>Imagine URL<input bind:value={form.imagine} required /></label>
        <label>Tags, separate prin virgula<input bind:value={form.tags} placeholder="Burger, Meniul Zilei" /></label>
        <label>Website oficial<input type="url" bind:value={form.website_url} /></label>
        <label>Menu URL (Facebook/Web/PDF)<input type="url" bind:value={form.menu_url} /></label>
        <label>Status<select bind:value={form.status}><option value="active">Activ</option><option value="inactive">Inactiv</option></select></label>
      </div>
      <div class="actions"><button class="primary" type="button" onclick={save} disabled={saving}>{saving ? 'Se salveaza...' : 'Salveaza'}</button>{#if selected}<button class="danger" type="button" onclick={remove}>Sterge</button>{/if}</div>
    </article>
    <article class="card"><h2>Restaurante ({restaurants.length})</h2>{#if loading}<p>Loading...</p>{:else if restaurants.length === 0}<p>Nu exista restaurante.</p>{:else}<div class="list">{#each restaurants as item}<button class:selected={selected?.id === item.id} type="button" onclick={() => selectRestaurant(item)}><strong>{item.nume}</strong><span>{item.buget} RON · {item.status}</span></button>{/each}</div>{/if}</article>
  </section>
</main>

<style>
  :global(body){margin:0;background:#0f1117;color:#f8f3eb;font-family:system-ui,sans-serif}.admin{max-width:1200px;margin:auto;padding:2rem 1.5rem}header,.card-head{display:flex;justify-content:space-between;align-items:center;gap:1rem}header button,.card-head button{background:none;color:inherit;border:1px solid #555;border-radius:8px;padding:.5rem}.eyebrow{color:#4cc9b0;text-transform:uppercase;letter-spacing:.1em}h1{font-size:clamp(2rem,4vw,3.5rem);margin:.2rem 0}.layout{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.card{background:#1b1e26;border:1px solid #30333d;border-radius:16px;padding:1.2rem}.fields{display:grid;gap:.7rem}label{display:grid;gap:.3rem;color:#c0b7a9}input,select{background:#141720;color:#f8f3eb;border:1px solid #444;border-radius:8px;padding:.65rem}.actions{display:flex;gap:.7rem;margin-top:1rem}.primary,.danger{border:0;border-radius:999px;padding:.7rem 1rem;color:#fff}.primary{background:#ff6b3d}.danger{background:#9e3434}.list{display:grid;gap:.4rem;max-height:600px;overflow:auto}.list button{display:flex;justify-content:space-between;text-align:left;background:#141720;color:inherit;border:1px solid #30333d;border-radius:8px;padding:.7rem;cursor:pointer}.list button.selected{border-color:#4cc9b0}.list span{color:#c0b7a9}.error{color:#ff8c7a}.success{color:#4cc9b0}@media(max-width:800px){.layout{grid-template-columns:1fr}}
</style>
