import axios, { AxiosError } from 'axios'

export const API_URL = import.meta.env.VITE_API_URL || '/api'

const TOKEN_KEY = 'gtm.access'
const REFRESH_KEY = 'gtm.refresh'

export const tokens = {
  get access() { try { return localStorage.getItem(TOKEN_KEY) } catch { return null } },
  get refresh() { try { return localStorage.getItem(REFRESH_KEY) } catch { return null } },
  set(access: string, refresh?: string) {
    try {
      localStorage.setItem(TOKEN_KEY, access)
      if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
    } catch { /* private mode */ }
  },
  clear() { try { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(REFRESH_KEY) } catch { /* noop */ } },
}

export const api = axios.create({ baseURL: API_URL, headers: { 'Content-Type': 'application/json' } })

api.interceptors.request.use((config) => {
  const t = tokens.access
  if (t) config.headers.Authorization = `Bearer ${t}`
  return config
})

let refreshing: Promise<string | null> | null = null

async function refreshAccess(): Promise<string | null> {
  const r = tokens.refresh
  if (!r) return null
  try {
    const { data } = await axios.post(`${API_URL}/auth/refresh/`, { refresh: r })
    tokens.set(data.access, data.refresh)
    return data.access
  } catch {
    tokens.clear()
    return null
  }
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as (typeof error.config & { _retried?: boolean }) | undefined
    if (error.response?.status === 401 && original && !original._retried && !original.url?.includes('/auth/')) {
      original._retried = true
      refreshing ??= refreshAccess().finally(() => { refreshing = null })
      const access = await refreshing
      if (access) {
        original.headers.Authorization = `Bearer ${access}`
        return api(original)
      }
      window.dispatchEvent(new CustomEvent('gtm:logout'))
    }
    return Promise.reject(error)
  },
)

export function errorMessage(e: unknown): string {
  if (axios.isAxiosError(e)) {
    const d = e.response?.data as Record<string, unknown> | undefined
    if (!d) return e.message
    if (typeof d.detail === 'string') return d.detail
    const first = Object.values(d)[0]
    if (Array.isArray(first)) return String(first[0])
    if (typeof first === 'string') return first
  }
  return e instanceof Error ? e.message : 'Something went wrong'
}

// ---- typed helpers ---------------------------------------------------------
export type Paginated<T> = { count: number; next: string | null; previous: string | null; results: T[] }

export const get = async <T,>(url: string, params?: Record<string, unknown>) => (await api.get<T>(url, { params })).data
export const post = async <T,>(url: string, body?: unknown) => (await api.post<T>(url, body)).data
export const patch = async <T,>(url: string, body?: unknown) => (await api.patch<T>(url, body)).data
export const del = async <T,>(url: string) => (await api.delete<T>(url)).data
