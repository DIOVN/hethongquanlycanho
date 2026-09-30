import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Wrench,
  Plus,
  Filter,
  CheckCircle2,
  Clock,
  AlertCircle,
  XCircle,
  FileImage,
  DollarSign,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react'
import toast from 'react-hot-toast'
import AppLayout from '@/components/layout/AppLayout'
import useAuthStore from '@/stores/authStore'
import ticketService from '@/services/ticketService'
import roomService from '@/services/roomService'

export default function TicketsPage() {
  const { user } = useAuthStore()
  const isLandlord = user?.role === 'landlord' || user?.role === 'admin'
  const queryClient = useQueryClient()

  const [statusFilter, setStatusFilter] = useState('ALL')
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [statusModalTicket, setStatusModalTicket] = useState(null)
  const [newStatus, setNewStatus] = useState('in_progress')
  const [repairCost, setRepairCost] = useState('')

  // Form states for creating ticket
  const [title, setTitle] = useState('')
  const [roomId, setRoomId] = useState('')
  const [category, setCategory] = useState('repair')
  const [priority, setPriority] = useState('medium')
  const [description, setDescription] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  // Fetch tickets
  const { data: tickets = [], isLoading, refetch } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => ticketService.getTickets(),
  })

  // Fetch rooms for dropdown if landlord
  const { data: rooms = [] } = useQuery({
    queryKey: ['rooms'],
    queryFn: () => roomService.getRooms(),
    enabled: isLandlord,
  })

  // Mutation: Update status
  const updateStatusMutation = useMutation({
    mutationFn: ({ ticketId, payload }) => ticketService.updateTicketStatus(ticketId, payload),
    onSuccess: () => {
      toast.success('Đã cập nhật tiến độ xử lý yêu cầu!')
      queryClient.invalidateQueries(['tickets'])
      setStatusModalTicket(null)
    },
    onError: (err) => {
      toast.error(err?.response?.data?.message || 'Không thể cập nhật trạng thái')
    },
  })

  const filteredTickets = tickets.filter((t) => {
    if (statusFilter === 'ALL') return true
    return t.status === statusFilter
  })

  const handleCreateSubmit = async (e) => {
    e.preventDefault()
    if (!title.trim()) {
      toast.error('Vui lòng nhập tiêu đề sự cố')
      return
    }

    setSubmitting(true)
    try {
      const formData = new FormData()
      formData.append('title', title.trim())
      formData.append('category', category)
      formData.append('priority', priority)
      if (roomId) formData.append('room_id', roomId)
      if (description) formData.append('description', description.trim())
      if (selectedFile) formData.append('image', selectedFile)

      await ticketService.createTicket(formData)
      toast.success('Đã gửi yêu cầu sửa chữa thành công!')
      setCreateModalOpen(false)
      setTitle('')
      setDescription('')
      setSelectedFile(null)
      queryClient.invalidateQueries(['tickets'])
    } catch (err) {
      toast.error(err?.response?.data?.message || 'Lỗi khi gửi yêu cầu')
    } finally {
      setSubmitting(false)
    }
  }

  const handleStatusSubmit = (e) => {
    e.preventDefault()
    if (!statusModalTicket) return
    updateStatusMutation.mutate({
      ticketId: statusModalTicket.id,
      payload: {
        status: newStatus,
        repair_cost: repairCost ? parseFloat(repairCost) : 0,
      },
    })
  }

  const priorityBadge = (p) => {
    switch (p) {
      case 'urgent':
        return <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-rose-100 text-rose-700">Khẩn cấp</span>
      case 'high':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-100 text-amber-800">Ưu tiên cao</span>
      case 'low':
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-slate-100 text-slate-600">Thấp</span>
      default:
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-700">Trung bình</span>
    }
  }

  const statusBadge = (s) => {
    switch (s) {
      case 'pending':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-50 text-amber-700 border border-amber-200">
            <Clock className="w-3.5 h-3.5 text-amber-500" />
            Chờ xử lý
          </span>
        )
      case 'in_progress':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Wrench className="w-3.5 h-3.5 text-indigo-500" />
            Đang xử lý
          </span>
        )
      case 'resolved':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
            Đã giải quyết
          </span>
        )
      case 'cancelled':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-100 text-slate-500 border border-slate-200">
            <XCircle className="w-3.5 h-3.5 text-slate-400" />
            Đã hủy
          </span>
        )
      default:
        return null
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header banner */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <Wrench className="w-7 h-7 text-indigo-600" />
              Báo hỏng & Sửa chữa Kỹ thuật
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Gửi yêu cầu bảo trì, theo dõi tiến độ sửa chữa thiết bị căn hộ và chi phí khắc phục.
            </p>
          </div>
          <button
            onClick={() => setCreateModalOpen(true)}
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 shadow-sm transition-colors min-h-[44px]"
          >
            <Plus className="w-4 h-4" />
            Tạo yêu cầu sửa chữa
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {[
            { key: 'ALL', label: 'Tất cả' },
            { key: 'pending', label: 'Chờ xử lý' },
            { key: 'in_progress', label: 'Đang xử lý' },
            { key: 'resolved', label: 'Đã giải quyết' },
            { key: 'cancelled', label: 'Đã hủy' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setStatusFilter(tab.key)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all min-h-[40px] ${
                statusFilter === tab.key
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tickets Grid / List */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-44 bg-white rounded-2xl border border-slate-200 animate-pulse p-6" />
            ))}
          </div>
        ) : filteredTickets.length === 0 ? (
          <div className="bg-white rounded-2xl border border-dashed border-slate-300 p-12 text-center">
            <div className="w-12 h-12 rounded-full bg-slate-50 flex items-center justify-center mx-auto text-slate-400 mb-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-500" />
            </div>
            <h3 className="text-base font-semibold text-slate-800">Không có yêu cầu sửa chữa nào</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Tất cả thiết bị và dịch vụ căn hộ hiện đang hoạt động bình thường hoặc đã được khắc phục.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTickets.map((t) => (
              <div
                key={t.id}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800">
                        Phòng {t.room_number || t.room_id}
                      </span>
                      {priorityBadge(t.priority)}
                    </div>
                    {statusBadge(t.status)}
                  </div>

                  <h3 className="text-base font-bold text-slate-900 line-clamp-1">{t.title}</h3>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                    {t.description || 'Không có mô tả chi tiết'}
                  </p>

                  {t.image_url && (
                    <div className="mt-3">
                      <a
                        href={t.image_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                      >
                        <FileImage className="w-4 h-4" />
                        Xem ảnh hiện trường
                      </a>
                    </div>
                  )}

                  {t.repair_cost > 0 && (
                    <div className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-slate-700 bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-100">
                      <DollarSign className="w-4 h-4 text-emerald-600" />
                      Chi phí sửa chữa: {Number(t.repair_cost).toLocaleString('vi-VN')} đ
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">
                    {t.created_at ? new Date(t.created_at).toLocaleDateString('vi-VN') : 'Mới tạo'}
                  </span>

                  {isLandlord && (
                    <button
                      onClick={() => {
                        setStatusModalTicket(t)
                        setNewStatus(t.status)
                        setRepairCost(t.repair_cost || '')
                      }}
                      className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 px-3 py-1.5 rounded-lg hover:bg-indigo-50 transition-colors"
                    >
                      Cập nhật tiến độ &rarr;
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal Tạo Yêu Cầu */}
        {createModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
            <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-100">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <Wrench className="w-5 h-5 text-indigo-600" />
                  Gửi yêu cầu sửa chữa căn hộ
                </h3>
                <button
                  onClick={() => setCreateModalOpen(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateSubmit} className="mt-4 space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Tiêu đề sự cố <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="VD: Hỏng vòi nước bồn rửa, điều hòa không mát..."
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Loại sự cố</label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="repair">Sửa chữa chung</option>
                      <option value="electrical">Điện / Ánh sáng</option>
                      <option value="plumbing">Cấp thoát nước</option>
                      <option value="appliance">Thiết bị gia dụng</option>
                      <option value="internet">Mạng / WiFi</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Mức độ ưu tiên</label>
                    <select
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="low">Thấp</option>
                      <option value="medium">Bình thường</option>
                      <option value="high">Ưu tiên cao</option>
                      <option value="urgent">Khẩn cấp (Rò rỉ nước/Chập điện)</option>
                    </select>
                  </div>
                </div>

                {isLandlord && (
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Chọn căn hộ / Phòng</label>
                    <select
                      value={roomId}
                      onChange={(e) => setRoomId(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="">-- Tự động theo hợp đồng của cư dân --</option>
                      {rooms.map((r) => (
                        <option key={r.id} value={r.id}>
                          Phòng {r.room_number} ({r.room_type})
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Mô tả chi tiết</label>
                  <textarea
                    rows={3}
                    placeholder="Mô tả cụ thể hiện tượng hư hỏng để kỹ thuật viên chuẩn bị phụ tùng..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Ảnh chụp hiện trường</label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setSelectedFile(e.target.files[0] || null)}
                    className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                  />
                </div>

                <div className="pt-2 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setCreateModalOpen(false)}
                    className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl min-h-[44px]"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs disabled:opacity-50 min-h-[44px]"
                  >
                    {submitting ? 'Đang gửi...' : 'Gửi yêu cầu'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal Cập Nhật Trạng Thái (Chủ nhà) */}
        {statusModalTicket && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-100">
              <h3 className="text-lg font-bold text-slate-900 mb-2">
                Cập nhật xử lý: Phòng {statusModalTicket.room_number || statusModalTicket.room_id}
              </h3>
              <p className="text-xs text-slate-500 mb-4">{statusModalTicket.title}</p>

              <form onSubmit={handleStatusSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Trạng thái mới</label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="pending">Chờ xử lý</option>
                    <option value="in_progress">Đang tiến hành sửa chữa</option>
                    <option value="resolved">Đã khắc phục xong</option>
                    <option value="cancelled">Hủy bỏ</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Chi phí sửa chữa (VNĐ - nếu có)
                  </label>
                  <input
                    type="number"
                    min="0"
                    placeholder="VD: 150000"
                    value={repairCost}
                    onChange={(e) => setRepairCost(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <p className="text-[11px] text-slate-400 mt-1">
                    Chi phí này có thể được hạch toán vào OpEx hoặc hóa đơn căn hộ.
                  </p>
                </div>

                <div className="pt-2 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setStatusModalTicket(null)}
                    className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl min-h-[44px]"
                  >
                    Đóng
                  </button>
                  <button
                    type="submit"
                    disabled={updateStatusMutation.isPending}
                    className="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs disabled:opacity-50 min-h-[44px]"
                  >
                    {updateStatusMutation.isPending ? 'Đang lưu...' : 'Lưu cập nhật'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
