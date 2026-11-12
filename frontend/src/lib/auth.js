import { browser } from '$app/environment';
import { getApiBaseUrl } from '$lib/api';

const AUTH_TOKEN_KEY = 'urbanplate-auth-token';
const AUTH_USER_KEY = 'urbanplate-auth-user';

function saveSession(data) {
  if (!browser) return;
  localStorage.setItem(AUTH_TOKEN_KEY, data.token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify({ name: data.name, role: data.role }));
}

export function getAuthToken() {
  return browser ? localStorage.getItem(AUTH_TOKEN_KEY) : null;
}

export function authHeader() {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function isAuthenticated() {
  return Boolean(getAuthToken());
}

export async function login({ email, password }) {
  try {
    const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (!response.ok) return { ok: false, message: data.detail ?? 'Email sau parola gresita.' };
    saveSession(data);
    return { ok: true };
  } catch (error) {
    console.error('Login API failed:', error);
    return { ok: false, message: 'Backend-ul nu este disponibil.' };
  }
}

export async function register({ name, email, password }) {
  try {
    const response = await fetch(`${getApiBaseUrl()}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await response.json();
    if (!response.ok) return { ok: false, message: data.detail ?? 'Nu am putut crea contul.' };
    saveSession(data);
    return { ok: true };
  } catch (error) {
    console.error('Register API failed:', error);
    return { ok: false, message: 'Backend-ul nu este disponibil.' };
  }
}

export function logout() {
  if (!browser) return;
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
  localStorage.removeItem('urbanplate-admin-token');
  localStorage.removeItem('urbanplate-admin-email');
}
