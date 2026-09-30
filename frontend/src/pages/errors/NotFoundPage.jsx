import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50">
      <div className="text-center">
        <p className="text-6xl font-bold text-primary-300">404</p>
        <h1 className="text-2xl font-semibold text-slate-800 mt-4">Không tìm thấy trang</h1>
        <p className="text-slate-500 mt-2 text-sm">Trang bạn truy cập không tồn tại.</p>
        <Link to="/dashboard" className="btn-primary mt-6 inline-flex">← Về trang chủ</Link>
      </div>
    </div>
  )
}
