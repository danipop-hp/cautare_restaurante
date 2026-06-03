import { browser } from '$app/environment';

const AUTH_KEY = 'urbanplate-auth';
const ADMIN_TOKEN_KEY = 'urbanplate-admin-token';
const USERS_KEY = 'urbanplate-users';

function getUsers() {
  if (!browser) {
    return [];
  }
  const raw = localStorage.getItem(USERS_KEY);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveUsers(users) {
  if (!browser) {
    return;
  }
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export function isAuthenticated() {
  if (!browser) {
    return false;
  }
  if (localStorage.getItem(AUTH_KEY) === '1') {
    return true;
  }
  return Boolean(localStorage.getItem(ADMIN_TOKEN_KEY));
}

export function login({ email, password }) {
  if (!browser) {
    return { ok: false, message: 'Login indisponibil in SSR.' };
  }
  const users = getUsers();
  const match = users.find(
    (user) => user.email.toLowerCase() === email.toLowerCase() && user.password === password
  );
  if (!match) {
    return { ok: false, message: 'Email sau parola gresita.' };
  }
  localStorage.setItem(AUTH_KEY, '1');
  return { ok: true };
}

export function register({ name, email, password }) {
  if (!browser) {
    return { ok: false, message: 'Register indisponibil in SSR.' };
  }
  const users = getUsers();
  const exists = users.some((user) => user.email.toLowerCase() === email.toLowerCase());
  if (exists) {
    return { ok: false, message: 'Exista deja un cont cu acest email.' };
  }
  const updated = [...users, { name, email, password }];
  saveUsers(updated);
  return { ok: true };
}

export function logout() {
  if (!browser) {
    return;
  }
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(ADMIN_TOKEN_KEY);
  localStorage.removeItem('urbanplate-admin-email');
}
