import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Building2,
  FileText,
  AlertTriangle,
  Wrench,
  QrCode,
  PlusCircle,
  TrendingUp,
  Clock,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  CreditCard,
} from 'lucide-react'
import AppLayout from '@/components/layout/AppLayout'
import useAuthStore from '@/stores/authStore'
import billingService from '@/services/billingService'
import ticketService from '@/services/ticketService'
import violationService from '@/services/violationService'
import roomService from '@/services/roomService'
import QuickInvoiceModal from '@/components/invoices/QuickInvoiceModal'
import VietQRModal from '@/components/invoices/VietQRModal'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const isLandlord = user?.role === 'landlord' || user?.role === 'admin'

  const [quickInvoiceOpen, setQuickInvoiceOpen] = useState(false)
  const [selectedInvoiceForQR, setSelectedInvoiceForQR] = useState(null)

  // Fetch Rooms (Landlord)
  const { data: rooms = [] } = useQuery({
    queryKey: ['rooms'],
    queryFn: () => roomService.getRooms(),
    enabled: isLandlord,
  })

  // Fetch Invoices
  const { data: invoices = [], isLoading: loadingInvoices, refetch: refetchInvoices } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => (isLandlord ? billingService.getInvoices() : billingService.getMyInvoices()),
  })

  // Fetch Tickets
  const { data: tickets = [], isLoading: loadingTickets } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => ticketService.getTickets(),
  })

  // Fetch Violations
  const { data: violations = [], isLoading: loadingViolations } = useQuery({
    queryKey: ['violations'],
    queryFn: () => violationService.getViolations(),
  })

  // Math KPI
  const unpaidInvoices = invoices.filter((inv) => inv.payment_status === 'unpaid' || inv.payment_status === 'pending')
  const totalPendingAmount = unpaidInvoices.reduce((sum, inv) => sum + (Number(inv.total_amount) || 0), 0)
  const openTickets = tickets.filter((t) => t.status === 'pending' || t.status === 'in_progress')
  const pendingViolations = violations.filter((v) => v.status === 'pending' || v.status === 'warned')

  const totalRoomsCount = rooms.length
  const rentedRoomsCount = rooms.filter((r) => r.status === 'rented' || r.current_tenant_id).length
  const occupancyRate = totalRoomsCount > 0 ? Math.round((rentedRoomsCount / totalRoomsCount) * 100) : 0

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Welcome Hero Card */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-6 sm:p-8 text-white shadow-xl">
          <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold border border-indigo-400/30">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Hệ thống Quản lý Căn hộ Thông minh SAMS</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                Xin chào, {user?.full_name || user?.username || 'Cư dân'}!
              </h1>
              <p className="text-sm text-slate-300 max-w-xl">
                {isLandlord
                  ? 'Theo dõi chỉ số điện nước, dòng tiền hóa đơn tự động và xử lý vi phạm nhanh chóng với sự hỗ trợ của AI Vision OCR.'
                  : 'Kiểm tra tiền thuê phòng, tạo mã VietQR Napas247 tức thì và gửi yêu cầu sửa chữa thiết bị căn hộ nhanh chóng.'}
              </p>
            </div>

            {/* Quick action hero button */}
            <div className="flex flex-wrap items-center gap-3">
              {isLandlord ? (
                <button
                  onClick={() => setQuickInvoiceOpen(true)}
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-2xl bg-indigo-500 hover:bg-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-500/30 transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[48px]"
                >
                  <PlusCircle className="w-5 h-5" />
                  Lập Hóa Đơn Nhanh / OCR
                </button>
              ) : (
                <Link
                  to="/invoices"
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm shadow-lg shadow-emerald-500/30 transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[48px]"
                >
                  <QrCode className="w-5 h-5" />
                  Xem Hóa Đơn & Quét VietQR
                </Link>
              )}
            </div>
          </div>
          <div className="absolute -right-12 -bottom-12 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        </div>

        {/* 4 Primary Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Stat 1: Rooms / Occupancy */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs hover:border-indigo-200 transition-colors">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">
                {isLandlord ? 'Tỷ lệ lấp đầy phòng' : 'Trạng thái phòng'}
              </span>
              <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
                <Building2 className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">
                {isLandlord ? `${occupancyRate}%` : 'Đang thuê'}
              </span>
              {isLandlord && (
                <span className="text-xs font-medium text-slate-500">
                  ({rentedRoomsCount}/{totalRoomsCount} phòng)
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
              Tình trạng quản lý ổn định
            </p>
          </div>

          {/* Stat 2: Unpaid Invoices */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs hover:border-amber-200 transition-colors">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">
                {isLandlord ? 'Hóa đơn chưa thanh toán' : 'Hóa đơn cần đóng'}
              </span>
              <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                <FileText className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{unpaidInvoices.length}</span>
              <span className="text-xs font-medium text-slate-500">hóa đơn</span>
            </div>
            <p className="text-[11px] text-amber-600 mt-2 font-medium">
              Tổng tiền: {Number(totalPendingAmount).toLocaleString('vi-VN')} đ
            </p>
          </div>

          {/* Stat 3: Open Tickets */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs hover:border-blue-200 transition-colors">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Sự cố đang xử lý</span>
              <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                <Wrench className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{openTickets.length}</span>
              <span className="text-xs font-medium text-slate-500">yêu cầu kỹ thuật</span>
            </div>
            <Link
              to="/tickets"
              className="text-[11px] text-indigo-600 hover:text-indigo-700 font-semibold mt-2 inline-flex items-center gap-1"
            >
              Xem chi tiết tiến độ &rarr;
            </Link>
          </div>

          {/* Stat 4: Pending Violations */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs hover:border-rose-200 transition-colors">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Nhắc nhở / Vi phạm</span>
              <div className="w-9 h-9 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{pendingViolations.length}</span>
              <span className="text-xs font-medium text-slate-500">vụ việc</span>
            </div>
            <Link
              to="/violations"
              className="text-[11px] text-rose-600 hover:text-rose-700 font-semibold mt-2 inline-flex items-center gap-1"
            >
              Kiểm tra quy định tòa nhà &rarr;
            </Link>
          </div>
        </div>

        {/* 2-Column Section: Recent Invoices & Open Tickets */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Card: Recent Invoices */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-indigo-600" />
                  <h3 className="text-base font-bold text-slate-900">Hóa đơn gần nhất</h3>
                </div>
                <Link
                  to="/invoices"
                  className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                >
                  Xem tất cả ({invoices.length})
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {loadingInvoices ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-16 bg-slate-50 rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : invoices.length === 0 ? (
                <div className="text-center py-8 text-slate-400 text-xs">
                  Chưa có hóa đơn nào được phát hành.
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {invoices.slice(0, 4).map((inv) => (
                    <div key={inv.id} className="py-3 flex items-center justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-xs text-slate-900">
                            Phòng {inv.room_number || inv.room_id}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            (Tháng {inv.billing_month || 'hiện tại'})
                          </span>
                        </div>
                        <p className="text-sm font-black text-indigo-700 mt-0.5">
                          {Number(inv.total_amount).toLocaleString('vi-VN')} đ
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        {inv.payment_status === 'paid' ? (
                          <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-50 text-emerald-700">
                            Đã thanh toán
                          </span>
                        ) : inv.payment_status === 'pending' ? (
                          <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-50 text-blue-700">
                            Chờ duyệt bill
                          </span>
                        ) : (
                          <button
                            onClick={() => setSelectedInvoiceForQR(inv)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 min-h-[36px]"
                          >
                            <QrCode className="w-3.5 h-3.5" />
                            VietQR
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                Hỗ trợ Napas247 & VietQR Chuẩn EMVCo
              </span>
            </div>
          </div>

          {/* Card: Active Tickets & Rules Alerts */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Wrench className="w-5 h-5 text-indigo-600" />
                  <h3 className="text-base font-bold text-slate-900">Yêu cầu bảo trì kỹ thuật</h3>
                </div>
                <Link
                  to="/tickets"
                  className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                >
                  Xem tất cả ({tickets.length})
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {loadingTickets ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-16 bg-slate-50 rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : tickets.length === 0 ? (
                <div className="text-center py-8 text-slate-400 text-xs">
                  Không có sự cố nào cần xử lý.
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {tickets.slice(0, 4).map((t) => (
                    <div key={t.id} className="py-3 flex items-center justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-xs text-slate-800">
                            Phòng {t.room_number || t.room_id}
                          </span>
                          <span className="text-xs font-medium text-slate-600 truncate max-w-[200px]">
                            {t.title}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-400 mt-0.5 block">
                          {t.created_at ? new Date(t.created_at).toLocaleDateString('vi-VN') : ''}
                        </span>
                      </div>

                      <div>
                        {t.status === 'resolved' ? (
                          <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-50 text-emerald-700">
                            Đã xử lý
                          </span>
                        ) : t.status === 'in_progress' ? (
                          <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-50 text-indigo-700">
                            Đang sửa
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-50 text-amber-700">
                            Chờ thợ
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <Link
                to="/violations"
                className="text-xs font-semibold text-rose-600 hover:text-rose-700 flex items-center gap-1.5"
              >
                <AlertTriangle className="w-4 h-4" />
                Kiểm tra {pendingViolations.length} vụ việc vi phạm nội quy &rarr;
              </Link>
            </div>
          </div>
        </div>

        {/* Quick Invoice Modal (OCR Vision & Penalties) */}
        {quickInvoiceOpen && (
          <QuickInvoiceModal
            onClose={() => setQuickInvoiceOpen(false)}
            onSuccess={() => {
              refetchInvoices()
              setQuickInvoiceOpen(false)
            }}
          />
        )}

        {/* VietQR Dynamic Modal */}
        {selectedInvoiceForQR && (
          <VietQRModal
            invoice={selectedInvoiceForQR}
            onClose={() => setSelectedInvoiceForQR(null)}
          />
        )}
      </div>
    </AppLayout>
  )
}
