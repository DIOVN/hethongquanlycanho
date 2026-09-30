// SAMS Frontend - Axios API Client
// Tự động gắn JWT Bearer token vào mọi request
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,  // 30s timeout (đủ dài cho AI OCR)
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: gắn access_token vào header Authorization
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: xử lý token hết hạn
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Nếu 401 và chưa thử refresh
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      error.response?.data?.error?.code === 'TOKEN_EXPIRED'
    ) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) throw new Error('No refresh token')

        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token } = response.data.data
        localStorage.setItem('access_token', access_token)

        // Retry original request với token mới
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return apiClient(originalRequest)
      } catch {
        // Refresh thất bại - đăng xuất người dùng
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
