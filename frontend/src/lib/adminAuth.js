import { browser } from '$app/environment';

const ADMIN_TOKEN_KEY = 'urbanplate-admin-token';
const ADMIN_EMAIL_KEY = 'urbanplate-admin-email';

export function getAdminToken() {
  if (!browser) {
    return null;
  }
  return localStorage.getItem(ADMIN_TOKEN_KEY);
}

export function isAdminAuthenticated() {
  return Boolean(getAdminToken());
}

export function storeAdminSession({ token, email }) {
  if (!browser) {
    return;
  }
  localStorage.setItem(ADMIN_TOKEN_KEY, token);
  if (email) {
    localStorage.setItem(ADMIN_EMAIL_KEY, email);
  }
}

export function clearAdminSession() {
  if (!browser) {
    return;
  }
  localStorage.removeItem(ADMIN_TOKEN_KEY);
  localStorage.removeItem(ADMIN_EMAIL_KEY);
}
