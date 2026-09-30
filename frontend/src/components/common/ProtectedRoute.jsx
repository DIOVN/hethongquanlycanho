// SAMS - Protected Route Guard
// Ngăn chặn truy cập route khi chưa đăng nhập hoặc sai role
import { Navigate, useLocation } from 'react-router-dom'
import useAuthStore from '@/stores/authStore'

/**
 * @param {React.ReactNode} children - Component con cần bảo vệ
 * @param {string[]} allowedRoles - Danh sách roles được phép ['admin','landlord','tenant']
 *                                  Nếu undefined/empty - chỉ cần đăng nhập
 */
export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, user } = useAuthStore()
  const location = useLocation()

  // Chưa đăng nhập -> về trang login, lưu lại intended URL
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Kiểm tra role nếu được chỉ định
  if (allowedRoles && allowedRoles.length > 0) {
    const hasRole = allowedRoles.includes(user?.role)
    // Admin luôn có quyền tối cao
    const isAdmin = user?.role === 'admin'
    if (!hasRole && !isAdmin) {
      return <Navigate to="/unauthorized" replace />
    }
  }

  return children
}
