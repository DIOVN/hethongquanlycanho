// SAMS - Zustand Auth Store
// Quản lý trạng thái xác thực toàn cục: user, tokens, actions
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '@/lib/apiClient'

const useAuthStore = create(
  persist(
    (set, get) => ({
      // --- State ---
      user: null,         // { id, username, full_name, role }
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      // --- Actions ---
      login: async (username, password) => {
        const response = await apiClient.post('/auth/login', { username, password })
        const data = response.data.data

        // Lưu tokens vào localStorage và state
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)

        set({
          user: data.user,
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          isAuthenticated: true,
        })

        return data.user
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      refreshProfile: async () => {
        try {
          const response = await apiClient.get('/auth/me')
          set({ user: response.data.data })
        } catch {
          get().logout()
        }
      },

      // Kiểm tra role helpers
      isAdmin: () => get().user?.role === 'admin',
      isLandlord: () => ['admin', 'landlord'].includes(get().user?.role),
      isTenant: () => get().user?.role === 'tenant',
    }),
    {
      name: 'sams-auth',
      // Chỉ persist user info, không persist tokens (đã lưu trong localStorage)
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

export default useAuthStore
