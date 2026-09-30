// SAMS - App Router & Root Component
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import ProtectedRoute from '@/components/common/ProtectedRoute'

// --- Lazy imports (Code Splitting) ---
import { lazy, Suspense } from 'react'

const LoginPage       = lazy(() => import('@/pages/auth/LoginPage'))
const RegisterPage    = lazy(() => import('@/pages/auth/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('@/pages/auth/ForgotPasswordPage'))
const DashboardPage   = lazy(() => import('@/pages/dashboard/DashboardPage'))
const RoomsPage       = lazy(() => import('@/pages/rooms/RoomsPage'))
const RoomDetailPage  = lazy(() => import('@/pages/rooms/RoomDetailPage'))
const RoomSearchPage  = lazy(() => import('@/pages/rooms/RoomSearchPage'))
const InvoicesPage    = lazy(() => import('@/pages/invoices/InvoicesPage'))
const TicketsPage     = lazy(() => import('@/pages/tickets/TicketsPage'))
const ViolationsPage  = lazy(() => import('@/pages/violations/ViolationsPage'))
const ReportsPage     = lazy(() => import('@/pages/reports/ReportsPage'))
const UnauthorizedPage = lazy(() => import('@/pages/errors/UnauthorizedPage'))
const NotFoundPage    = lazy(() => import('@/pages/errors/NotFoundPage'))

// Global QueryClient với retry & cache config
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 phút
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Loading fallback component
function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-50">
      <div className="flex flex-col items-center gap-3">
        <div className="spinner w-8 h-8 text-primary-600" />
        <p className="text-sm text-slate-500">Đang tải...</p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* === Public Routes === */}
            <Route path="/login"           element={<LoginPage />} />
            <Route path="/register"        element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/rooms/search"    element={<RoomSearchPage />} />

            {/* === Protected: Mọi user đã đăng nhập === */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            <Route path="/invoices" element={
              <ProtectedRoute>
                <InvoicesPage />
              </ProtectedRoute>
            } />
            <Route path="/tickets" element={
              <ProtectedRoute>
                <TicketsPage />
              </ProtectedRoute>
            } />
            <Route path="/violations" element={
              <ProtectedRoute>
                <ViolationsPage />
              </ProtectedRoute>
            } />

            {/* === Protected: Landlord/Admin only === */}
            <Route path="/rooms" element={
              <ProtectedRoute allowedRoles={['landlord', 'admin']}>
                <RoomsPage />
              </ProtectedRoute>
            } />
            <Route path="/rooms/:roomId" element={
              <ProtectedRoute allowedRoles={['landlord', 'admin']}>
                <RoomDetailPage />
              </ProtectedRoute>
            } />
            <Route path="/reports" element={
              <ProtectedRoute allowedRoles={['landlord', 'admin']}>
                <ReportsPage />
              </ProtectedRoute>
            } />

            {/* === Error Pages === */}
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/404"          element={<NotFoundPage />} />

            {/* === Redirect === */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </Suspense>

        {/* Toast notifications - toàn cục */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              fontSize: '14px',
              fontFamily: 'Inter, sans-serif',
              borderRadius: '12px',
              padding: '12px 16px',
            },
            success: { iconTheme: { primary: '#22c55e', secondary: '#fff' } },
            error:   { iconTheme: { primary: '#ef4444', secondary: '#fff' } },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
