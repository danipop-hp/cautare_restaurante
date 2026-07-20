<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAdminAuthenticated, storeAdminSession } from '$lib/adminAuth';
  import { getApiBaseUrl } from '$lib/api';

  let email = $state('');
  let password = $state('');
  let error = $state('');
  let isLoading = $state(false);

  const apiBaseUrl = () => getApiBaseUrl();

  onMount(() => {
    if (isAdminAuthenticated()) {
      goto('/admin');
    }
  });

  async function handleSubmit(event) {
    event.preventDefault();
    error = '';

    if (!email.trim() || !password.trim()) {
      error = 'Completeaza toate campurile pentru a continua.';
      return;
    }

    isLoading = true;

    try {
      const response = await fetch(`${apiBaseUrl()}/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password })
      });

      if (!response.ok) {
        error = 'Email sau parola gresita.';
        return;
      }

      const payload = await response.json();
      storeAdminSession({ token: payload.token, email: email.trim() });
      goto('/admin');
    } catch (err) {
      console.error('Nu am putut face login admin:', err);
      error = 'Login indisponibil momentan. Incearca din nou.';
    } finally {
      isLoading = false;
    }
  }
</script>

<main class="auth-main">
  <section class="auth-card">
    <div class="auth-header">
      <p class="auth-brand">Urban<span>Plate</span> Admin</p>
      <h1>Acces administrator</h1>
      <p class="auth-subtitle">Gestioneaza restaurantele si meniurile din platforma.</p>
    </div>

    <form class="auth-form" onsubmit={handleSubmit}>
      <label>
        Email admin
        <input type="email" bind:value={email} placeholder="admin@email.ro" required />
      </label>
      <label>
        Parola
        <input type="password" bind:value={password} placeholder="Parola" required />
      </label>

      {#if error}
        <p class="auth-error">{error}</p>
      {/if}

      <button class="btn" type="submit" disabled={isLoading}>
        {isLoading ? 'Se autentifica...' : 'Login admin'}
      </button>
    </form>

    <p class="auth-footer">
      Revii la utilizatori?
      <a href="/login">Login user</a>
    </p>
  </section>
</main>

<style>
  :global(:root) {
    --bg: #0f1117;
    --ink: #f8f3eb;
    --muted: #c0b7a9;
    --accent: #ff6b3d;
    --accent-2: #4cc9b0;
    --surface: #1b1e26;
    --surface-2: #141720;
    --shadow: 0 24px 60px rgba(8, 10, 15, 0.55);
  }

  :global(html) {
    height: 100%;
    background-color: #0f1117;
  }

  :global(body) {
    margin: 0;
    min-height: 100%;
    width: 100%;
    overflow-x: hidden;
    font-family: "Space Grotesk", system-ui, sans-serif;
    background: radial-gradient(circle at 12% 15%, rgba(76, 201, 176, 0.35) 0, transparent 45%),
      radial-gradient(circle at 85% 12%, rgba(255, 107, 61, 0.28) 0, transparent 45%),
      radial-gradient(circle at 50% 80%, rgba(244, 208, 111, 0.2) 0, transparent 55%),
      linear-gradient(180deg, #0f1117 0%, #121522 100%);
    background-position: center center;
    background-repeat: no-repeat;
    background-size: cover;
    color: var(--ink);
  }

  .auth-main {
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 1.75rem 1rem;
    width: 100%;
    box-sizing: border-box;
  }

  .auth-card {
    width: min(440px, 92vw);
    background: var(--surface);
    border-radius: 24px;
    padding: 2.5rem;
    margin: 0 auto;
    box-shadow: var(--shadow);
    border: 1px solid rgba(248, 243, 235, 0.08);
  }

  .auth-brand {
    font-weight: 700;
    margin: 0;
    font-size: 1.2rem;
  }

  .auth-brand span {
    color: var(--accent);
  }

  .auth-header h1 {
    margin: 0.4rem 0 0.6rem;
  }

  .auth-subtitle {
    margin: 0 0 1.6rem;
    color: var(--muted);
  }

  .auth-form {
    display: grid;
    gap: 1rem;
  }

  label {
    display: grid;
    gap: 0.4rem;
    font-weight: 600;
  }

  input {
    border-radius: 12px;
    border: 1px solid rgba(248, 243, 235, 0.12);
    background: var(--surface-2);
    color: var(--ink);
    padding: 0.75rem 0.9rem;
    font-size: 1rem;
  }

  .auth-error {
    color: #b42318;
    margin: 0;
    background: #ffe4e1;
    padding: 0.6rem 0.8rem;
    border-radius: 10px;
  }

  .btn {
    border: none;
    border-radius: 999px;
    padding: 0.75rem 1.4rem;
    font-weight: 600;
    background: var(--accent);
    color: #fff;
    cursor: pointer;
  }

  .btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .auth-footer {
    margin-top: 1.6rem;
    color: var(--muted);
  }

  .auth-footer a {
    color: var(--accent-2);
    text-decoration: none;
    font-weight: 600;
  }

  @media (max-width: 480px) {
    .auth-main {
      padding: 1.25rem 0.75rem;
    }

    .auth-card {
      width: 100%;
      padding: 1.5rem 1.25rem;
      border-radius: 18px;
    }

    .auth-header h1 {
      font-size: 1.4rem;
    }

    .auth-subtitle {
      font-size: 0.95rem;
    }

    input {
      font-size: 0.95rem;
      padding: 0.7rem 0.85rem;
    }

    .btn {
      width: 100%;
    }
  }
</style>
