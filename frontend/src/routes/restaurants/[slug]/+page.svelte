<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { authHeader, isAuthenticated, logout } from '$lib/auth';
  import { getApiBaseUrl } from '$lib/api';

  let restaurant = $state(null);
  let loading = $state(true);
  let error = $state('');
  let message = $state('');
  let favorite = $state(false);
  let isAuthed = $state(false);
  let note = $state('');
  let noteMessage = $state('');
  let voteCount = $state(0);
  let voted = $state(false);
  let collections = $state([]);
  let selectedCollection = $state('');
  let collectionMessage = $state('');

  const api = () => getApiBaseUrl();

  async function loadRestaurant() {
    try {
      const response = await fetch(`${api()}/restaurants/${encodeURIComponent($page.params.slug)}`);
      if (!response.ok) throw new Error(response.status === 404 ? 'Restaurantul nu a fost gasit.' : 'Eroare API.');
      restaurant = await response.json();
      isAuthed = isAuthenticated();
      if (isAuthed) {
        const [visitResponse, favoritesResponse, noteResponse, voteResponse, collectionsResponse] = await Promise.all([
          fetch(`${api()}/restaurants/${restaurant.id}/visit`, {
            method: 'POST',
            headers: authHeader()
          }),
          fetch(`${api()}/me/favorites`, { headers: authHeader() }),
          fetch(`${api()}/restaurants/${restaurant.id}/note`, { headers: authHeader() }),
          fetch(`${api()}/restaurants/${restaurant.id}/vote`, { headers: authHeader() }),
          fetch(`${api()}/me/collections`, { headers: authHeader() })
        ]);
        if (!visitResponse.ok) {
          console.error('Nu am putut inregistra vizita restaurantului.');
        }
        if (favoritesResponse.ok) {
          favorite = (await favoritesResponse.json()).some((item) => item.restaurant.id === restaurant.id);
        }
        if (noteResponse.ok) {
          const savedNote = await noteResponse.json();
          note = savedNote?.note ?? '';
        }
        if (voteResponse.ok) {
          const vote = await voteResponse.json();
          voteCount = vote.community_votes;
          voted = vote.voted;
        }
        if (collectionsResponse.ok) {
          collections = await collectionsResponse.json();
        }
      }
    } catch (requestError) {
      console.error('Nu am putut incarca restaurantul:', requestError);
      error = requestError.message ?? 'Nu am putut incarca detaliile.';
    } finally {
      loading = false;
    }
  }

  async function toggleFavorite() {
    if (!isAuthenticated()) {
      goto('/login');
      return;
    }
    const response = await fetch(`${api()}/restaurants/${restaurant.id}/favorite`, {
      method: favorite ? 'DELETE' : 'POST',
      headers: { ...authHeader(), 'Content-Type': 'application/json' }
    });
    if (response.ok) {
      favorite = !favorite;
      message = favorite ? 'Restaurant adaugat la favorite.' : 'Restaurant eliminat din favorite.';
    }
  }

  function getDirectLink() {
    const query = encodeURIComponent(`${restaurant.nume} ${restaurant.locatie}`);
    return `https://duckduckgo.com/?q=%5C${query}`;
  }

  function openOfficialLink(url) {
    window.open(url, '_blank', 'noopener,noreferrer');
  }

  async function saveNote() {
    const response = await fetch(`${api()}/restaurants/${restaurant.id}/note`, {
      method: 'PUT',
      headers: { ...authHeader(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ note })
    });
    if (response.ok) {
      noteMessage = note.trim() ? 'Nota personala a fost salvata.' : 'Nota personala a fost stearsa.';
    } else {
      noteMessage = 'Nu am putut salva nota personala.';
    }
  }

  async function toggleVote() {
    if (!isAuthenticated()) {
      goto('/login');
      return;
    }
    const response = await fetch(`${api()}/restaurants/${restaurant.id}/vote`, {
      method: voted ? 'DELETE' : 'POST',
      headers: authHeader()
    });
    if (response.ok) {
      const result = await response.json();
      voteCount = result.community_votes;
      voted = result.voted;
    }
  }

  async function addToCollection() {
    if (!selectedCollection) return;
    const response = await fetch(`${api()}/me/collections/${selectedCollection}/restaurants/${restaurant.id}`, {
      method: 'POST',
      headers: authHeader()
    });
    collectionMessage = response.ok ? 'Restaurant adaugat in lista.' : 'Nu am putut adauga restaurantul in lista.';
  }

  function signOut() {
    logout();
    goto('/login');
  }

  onMount(loadRestaurant);
</script>

<nav class="navbar">
  <a class="logo" href="/">Urban<span>Plate</span></a>
  <div class="links"><a href="/">Cautare</a>{#if isAuthed}<a href="/account">Contul meu</a><button type="button" onclick={signOut}>Logout</button>{:else}<a href="/login">Login</a>{/if}</div>
</nav>

<main>
  <a class="back" href="/">← Inapoi la cautare</a>
  {#if loading}<p class="state">Loading restaurant...</p>
  {:else if error}<p class="state error">{error}</p>
  {:else if restaurant}
    <article class="card">
      <img src={restaurant.imagine} alt={restaurant.nume} />
      <div class="content">
        <p class="eyebrow">{restaurant.specific}</p>
        <h1>{restaurant.nume}</h1>
        <p>{restaurant.locatie}</p>
        <p class="budget">Buget mediu: <strong>{restaurant.buget} RON</strong></p>
        <button class="vote" type="button" onclick={toggleVote}>{voted ? '👍 Ai votat' : '👍 Merita banii'} · {voteCount}</button>
        <div class="tags">{#each restaurant.tags as tag}<span>{tag}</span>{/each}</div>
        {#if message}<p class="message">{message}</p>{/if}
        <div class="actions">
          <button class="secondary" type="button" onclick={toggleFavorite}>{favorite ? '♥ La favorite' : '♡ Salveaza la favorite'}</button>
          {#if restaurant.menu_url}<button class="primary" type="button" onclick={() => openOfficialLink(getDirectLink())}>Vezi meniul oficial</button>{/if}
        </div>
        {#if isAuthed}
          <div class="note-box">
            <label for="personal-note">Nota ta personala</label>
            <textarea id="personal-note" bind:value={note} maxlength="2000" placeholder="Scrie o nota vizibila doar pentru tine..."></textarea>
            <button class="secondary" type="button" onclick={saveNote}>Salveaza nota</button>
            {#if noteMessage}<small>{noteMessage}</small>{/if}
          </div>
          {#if collections.length > 0}
            <div class="collection-box">
              <label for="collection">Adauga in lista</label>
              <div><select id="collection" bind:value={selectedCollection}><option value="">Alege o lista</option>{#each collections as collection}<option value={collection.id}>{collection.name}</option>{/each}</select><button class="secondary" type="button" onclick={addToCollection}>Adauga</button></div>
              {#if collectionMessage}<small>{collectionMessage}</small>{/if}
            </div>
          {/if}
        {/if}
        <p class="hint">UrbanPlate te redirectioneaza catre sursa oficiala. Nu stocam meniuri sau comenzi in aplicatie.</p>
      </div>
    </article>
  {/if}
</main>

<style>
  :global(body){margin:0;background:#0f1117;color:#f8f3eb;font-family:system-ui,sans-serif}.navbar{display:flex;justify-content:space-between;align-items:center;padding:1rem 5%;border-bottom:1px solid #30333d}.logo{font-size:1.3rem;font-weight:700;color:inherit;text-decoration:none}.logo span{color:#ff6b3d}.links{display:flex;gap:1rem;align-items:center}.links a,.links button{color:inherit;background:none;border:0;text-decoration:none}.back,main{color:inherit}main{max-width:1000px;margin:auto;padding:2rem 1.5rem}.back{display:inline-block;margin-bottom:1.5rem;text-decoration:none}.card{display:grid;grid-template-columns:1fr 1fr;background:#1b1e26;border-radius:20px;overflow:hidden}.card img{width:100%;height:100%;min-height:360px;object-fit:cover}.content{display:flex;flex-direction:column;gap:0.75rem;padding:2rem}.eyebrow{color:#4cc9b0;text-transform:uppercase;letter-spacing:.08em}.budget{font-size:1.2rem}.vote{width:fit-content;background:none;color:#f8f3eb;border:1px solid #4cc9b0;border-radius:999px;padding:.5rem .8rem;cursor:pointer}.tags{display:flex;gap:.5rem;flex-wrap:wrap}.tags span{background:#30333d;border-radius:999px;padding:.3rem .7rem}.actions{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1.5rem}.primary,.secondary{padding:.75rem 1rem;border-radius:999px;border:0;cursor:pointer}.primary{background:#ff6b3d;color:#fff}.secondary{background:#4cc9b0;color:#101514}.note-box,.collection-box{display:grid;gap:.5rem;margin-top:1.5rem}.note-box label,.collection-box label{color:#c0b7a9}.note-box textarea{min-height:90px;resize:vertical;background:#141720;color:#f8f3eb;border:1px solid #444;border-radius:8px;padding:.65rem}.note-box small,.collection-box small{color:#4cc9b0}.collection-box div{display:flex;gap:.5rem}.collection-box select{flex:1;background:#141720;color:#f8f3eb;border:1px solid #444;border-radius:8px;padding:.65rem}.hint,.state{color:#c0b7a9}.message{color:#4cc9b0}.error{color:#ff8c7a}@media(max-width:700px){.card{grid-template-columns:1fr}.card img{min-height:220px}}
</style>
