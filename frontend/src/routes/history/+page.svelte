<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/auth';
  onMount(() => isAuthenticated() ? goto('/account') : goto('/login'));
</script>
<p>Se verifica autentificarea...</p>
