function normalizeBaseUrl(url) {
  return url.replace(/\/+$/, '');
}

export function getApiBaseUrl() {
  if (typeof window === 'undefined') {
    return '/api';
  }

  const customBaseUrl = window.API_BASE_URL;
  if (typeof customBaseUrl === 'string' && customBaseUrl.trim().length > 0) {
    return normalizeBaseUrl(customBaseUrl.trim());
  }

  return '/api';
}