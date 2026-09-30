// SAMS - Login Page
import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import useAuthStore from '@/stores/authStore'

export default function LoginPage() {
  const { login } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/dashboard'
  const [loading, setLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await login(data.username, data.password)
      toast.success('Đăng nhập thành công!')
      navigate(from, { replace: true })
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Tên đăng nhập hoặc mật khẩu không đúng.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white tracking-tight">SAMS</h1>
          <p className="text-primary-200 mt-1 text-sm">Hệ thống Quản lý Căn hộ Thông minh</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-3xl shadow-modal p-8">
          <h2 className="text-xl font-semibold text-slate-800 mb-6">Đăng nhập</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="label">Tên đăng nhập</label>
              <input
                className={`input ${errors.username ? 'input-error' : ''}`}
                placeholder="Nhập tên đăng nhập..."
                {...register('username', { required: 'Vui lòng nhập tên đăng nhập' })}
              />
              {errors.username && (
                <p className="text-xs text-danger-500 mt-1">{errors.username.message}</p>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="label mb-0">Mật khẩu</label>
                <Link
                  to="/forgot-password"
                  className="text-xs text-primary-600 hover:text-primary-700 font-medium hover:underline"
                >
                  Quên mật khẩu?
                </Link>
              </div>
              <input
                type="password"
                className={`input ${errors.password ? 'input-error' : ''}`}
                placeholder="••••••••"
                {...register('password', { required: 'Vui lòng nhập mật khẩu' })}
              />
              {errors.password && (
                <p className="text-xs text-danger-500 mt-1">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-2.5 mt-2"
            >
              {loading ? <span className="spinner" /> : null}
              {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            Chưa có tài khoản?{' '}
            <Link to="/register" className="text-primary-600 font-medium hover:underline">
              Đăng ký ngay
            </Link>
          </p>
          <p className="text-center text-sm text-slate-500 mt-2">
            Tìm phòng trống?{' '}
            <Link to="/rooms/search" className="text-primary-600 font-medium hover:underline">
              Xem phòng cho thuê
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
