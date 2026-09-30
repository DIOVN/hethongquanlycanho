import { useState, useEffect } from 'react'
import {
  FileText,
  QrCode,
  Upload,
  CheckCircle2,
  Clock,
  AlertCircle,
  Plus,
  RefreshCw,
  Eye,
  Filter,
  Check,
} from 'lucide-react'
import toast from 'react-hot-toast'
import AppLayout from '@/components/layout/AppLayout'
import useAuthStore from '@/stores/authStore'
import billingService from '@/services/billingService'
import VietQRModal from '@/components/invoices/VietQRModal'
import PaymentSlipModal from '@/components/invoices/PaymentSlipModal'
import QuickInvoiceModal from '@/components/invoices/QuickInvoiceModal'

export default function InvoicesPage() {
  const { user } = useAuthStore()
  const isLandlord = user?.role === 'landlord' || user?.role === 'admin'

  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterStatus, setFilterStatus] = useState('all')

  // Modals state
  const [selectedInvoice, setSelectedInvoice] = useState(null)
  const [qrModalOpen, setQrModalOpen] = useState(false)
  const [slipModalOpen, setSlipModalOpen] = useState(false)
  const [quickInvoiceModalOpen, setQuickInvoiceModalOpen] = useState(false)
  const [expandedInvoiceId, setExpandedInvoiceId] = useState(null)

  const fetchInvoices = async () => {
    setLoading(true)
    try {
      let data
      if (isLandlord) {
        data = await billingService.getInvoices(
          filterStatus !== 'all' ? { status: filterStatus } : {}
        )
      } else {
        data = await billingService.getMyInvoices()
      }
      setInvoices(data || [])
    } catch {
      toast.error('Không thể tải danh sách hóa đơn.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchInvoices()
  }, [filterStatus, isLandlord])

  const handleConfirmPayment = async (invoiceId) => {
    try {
      await billingService.confirmPayment(invoiceId)
      toast.success('Đã xác nhận thanh toán thành công!')
      fetchInvoices()
    } catch {
      toast.error('Xác nhận thanh toán thất bại.')
    }
  }

  const filteredInvoices = invoices.filter((inv) => {
    if (filterStatus === 'all') return true
    return inv.status === filterStatus
  })

  const getStatusBadge = (status) => {
    switch (status) {
      case 'paid':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Đã thanh toán
          </span>
        )
      case 'pending_verification':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200">
            <Clock className="w-3.5 h-3.5" />
            Chờ đối soát biên lai
          </span>
        )
      case 'overdue':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <AlertCircle className="w-3.5 h-3.5" />
            Quá hạn
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertCircle className="w-3.5 h-3.5" />
            Chưa thanh toán
          </span>
        )
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600">
                <FileText className="w-5 h-5" />
              </div>
              Quản lý Hóa đơn & Thanh toán VietQR
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              {isLandlord
                ? 'Theo dõi công nợ, đối soát biên lai ngân hàng và lập hóa đơn tại chỗ'
                : 'Tra cứu tiền phòng, quét mã VietQR 1-chạm hoặc tải ảnh biên lai ngân hàng'}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchInvoices}
              className="btn btn-secondary text-xs px-3 py-2 flex items-center gap-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Làm mới
            </button>

            {isLandlord && (
              <button
                onClick={() => setQuickInvoiceModalOpen(true)}
                className="btn btn-primary text-xs px-4 py-2 flex items-center gap-1.5 shadow-sm"
              >
                <Plus className="w-4 h-4" />
                Lập hóa đơn nhanh (AI OCR)
              </button>
            )}
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1.5 bg-slate-100 rounded-2xl w-fit">
          {[
            { id: 'all', label: 'Tất cả' },
            { id: 'unpaid', label: 'Chưa thanh toán' },
            { id: 'pending_verification', label: 'Chờ đối soát' },
            { id: 'paid', label: 'Đã thanh toán' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterStatus(tab.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-xl transition-all ${
                filterStatus === tab.id
                  ? 'bg-white text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Invoices List */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-28 bg-white rounded-2xl border border-slate-200 animate-pulse" />
            ))}
          </div>
        ) : filteredInvoices.length === 0 ? (
          <div className="card text-center py-16">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-800">Không có hóa đơn nào</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              {filterStatus !== 'all'
                ? `Không có hóa đơn nào ở trạng thái '${filterStatus}'.`
                : 'Chưa có hóa đơn nào được phát hành trong kỳ này.'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredInvoices.map((inv) => {
              const isExpanded = expandedInvoiceId === inv.id
              const amountFormatted = new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND',
              }).format(inv.total_amount || 0)

              return (
                <div
                  key={inv.id}
                  className="card hover:shadow-card-hover transition-all duration-200 border-slate-200 overflow-hidden"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    {/* Invoice Info */}
                    <div className="flex items-start gap-3.5">
                      <div className="w-11 h-11 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shrink-0 mt-0.5">
                        <FileText className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-bold text-slate-900">
                            Hóa đơn Tháng {inv.month}/{inv.year}
                          </h3>
                          <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                            Phòng {inv.room_number || inv.room_id}
                          </span>
                          {getStatusBadge(inv.status)}
                        </div>

                        <div className="flex items-center gap-4 text-xs text-slate-500 mt-1">
                          <span>Mã: #{inv.id}</span>
                          {inv.due_date && <span>Hạn: {inv.due_date}</span>}
                          {inv.payment_ref && (
                            <span className="font-mono text-indigo-600">
                              Nội dung: {inv.payment_ref}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Total Amount & Action Buttons */}
                    <div className="flex items-center justify-between md:justify-end gap-3 pt-3 md:pt-0 border-t md:border-t-0 border-slate-100">
                      <div className="text-left md:text-right">
                        <span className="block text-[11px] text-slate-400 font-medium">Tổng tiền</span>
                        <span className="text-base font-bold text-indigo-700">{amountFormatted}</span>
                      </div>

                      <div className="flex items-center gap-1.5">
                        {/* VietQR button */}
                        <button
                          onClick={() => {
                            setSelectedInvoice(inv)
                            setQrModalOpen(true)
                          }}
                          className="btn btn-secondary text-xs px-3 py-2 flex items-center gap-1 text-indigo-700 hover:bg-indigo-50 border-indigo-200"
                        >
                          <QrCode className="w-4 h-4 text-indigo-600" />
                          <span>Mã VietQR</span>
                        </button>

                        {/* Tenant Upload Slip button */}
                        {!isLandlord && inv.status !== 'paid' && (
                          <button
                            onClick={() => {
                              setSelectedInvoice(inv)
                              setSlipModalOpen(true)
                            }}
                            className="btn btn-primary text-xs px-3 py-2 flex items-center gap-1"
                          >
                            <Upload className="w-3.5 h-3.5" />
                            <span>Gửi biên lai</span>
                          </button>
                        )}

                        {/* Landlord Confirm Payment button */}
                        {isLandlord && inv.status !== 'paid' && (
                          <button
                            onClick={() => handleConfirmPayment(inv.id)}
                            className="btn btn-primary text-xs px-3 py-2 flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700"
                          >
                            <Check className="w-3.5 h-3.5" />
                            <span>Duyệt đã thu</span>
                          </button>
                        )}

                        {/* Expand Details */}
                        <button
                          onClick={() => setExpandedInvoiceId(isExpanded ? null : inv.id)}
                          className="p-2 text-slate-400 hover:text-slate-700 rounded-xl hover:bg-slate-100"
                          title="Chi tiết khoản mục"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Expanded Line Items Detail */}
                  {isExpanded && inv.items && inv.items.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-slate-100 bg-slate-50/70 -mx-5 -mb-5 p-4">
                      <h4 className="text-xs font-bold text-slate-700 mb-2">Chi tiết các khoản thu:</h4>
                      <div className="space-y-1.5">
                        {inv.items.map((item, idx) => (
                          <div key={idx} className="flex items-center justify-between text-xs py-1 border-b border-slate-200/50">
                            <span className="text-slate-600">{item.description}</span>
                            <span className="font-semibold text-slate-800">
                              {new Intl.NumberFormat('vi-VN', {
                                style: 'currency',
                                currency: 'VND',
                              }).format(item.subtotal || 0)}
                            </span>
                          </div>
                        ))}
                      </div>

                      {inv.payment_slip_url && (
                        <div className="mt-3 flex items-center gap-2">
                          <span className="text-xs font-semibold text-slate-600">Ảnh biên lai đã gửi:</span>
                          <a
                            href={inv.payment_slip_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-indigo-600 hover:underline flex items-center gap-1"
                          >
                            Xem ảnh biên lai
                          </a>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Modals */}
      <VietQRModal
        invoice={selectedInvoice}
        isOpen={qrModalOpen}
        onClose={() => setQrModalOpen(false)}
        onOpenPaymentSlip={(inv) => {
          setSelectedInvoice(inv)
          setSlipModalOpen(true)
        }}
      />

      <PaymentSlipModal
        invoice={selectedInvoice}
        isOpen={slipModalOpen}
        onClose={() => setSlipModalOpen(false)}
        onSuccess={fetchInvoices}
      />

      <QuickInvoiceModal
        isOpen={quickInvoiceModalOpen}
        onClose={() => setQuickInvoiceModalOpen(false)}
        onSuccess={fetchInvoices}
      />
    </AppLayout>
  )
}
