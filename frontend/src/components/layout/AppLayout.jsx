import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Building2,
  FileText,
  AlertTriangle,
  Wrench,
  Search,
  LayoutDashboard,
  LogOut,
  User,
  Menu,
  X,
  Sparkles,
} from 'lucide-react'
import useAuthStore from '@/stores/authStore'
import ChatWidget from '@/components/chat/ChatWidget'

export default function AppLayout({ children }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const isLandlordOrAdmin = user?.role === 'landlord' || user?.role === 'admin'

  const navItems = [
    { label: 'Tổng quan', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Hóa đơn & VietQR', path: '/invoices', icon: FileText },
    { label: 'Vi phạm nội quy', path: '/violations', icon: AlertTriangle },
    { label: 'Báo hỏng & Sửa chữa', path: '/tickets', icon: Wrench },
    { label: 'Tìm phòng trống', path: '/rooms/search', icon: Search },
    ...(isLandlordOrAdmin
      ? [{ label: 'Quản lý phòng', path: '/rooms', icon: Building2 }]
      : []),
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const roleBadge = {
    admin: { label: 'Admin', color: 'bg-purple-100 text-purple-700' },
    landlord: { label: 'Chủ nhà', color: 'bg-blue-100 text-blue-700' },
    tenant: { label: 'Khách thuê', color: 'bg-emerald-100 text-emerald-700' },
  }[user?.role || 'tenant']

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <Link to="/dashboard" className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-primary-500 flex items-center justify-center text-white shadow-md shadow-indigo-200">
                  <Building2 className="w-6 h-6" />
                </div>
                <div>
                  <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-slate-900 to-indigo-900 bg-clip-text text-transparent">
                    SAMS
                  </span>
                  <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
                    Smart Apartment
                  </span>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-xl transition-all duration-150 ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700 font-semibold shadow-xs'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </nav>

            {/* User Profile & Actions */}
            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-2.5 pl-3 border-l border-slate-200">
                <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600">
                  <User className="w-4 h-4" />
                </div>
                <div className="text-left text-xs">
                  <div className="font-semibold text-slate-800 leading-tight">
                    {user?.full_name || user?.username || 'Cư dân'}
                  </div>
                  <span className={`inline-block px-1.5 py-0.2 rounded text-[10px] font-medium mt-0.5 ${roleBadge.color}`}>
                    {roleBadge.label}
                  </span>
                </div>
              </div>

              <button
                onClick={handleLogout}
                title="Đăng xuất"
                className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors ml-1"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>

            {/* Mobile Hamburger Button */}
            <div className="flex md:hidden items-center gap-2">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-xl text-slate-600 hover:bg-slate-100"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 font-semibold'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-5 h-5 text-indigo-600" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
            <div className="pt-3 mt-2 border-t border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${roleBadge.color}`}>
                  {roleBadge.label}
                </span>
                <span className="text-sm font-medium text-slate-700">
                  {user?.full_name || user?.username}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-lg"
              >
                <LogOut className="w-3.5 h-3.5" />
                Đăng xuất
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Main Page Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>

      {/* Floating Gemini AI Chat Assistant Widget */}
      <ChatWidget />
    </div>
  )
}
