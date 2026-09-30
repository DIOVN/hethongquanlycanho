import React, { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Home,
  Building2,
  Users,
  CheckCircle2,
  Wrench,
  Sparkles,
  ArrowLeft,
  Phone,
  Mail,
  CreditCard,
  Plus,
  Wind,
  Shirt,
  CookingPot,
  Car,
  FileText,
  AlertTriangle,
  Receipt,
  UserCheck,
} from 'lucide-react'
import toast from 'react-hot-toast'
import AppLayout from '@/components/layout/AppLayout'
import roomService from '@/services/roomService'

export default function RoomDetailPage() {
  const { roomId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [isAddingRoommate, setIsAddingRoommate] = useState(false)
  const [newRoommate, setNewRoommate] = useState({
    full_name: '',
    phone: '',
    cccd_number: '',
    vehicle_plate: '',
  })

  // 1. Fetch Room Details
  const { data: room, isLoading, isError } = useQuery({
    queryKey: ['room', roomId],
    queryFn: () => roomService.getRoomDetail(roomId),
    enabled: !!roomId,
  })

  // 2. Fetch Roommates
  const { data: roommates = [], refetch: refetchRoommates } = useQuery({
    queryKey: ['roommates', roomId],
    queryFn: () => roomService.getRoommates(roomId),
    enabled: !!roomId,
  })

  // Mutation cập nhật trạng thái
  const updateStatusMutation = useMutation({
    mutationFn: (status) => roomService.updateRoomStatus(roomId, status),
    onSuccess: (res) => {
      toast.success(res?.message || 'Cập nhật trạng thái thành công!')
      queryClient.invalidateQueries(['room', roomId])
      queryClient.invalidateQueries(['rooms'])
    },
    onError: (err) => {
      toast.error(err.response?.data?.error?.message || 'Lỗi cập nhật trạng thái.')
    },
  })

  // Mutation thêm người ở cùng
  const addRoommateMutation = useMutation({
    mutationFn: (data) => roomService.addRoommate(roomId, data),
    onSuccess: () => {
      toast.success('Đã thêm người ở cùng thành công!')
      refetchRoommates()
      setIsAddingRoommate(false)
      setNewRoommate({ full_name: '', phone: '', cccd_number: '', vehicle_plate: '' })
    },
    onError: (err) => {
      toast.error(err.response?.data?.error?.message || 'Thêm người ở cùng thất bại.')
    },
  })

  const formatMoney = (val) => {
    if (!val) return '0 đ'
    return new Intl.NumberFormat('vi-VN').format(val) + ' đ'
  }

  if (isLoading) {
    return (
      <AppLayout>
        <div className="py-20 flex flex-col items-center justify-center text-slate-400">
          <div className="spinner w-8 h-8 text-indigo-600 mb-3" />
          <p className="text-sm font-medium">Đang tải chi tiết phòng #{roomId}...</p>
        </div>
      </AppLayout>
    )
  }

  if (isError || !room) {
    return (
      <AppLayout>
        <div className="p-8 max-w-xl mx-auto text-center bg-white rounded-3xl border border-slate-100 shadow-sm mt-10">
          <Home className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h2 className="text-xl font-bold text-slate-800">Không tìm thấy phòng #{roomId}</h2>
          <p className="text-xs text-slate-500 mt-1">Phòng này không tồn tại hoặc đã bị xóa khỏi hệ thống.</p>
          <button onClick={() => navigate('/rooms')} className="btn-primary mt-5 text-xs py-2 px-4">
            Quay lại danh sách phòng
          </button>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto space-y-6">
        {/* Navigation Back */}
        <div className="flex items-center justify-between">
          <Link
            to="/rooms"
            className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-indigo-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Quay lại danh sách phòng
          </Link>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">Trạng thái:</span>
            <select
              value={room.status}
              onChange={(e) => updateStatusMutation.mutate(e.target.value)}
              className="text-xs font-bold py-1.5 px-3 border border-slate-200 rounded-xl bg-white text-slate-800"
            >
              <option value="vacant">Phòng trống</option>
              <option value="occupied">Đang cho thuê</option>
              <option value="maintenance">Đang bảo trì</option>
            </select>
          </div>
        </div>

        {/* Hero Card */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-100 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-3xl bg-indigo-600 text-white font-mono font-black text-2xl flex items-center justify-center shadow-lg shadow-indigo-600/30">
              {room.room_number}
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                  Phòng {room.room_number}
                </h1>
                <span className="badge badge-indigo text-xs">Tầng {room.floor || 1}</span>
              </div>
              <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-1 font-medium">
                <Building2 className="w-4 h-4 text-slate-400" />
                {room.building_name} • {room.address}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 bg-indigo-50/50 p-4 rounded-2xl border border-indigo-100/60">
            <div>
              <span className="text-xs text-slate-400 font-medium">Giá thuê niêm yết:</span>
              <div className="text-2xl font-black text-indigo-600">
                {formatMoney(room.base_price)}
                <span className="text-xs text-slate-400 font-normal"> /tháng</span>
              </div>
            </div>
          </div>
        </div>

        {/* 2-Column Info Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* CỘT TRÁI: THÔNG TIN CHI TIẾT & TIỆN ÍCH (2 Cột) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm space-y-5">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Home className="w-4 h-4 text-indigo-600" /> Thông số kỹ thuật & Diện tích
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
                  <span className="text-xs text-slate-400">Diện tích phòng</span>
                  <p className="text-lg font-black text-slate-800 mt-1">{room.area_sqm || 25} m²</p>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
                  <span className="text-xs text-slate-400">Tầng lầu</span>
                  <p className="text-lg font-black text-slate-800 mt-1">Tầng {room.floor || 1}</p>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
                  <span className="text-xs text-slate-400">Tình trạng phòng</span>
                  <p className="text-sm font-bold text-indigo-600 mt-1 capitalize">{room.status}</p>
                </div>
              </div>

              {/* Tiện nghi phòng */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5">
                  Tiện ích trang bị sẵn:
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className={`p-3.5 rounded-2xl border flex items-center gap-2.5 ${room.has_balcony ? 'bg-indigo-50/50 border-indigo-200 text-indigo-950 font-bold' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
                    <Wind className="w-4 h-4 text-indigo-600" /> Ban công
                  </div>
                  <div className={`p-3.5 rounded-2xl border flex items-center gap-2.5 ${room.has_washing_machine ? 'bg-indigo-50/50 border-indigo-200 text-indigo-950 font-bold' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
                    <Shirt className="w-4 h-4 text-indigo-600" /> Máy giặt
                  </div>
                  <div className={`p-3.5 rounded-2xl border flex items-center gap-2.5 ${room.has_kitchen ? 'bg-indigo-50/50 border-indigo-200 text-indigo-950 font-bold' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
                    <CookingPot className="w-4 h-4 text-indigo-600" /> Bếp riêng
                  </div>
                  <div className={`p-3.5 rounded-2xl border flex items-center gap-2.5 ${room.has_parking ? 'bg-indigo-50/50 border-indigo-200 text-indigo-950 font-bold' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
                    <Car className="w-4 h-4 text-indigo-600" /> Chỗ để xe
                  </div>
                </div>
              </div>

              {room.description && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">Ghi chú & Mô tả:</h4>
                  <p className="text-xs text-slate-600 bg-slate-50 p-4 rounded-2xl border border-slate-100 leading-relaxed">
                    {room.description}
                  </p>
                </div>
              )}
            </div>

            {/* DANH SÁCH NGƯỜI Ở CÙNG (ROOMMATES) */}
            <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <Users className="w-4 h-4 text-indigo-600" /> Nhân khẩu & Người ở cùng ({roommates.length})
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">Danh sách các cá nhân cư trú hợp pháp trong phòng</p>
                </div>
                <button
                  onClick={() => setIsAddingRoommate(!isAddingRoommate)}
                  className="btn-primary py-1.5 px-3 text-xs font-bold rounded-xl flex items-center gap-1.5"
                >
                  <Plus className="w-3.5 h-3.5" /> Thêm người ở cùng
                </button>
              </div>

              {/* Form Thêm nhanh nhân khẩu */}
              {isAddingRoommate && (
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    if (!newRoommate.full_name) {
                      toast.error('Vui lòng nhập họ tên người ở cùng!')
                      return
                    }
                    addRoommateMutation.mutate(newRoommate)
                  }}
                  className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3 animate-in fade-in duration-200"
                >
                  <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
                    Đăng ký nhân khẩu mới
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Họ và tên *</label>
                      <input
                        type="text"
                        required
                        placeholder="Nguyễn Văn A..."
                        value={newRoommate.full_name}
                        onChange={(e) => setNewRoommate({ ...newRoommate, full_name: e.target.value })}
                        className="input py-1.5 text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Số điện thoại</label>
                      <input
                        type="text"
                        placeholder="0912345678"
                        value={newRoommate.phone}
                        onChange={(e) => setNewRoommate({ ...newRoommate, phone: e.target.value })}
                        className="input py-1.5 text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Số CCCD (12 số)</label>
                      <input
                        type="text"
                        maxLength={12}
                        placeholder="07909500xxxx"
                        value={newRoommate.cccd_number}
                        onChange={(e) => setNewRoommate({ ...newRoommate, cccd_number: e.target.value })}
                        className="input py-1.5 text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Biển số xe máy</label>
                      <input
                        type="text"
                        placeholder="59A-123.45"
                        value={newRoommate.vehicle_plate}
                        onChange={(e) => setNewRoommate({ ...newRoommate, vehicle_plate: e.target.value })}
                        className="input py-1.5 text-xs"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-2">
                    <button
                      type="button"
                      onClick={() => setIsAddingRoommate(false)}
                      className="btn-secondary py-1 px-3 text-xs font-semibold"
                    >
                      Hủy
                    </button>
                    <button
                      type="submit"
                      disabled={addRoommateMutation.isPending}
                      className="btn-primary py-1 px-3 text-xs font-bold"
                    >
                      {addRoommateMutation.isPending ? 'Đang lưu...' : 'Lưu nhân khẩu'}
                    </button>
                  </div>
                </form>
              )}

              {roommates.length === 0 ? (
                <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                  <Users className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-xs text-slate-500 font-medium">Chưa có người ở cùng nào được đăng ký trong phòng này.</p>
                </div>
              ) : (
                <div className="space-y-2.5">
                  {roommates.map((occupant) => (
                    <div
                      key={occupant.id}
                      className="p-3.5 bg-slate-50/70 border border-slate-100 rounded-2xl flex items-center justify-between shadow-xs"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-sm">
                          {occupant.full_name?.charAt(0) || 'U'}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-bold text-slate-900">{occupant.full_name}</p>
                            {occupant.is_primary_tenant && (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800">
                                Người đứng hợp đồng
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400 mt-0.5">
                            CCCD: {occupant.cccd_number || 'Chưa cung cấp'} • SĐT: {occupant.phone || 'Chưa có'}
                            {occupant.vehicle_plate && ` • Biển số: ${occupant.vehicle_plate}`}
                          </p>
                        </div>
                      </div>
                      <span className="badge badge-emerald text-[11px]">Đang cư trú</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* CỘT PHẢI: KHÁCH THUÊ HIỆN TẠI & TÁC VỤ NHANH */}
          <div className="space-y-6">
            {/* Thẻ khách thuê */}
            <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-emerald-600" /> Cư dân thuê chính
              </h3>

              {room.current_tenant_name ? (
                <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-950 space-y-2">
                  <div>
                    <span className="text-emerald-700 text-[11px] font-medium">Họ và tên:</span>
                    <p className="text-base font-black text-slate-900">{room.current_tenant_name}</p>
                  </div>
                  {room.current_tenant_phone && (
                    <div className="flex items-center gap-2 text-slate-700 font-medium">
                      <Phone className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{room.current_tenant_phone}</span>
                    </div>
                  )}
                  {room.current_tenant_email && (
                    <div className="flex items-center gap-2 text-slate-700 font-medium">
                      <Mail className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{room.current_tenant_email}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-xs text-slate-500 text-center">
                  <Sparkles className="w-6 h-6 text-slate-400 mx-auto mb-2" />
                  <p className="font-semibold text-slate-700">Phòng chưa có khách thuê</p>
                  <p className="text-[11px] text-slate-400 mt-1">Sẵn sàng để lập hợp đồng mới cho người thuê.</p>
                </div>
              )}
            </div>

            {/* Quick Actions Card */}
            <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Tác vụ nhanh</h3>
              <div className="space-y-2">
                <Link
                  to="/invoices"
                  className="w-full py-2.5 px-4 rounded-2xl bg-slate-50 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 text-xs font-bold transition-all flex items-center justify-between"
                >
                  <span className="flex items-center gap-2">
                    <Receipt className="w-4 h-4 text-indigo-500" /> Lập hóa đơn phòng này
                  </span>
                  <span className="text-slate-400">→</span>
                </Link>
                <Link
                  to="/violations"
                  className="w-full py-2.5 px-4 rounded-2xl bg-slate-50 hover:bg-rose-50 hover:text-rose-600 text-slate-700 text-xs font-bold transition-all flex items-center justify-between"
                >
                  <span className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-500" /> Lập biên bản vi phạm
                  </span>
                  <span className="text-slate-400">→</span>
                </Link>
                <Link
                  to="/tickets"
                  className="w-full py-2.5 px-4 rounded-2xl bg-slate-50 hover:bg-amber-50 hover:text-amber-600 text-slate-700 text-xs font-bold transition-all flex items-center justify-between"
                >
                  <span className="flex items-center gap-2">
                    <Wrench className="w-4 h-4 text-amber-500" /> Báo cáo sự cố sửa chữa
                  </span>
                  <span className="text-slate-400">→</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
