const API_ORIGIN =
  window.location.port === "5173"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : window.location.origin;

const TOKEN_KEY = "laliga_predictor_token";
const REFRESH_KEY = "laliga_predictor_refresh";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

export function setRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export class ApiRequestError extends Error {
  code: string;
  status: number;
  constructor(message: string, code: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

const MAX_RETRIES = 2;
const REQUEST_TIMEOUT_MS = 30000;

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function tryRefreshToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;
  try {
    const res = await fetch(`${API_ORIGIN}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    setToken(data.access_token);
    setRefreshToken(data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  let lastError: ApiRequestError | null = null;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    const token = getToken();
    const headers: Record<string, string> = {
      ...((options.headers as Record<string, string>) || {}),
    };
    if (options.body) headers["Content-Type"] = "application/json";
    if (token) headers.Authorization = `Bearer ${token}`;

    try {
      const response = await fetchWithTimeout(
        `${API_ORIGIN}${path}`,
        { ...options, headers },
        REQUEST_TIMEOUT_MS,
      );
      const payload = await response.json().catch(() => ({}));

      if (response.status === 401 && attempt === 0 && path !== "/api/v1/auth/refresh") {
        const refreshed = await tryRefreshToken();
        if (refreshed) continue;
      }

      if (!response.ok) {
        if (response.status === 401) clearToken();
        throw new ApiRequestError(
          payload.message || "Ocurrió un error inesperado.",
          payload.error || "UNKNOWN_ERROR",
          response.status,
        );
      }
      return payload as T;
    } catch (err) {
      if (err instanceof ApiRequestError) {
        if (err.status >= 400 && err.status < 500) throw err;
        lastError = err;
      } else {
        lastError = new ApiRequestError(
          "No se pudo conectar con el servidor.",
          "NETWORK_ERROR",
          0,
        );
      }
      if (attempt < MAX_RETRIES) {
        await new Promise((r) => setTimeout(r, 500 * (attempt + 1)));
      }
    }
  }
  throw lastError!;
}
