import { create } from 'zustand'
import { api, post, tokens } from '@/lib/api'

export type Workspace = { id: string; name: string; slug: string; plan: string; onboarding_completed: boolean }
export type User = { id: number; email: string; full_name: string; current_workspace: Workspace | null; workspaces: Workspace[] }

type AuthState = {
  user: User | null
  loading: boolean
  bootstrap: () => Promise<void>
  login: (email: string, password: string) => Promise<void>
  register: (payload: { email: string; password: string; full_name: string; company_name: string }) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: true,
  bootstrap: async () => {
    if (!tokens.access) { set({ loading: false }); return }
    try {
      const { data } = await api.get<User>('/auth/me/')
      set({ user: data, loading: false })
    } catch {
      tokens.clear()
      set({ user: null, loading: false })
    }
  },
  login: async (email, password) => {
    const data = await post<{ user: User; access: string; refresh: string }>('/auth/login/', { email, password })
    tokens.set(data.access, data.refresh)
    set({ user: data.user })
  },
  register: async (payload) => {
    const data = await post<{ user: User; access: string; refresh: string }>('/auth/register/', payload)
    tokens.set(data.access, data.refresh)
    set({ user: data.user })
  },
  logout: () => { tokens.clear(); set({ user: null }) },
  refreshUser: async () => {
    const { data } = await api.get<User>('/auth/me/')
    set({ user: data })
  },
}))

window.addEventListener('gtm:logout', () => useAuth.getState().logout())
