import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Home,
  Building2,
  Users,
  CheckCircle2,
  AlertCircle,
  Wrench,
  Plus,
  Search,
  Filter,
  Grid,
  List,
  Eye,
  Edit3,
  Phone,
  Maximize2,
  Wind,
  CookingPot,
  Car,
  Shirt,
  X,
  Sparkles,
  ChevronRight,
  TrendingUp,
  UserCheck,
  Tag,
  ArrowUpRight,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import AppLayout from '@/components/layout/AppLayout'
import roomService from '@/services/roomService'

export default function RoomsPage() {
  const queryClient = useQueryClient()

  // State bộ lọc & giao diện
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [floorFilter, setFloorFilter] = useState('ALL')
  const [buildingFilter, setBuildingFilter] = useState('ALL')
  const [viewMode, setViewMode] = useState('grid') // 'grid' | 'table'

  // State Modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [editingRoom, setEditingRoom] = useState(null)
  const [selectedRoomDetail, setSelectedRoomDetail] = useState(null)

  // 1. Fetch danh sách phòng
  const { data: rooms = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['rooms', statusFilter, buildingFilter],
    queryFn: async () => {
      const params = {}
      if (statusFilter !== 'ALL') params.status = statusFilter
      if (buildingFilter !== 'ALL') params.building_id = buildingFilter
      const res = await roomService.getRooms(params)
      return res || []
    },
  })

  // 2. Fetch danh sách tòa nhà
  const { data: buildings = [] } = useQuery({
    queryKey: ['buildings'],
    queryFn: async () => {
      const res = await roomService.getBuildings()
      return res || []
    },
  })

  // Fetch người ở cùng cho modal chi tiết
  const { data: roommates = [], refetch: refetchRoommates } = useQuery({
    queryKey: ['roommates', selectedRoomDetail?.id],
    queryFn: async () => {
      if (!selectedRoomDetail?.id) return []
      return await roomService.getRoommates(selectedRoomDetail.id)
    },
    enabled: !!selectedRoomDetail?.id,
  })

  // Mutation cập nhật trạng thái phòng
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }) => roomService.updateRoomStatus(id, status),
    onSuccess: (data) => {
      toast.success(data?.message || 'Cập nhật trạng thái phòng thành công!')
      queryClient.invalidateQueries(['rooms'])
      if (selectedRoomDetail) {
        setSelectedRoomDetail(prev => ({ ...prev, status: data?.data?.status || prev.status }))
      }
    },
    onError: (err) => {
      toast.error(err.response?.data?.error?.message || 'Không thể đổi trạng thái phòng.')
    },
  })

  // Mutation tạo/sửa phòng
  const saveRoomMutation = useMutation({
    mutationFn: async (payload) => {
      if (editingRoom) {
        return await roomService.updateRoom(editingRoom.id, payload)
      } else {
        return await roomService.createRoom(payload)
      }
    },
    onSuccess: () => {
      toast.success(editingRoom ? 'Đã cập nhật thông tin phòng!' : 'Đã tạo phòng mới thành công!')
      setIsCreateModalOpen(false)
      setEditingRoom(null)
      queryClient.invalidateQueries(['rooms'])
    },
    onError: (err) => {
      toast.error(err.response?.data?.error?.message || 'Thao tác lưu phòng thất bại.')
    },
  })

  // Mutation thêm người ở cùng
  const addRoommateMutation = useMutation({
    mutationFn: (payload) => roomService.addRoommate(selectedRoomDetail.id, payload),
    onSuccess: () => {
      toast.success('Đã thêm nhân khẩu vào phòng thành công!')
      refetchRoommates()
    },
    onError: (err) => {
      toast.error(err.response?.data?.error?.message || 'Không thể thêm nhân khẩu.')
    },
  })

  // Lọc dữ liệu client-side theo từ khóa tìm kiếm & tầng
  const filteredRooms = useMemo(() => {
    return rooms.filter((room) => {
      const matchSearch =
        !searchTerm.trim() ||
        room.room_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        room.building_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        room.current_tenant_name?.toLowerCase().includes(searchTerm.toLowerCase())

      const matchStatus =
        statusFilter === 'ALL' || room.status === statusFilter

      const matchFloor =
        floorFilter === 'ALL' || String(room.floor) === String(floorFilter)

      return matchSearch && matchStatus && matchFloor
    })
  }, [rooms, searchTerm, statusFilter, floorFilter])

  // Thống kê nhanh KPIs
  const stats = useMemo(() => {
    const total = rooms.length
    const occupied = rooms.filter((r) => r.status === 'occupied').length
    const vacant = rooms.filter((r) => r.status === 'vacant').length
    const maintenance = rooms.filter((r) => r.status === 'maintenance').length
    const occupancyRate = total > 0 ? Math.round((occupied / total) * 100) : 0
    return { total, occupied, vacant, maintenance, occupancyRate }
  }, [rooms])

  // Danh sách các tầng có sẵn
  const availableFloors = useMemo(() => {
    const floors = new Set(rooms.map((r) => r.floor).filter(Boolean))
    return Array.from(floors).sort((a, b) => a - b)
  }, [rooms])

  const formatMoney = (val) => {
    if (!val) return '0 đ'
    return new Intl.NumberFormat('vi-VN').format(val) + ' đ'
  }

  const renderStatusBadge = (status) => {
    switch (status) {
      case 'occupied':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60 shadow-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Đang thuê
          </span>
        )
      case 'vacant':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200/60 shadow-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            Phòng trống
          </span>
        )
      case 'maintenance':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200/60 shadow-xs">
            <Wrench className="w-3 h-3 text-amber-500" />
            Đang sửa chữa
          </span>
        )
      default:
        return <span className="badge badge-gray">{status}</span>
    }
  }

  return (
    <AppLayout>
      <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
        {/* HEADER SECTION */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
          <div>
            <div className="flex items-center gap-2 text-indigo-600 font-semibold text-xs uppercase tracking-wider mb-1">
              <Building2 className="w-4 h-4" />
              Quản lý Căn hộ & Bất động sản SAMS
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Danh sách Phòng & Căn hộ
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Theo dõi tình trạng lấp đầy, giá thuê, người ở cùng và kiểm soát vận hành toàn bộ tòa nhà.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <Link
              to="/rooms/search"
              className="btn-secondary flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-2xl"
              title="Xem trang tìm phòng công khai"
            >
              <ArrowUpRight className="w-4 h-4 text-slate-500" />
              Cổng tìm phòng Public
            </Link>
            <button
              onClick={() => {
                setEditingRoom(null)
                setIsCreateModalOpen(true)
              }}
              className="btn-primary flex items-center gap-2 px-4 py-2.5 text-xs font-bold rounded-2xl shadow-lg shadow-indigo-600/20"
            >
              <Plus className="w-4 h-4" />
              Thêm phòng mới
            </button>
          </div>
        </div>

        {/* KPI SUMMARY CARDS */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5 sm:gap-4">
          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-100 shadow-xs hover:border-indigo-100 transition-all">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium text-slate-500">Tổng số phòng</span>
              <div className="w-8 h-8 rounded-xl bg-slate-50 flex items-center justify-center text-slate-600">
                <Home className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900">{stats.total}</div>
            <div className="text-xs text-slate-400 mt-1">Toàn bộ dự án</div>
          </div>

          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-100 shadow-xs hover:border-emerald-100 transition-all">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium text-emerald-700">Đang cho thuê</span>
              <div className="w-8 h-8 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
                <CheckCircle2 className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-emerald-600">{stats.occupied}</div>
            <div className="text-xs text-emerald-600/80 mt-1 font-medium">Có khách đang ở</div>
          </div>

          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-100 shadow-xs hover:border-blue-100 transition-all">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium text-blue-700">Phòng trống</span>
              <div className="w-8 h-8 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600">
                <Sparkles className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-blue-600">{stats.vacant}</div>
            <div className="text-xs text-blue-600/80 mt-1 font-medium">Sẵn sàng đón khách</div>
          </div>

          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-100 shadow-xs hover:border-amber-100 transition-all">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium text-amber-700">Đang bảo trì</span>
              <div className="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600">
                <Wrench className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-amber-600">{stats.maintenance}</div>
            <div className="text-xs text-amber-600/80 mt-1 font-medium">Đang tân trang / sửa</div>
          </div>

          <div className="bg-gradient-to-br from-indigo-900 to-slate-900 p-4 sm:p-5 rounded-2xl text-white shadow-md col-span-2 lg:col-span-1">
            <div className="flex items-center justify-between text-indigo-200 mb-2">
              <span className="text-xs font-medium">Tỷ lệ lấp đầy</span>
              <TrendingUp className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-black text-white">{stats.occupancyRate}%</div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2.5 overflow-hidden">
              <div
                className="bg-emerald-400 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${stats.occupancyRate}%` }}
              />
            </div>
          </div>
        </div>

        {/* CONTROLS & FILTER BAR */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-100 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-3.5">
          {/* Status Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
            {[
              { id: 'ALL', label: 'Tất cả phòng', count: stats.total },
              { id: 'occupied', label: 'Đang thuê', count: stats.occupied },
              { id: 'vacant', label: 'Phòng trống', count: stats.vacant },
              { id: 'maintenance', label: 'Bảo trì', count: stats.maintenance },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                  statusFilter === tab.id
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
                }`}
              >
                <span>{tab.label}</span>
                <span
                  className={`px-1.5 py-0.5 rounded-md text-[10px] ${
                    statusFilter === tab.id ? 'bg-white/20 text-white' : 'bg-slate-200 text-slate-700'
                  }`}
                >
                  {tab.count}
                </span>
              </button>
            ))}
          </div>

          {/* Search & Select Filters */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-2.5">
            {/* Search Input */}
            <div className="relative flex-1 sm:w-60">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Tìm số phòng, tên khách..."
                className="input pl-9 py-1.5 text-xs rounded-xl"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Filter by Floor */}
            {availableFloors.length > 0 && (
              <select
                value={floorFilter}
                onChange={(e) => setFloorFilter(e.target.value)}
                className="select py-1.5 text-xs rounded-xl w-28"
              >
                <option value="ALL">Tất cả tầng</option>
                {availableFloors.map((fl) => (
                  <option key={fl} value={fl}>
                    Tầng {fl}
                  </option>
                ))}
              </select>
            )}

            {/* Filter by Building */}
            {buildings.length > 0 && (
              <select
                value={buildingFilter}
                onChange={(e) => setBuildingFilter(e.target.value)}
                className="select py-1.5 text-xs rounded-xl w-36 max-w-[150px] truncate"
              >
                <option value="ALL">Tất cả tòa nhà</option>
                {buildings.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            )}

            {/* View Switch Buttons */}
            <div className="flex items-center bg-slate-100 p-0.5 rounded-xl">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-lg text-slate-600 transition-colors ${
                  viewMode === 'grid' ? 'bg-white shadow-xs text-indigo-600' : 'hover:text-slate-900'
                }`}
                title="Dạng lưới thẻ (Grid)"
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`p-1.5 rounded-lg text-slate-600 transition-colors ${
                  viewMode === 'table' ? 'bg-white shadow-xs text-indigo-600' : 'hover:text-slate-900'
                }`}
                title="Dạng bảng chi tiết (Table)"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* MAIN CONTENT: ROOMS LIST */}
        {isLoading ? (
          <div className="py-20 flex flex-col items-center justify-center text-slate-400">
            <div className="spinner w-8 h-8 text-indigo-600 mb-3" />
            <p className="text-sm font-medium">Đang tải danh sách phòng căn hộ...</p>
          </div>
        ) : isError ? (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 p-6 rounded-2xl text-center">
            <AlertCircle className="w-8 h-8 text-rose-500 mx-auto mb-2" />
            <h3 className="font-bold text-base">Không thể tải danh sách phòng</h3>
            <p className="text-xs text-rose-600 mt-1">Đã có lỗi kết nối tới máy chủ API.</p>
            <button
              onClick={() => refetch()}
              className="mt-4 px-4 py-2 bg-rose-600 text-white rounded-xl text-xs font-semibold hover:bg-rose-700 transition-colors"
            >
              Thử lại ngay
            </button>
          </div>
        ) : filteredRooms.length === 0 ? (
          <div className="bg-white rounded-3xl border border-slate-100 p-12 text-center shadow-xs">
            <div className="w-16 h-16 rounded-3xl bg-slate-50 flex items-center justify-center mx-auto mb-3 text-slate-400">
              <Home className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-slate-800">Không tìm thấy phòng nào phù hợp</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Thử thay đổi bộ lọc trạng thái, tầng hoặc tìm kiếm bằng từ khóa khác.
            </p>
            {(searchTerm || statusFilter !== 'ALL' || floorFilter !== 'ALL' || buildingFilter !== 'ALL') && (
              <button
                onClick={() => {
                  setSearchTerm('')
                  setStatusFilter('ALL')
                  setFloorFilter('ALL')
                  setBuildingFilter('ALL')
                }}
                className="mt-4 text-xs font-bold text-indigo-600 hover:underline"
              >
                Xóa tất cả bộ lọc
              </button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          /* =======================================
             GRID VIEW (CARD PREVIEWS)
             ======================================= */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5">
            {filteredRooms.map((room) => (
              <div
                key={room.id}
                className="bg-white rounded-3xl border border-slate-100 shadow-xs hover:shadow-lg hover:border-indigo-200 transition-all duration-200 flex flex-col justify-between overflow-hidden group"
              >
                <div className="p-5">
                  {/* Top Bar: Room Number & Status */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-10 h-10 rounded-2xl bg-indigo-50 text-indigo-700 flex items-center justify-center font-black text-base font-mono shadow-xs group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                        {room.room_number}
                      </div>
                      <div>
                        <h3 className="font-bold text-slate-900 text-sm leading-tight">
                          Phòng {room.room_number}
                        </h3>
                        <p className="text-[11px] text-slate-400">
                          Tầng {room.floor || 1} • {room.area_sqm || 25} m²
                        </p>
                      </div>
                    </div>
                    <div>{renderStatusBadge(room.status)}</div>
                  </div>

                  {/* Building & Address */}
                  <div className="flex items-start gap-1.5 text-xs text-slate-500 mb-3 bg-slate-50/70 p-2.5 rounded-xl border border-slate-100/60">
                    <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                    <span className="truncate font-medium">{room.building_name || 'Tòa nhà Căn hộ SAMS'}</span>
                  </div>

                  {/* Rent Price */}
                  <div className="mb-4">
                    <span className="text-xs text-slate-400 font-medium">Giá thuê:</span>
                    <div className="text-lg font-black text-indigo-600">
                      {formatMoney(room.base_price)}
                      <span className="text-xs text-slate-400 font-normal"> /tháng</span>
                    </div>
                  </div>

                  {/* Amenities Icons */}
                  <div className="flex items-center gap-3 py-2 border-t border-b border-slate-50 mb-3.5 text-slate-600 text-xs">
                    <span
                      title={room.has_balcony ? 'Có ban công thoáng' : 'Không có ban công'}
                      className={`flex items-center gap-1 ${room.has_balcony ? 'text-indigo-600 font-semibold' : 'text-slate-300'}`}
                    >
                      <Wind className="w-3.5 h-3.5" /> Ban công
                    </span>
                    <span
                      title={room.has_washing_machine ? 'Có máy giặt riêng' : 'Không có máy giặt'}
                      className={`flex items-center gap-1 ${room.has_washing_machine ? 'text-indigo-600 font-semibold' : 'text-slate-300'}`}
                    >
                      <Shirt className="w-3.5 h-3.5" /> Máy giặt
                    </span>
                    <span
                      title={room.has_kitchen ? 'Bếp nấu ăn riêng' : 'Không có bếp'}
                      className={`flex items-center gap-1 ${room.has_kitchen ? 'text-indigo-600 font-semibold' : 'text-slate-300'}`}
                    >
                      <CookingPot className="w-3.5 h-3.5" /> Bếp
                    </span>
                  </div>

                  {/* Current Tenant / Availability status info */}
                  {room.status === 'occupied' && room.current_tenant_name ? (
                    <div className="p-2.5 rounded-xl bg-emerald-50/60 border border-emerald-100/60 text-xs text-emerald-950 flex items-center justify-between">
                      <div className="flex items-center gap-2 truncate">
                        <div className="w-6 h-6 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0">
                          <UserCheck className="w-3.5 h-3.5" />
                        </div>
                        <div className="truncate">
                          <p className="font-bold text-[11px] truncate">{room.current_tenant_name}</p>
                          <p className="text-[10px] text-emerald-700 truncate">{room.current_tenant_phone || 'Đã có hợp đồng'}</p>
                        </div>
                      </div>
                    </div>
                  ) : room.status === 'vacant' ? (
                    <div className="p-2.5 rounded-xl bg-blue-50/60 border border-blue-100/60 text-xs text-blue-900 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-blue-500 shrink-0" />
                      <span className="text-[11px] font-medium">Sẵn sàng lập hợp đồng cho khách thuê</span>
                    </div>
                  ) : (
                    <div className="p-2.5 rounded-xl bg-amber-50/60 border border-amber-100/60 text-xs text-amber-900 flex items-center gap-2">
                      <Wrench className="w-4 h-4 text-amber-500 shrink-0" />
                      <span className="text-[11px] font-medium">Đang kiểm tra bảo trì kỹ thuật</span>
                    </div>
                  )}
                </div>

                {/* Card Footer: Quick Actions */}
                <div className="px-5 py-3 bg-slate-50/60 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    onClick={() => setSelectedRoomDetail(room)}
                    className="flex-1 py-1.5 px-3 rounded-xl bg-white border border-slate-200 text-slate-700 text-xs font-bold hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 transition-all flex items-center justify-center gap-1.5 shadow-xs"
                  >
                    <Eye className="w-3.5 h-3.5" /> Chi tiết & Nhân khẩu
                  </button>

                  <div className="flex items-center gap-1">
                    {/* Status quick switcher dropdown */}
                    <select
                      value={room.status}
                      onChange={(e) => updateStatusMutation.mutate({ id: room.id, status: e.target.value })}
                      className="text-[11px] font-semibold py-1.5 px-2 bg-white border border-slate-200 rounded-xl text-slate-700 outline-none hover:border-indigo-300"
                      title="Đổi nhanh trạng thái"
                    >
                      <option value="vacant">Trống</option>
                      <option value="occupied">Đang thuê</option>
                      <option value="maintenance">Bảo trì</option>
                    </select>

                    <button
                      onClick={() => {
                        setEditingRoom(room)
                        setIsCreateModalOpen(true)
                      }}
                      className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-white rounded-lg transition-colors"
                      title="Sửa thông tin phòng"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* =======================================
             TABLE VIEW
             ======================================= */
          <div className="bg-white rounded-3xl border border-slate-100 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50/80 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100 text-[11px]">
                  <tr>
                    <th className="py-3.5 px-4">Số phòng</th>
                    <th className="py-3.5 px-4">Tòa nhà</th>
                    <th className="py-3.5 px-4">Tầng</th>
                    <th className="py-3.5 px-4">Diện tích</th>
                    <th className="py-3.5 px-4">Giá thuê / tháng</th>
                    <th className="py-3.5 px-4">Tiện ích</th>
                    <th className="py-3.5 px-4">Khách đang thuê</th>
                    <th className="py-3.5 px-4">Trạng thái</th>
                    <th className="py-3.5 px-4 text-right">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                  {filteredRooms.map((room) => (
                    <tr key={room.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4">
                        <span className="font-mono font-bold text-slate-900 text-sm bg-slate-100 px-2 py-0.5 rounded-lg">
                          {room.room_number}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-slate-800">
                        {room.building_name || 'Căn hộ SAMS'}
                      </td>
                      <td className="py-3.5 px-4 text-slate-500">Tầng {room.floor || 1}</td>
                      <td className="py-3.5 px-4 text-slate-500">{room.area_sqm || 25} m²</td>
                      <td className="py-3.5 px-4 font-bold text-indigo-600">
                        {formatMoney(room.base_price)}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-1.5 text-slate-400">
                          {room.has_balcony && <span className="p-1 rounded bg-slate-100 text-indigo-600" title="Ban công"><Wind className="w-3 h-3" /></span>}
                          {room.has_washing_machine && <span className="p-1 rounded bg-slate-100 text-indigo-600" title="Máy giặt"><Shirt className="w-3 h-3" /></span>}
                          {room.has_kitchen && <span className="p-1 rounded bg-slate-100 text-indigo-600" title="Bếp"><CookingPot className="w-3 h-3" /></span>}
                          {room.has_parking && <span className="p-1 rounded bg-slate-100 text-indigo-600" title="Chỗ để xe"><Car className="w-3 h-3" /></span>}
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        {room.current_tenant_name ? (
                          <div className="text-slate-900 font-bold">
                            {room.current_tenant_name}
                            {room.current_tenant_phone && (
                              <div className="text-[11px] text-slate-400 font-normal">{room.current_tenant_phone}</div>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-400 italic">Chưa có khách</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">{renderStatusBadge(room.status)}</td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => setSelectedRoomDetail(room)}
                            className="px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-600 hover:bg-indigo-100 font-bold transition-colors"
                          >
                            Xem
                          </button>
                          <button
                            onClick={() => {
                              setEditingRoom(room)
                              setIsCreateModalOpen(true)
                            }}
                            className="p-1.5 text-slate-400 hover:text-indigo-600 rounded-lg"
                            title="Sửa phòng"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* MODAL: THÊM / CHỈNH SỬA PHÒNG */}
        {isCreateModalOpen && (
          <RoomFormModal
            room={editingRoom}
            buildings={buildings}
            onClose={() => {
              setIsCreateModalOpen(false)
              setEditingRoom(null)
            }}
            onSave={(formData) => saveRoomMutation.mutate(formData)}
            isSaving={saveRoomMutation.isPending}
          />
        )}

        {/* MODAL: CHI TIẾT PHÒNG & NHÂN KHẨU (ROOMMATES) */}
        {selectedRoomDetail && (
          <RoomDetailModal
            room={selectedRoomDetail}
            roommates={roommates}
            onClose={() => setSelectedRoomDetail(null)}
            onAddRoommate={(roommateData) => addRoommateMutation.mutate(roommateData)}
            isAddingRoommate={addRoommateMutation.isPending}
            onStatusChange={(newStatus) => updateStatusMutation.mutate({ id: selectedRoomDetail.id, status: newStatus })}
          />
        )}
      </div>
    </AppLayout>
  )
}

/* =========================================================================
   MODAL 1: FORM TẠO HOẶC SỬA PHÒNG
   ========================================================================= */
function RoomFormModal({ room, buildings, onClose, onSave, isSaving }) {
  const [formData, setFormData] = useState({
    building_id: room?.building_id || buildings[0]?.id || 1,
    room_number: room?.room_number || '',
    floor: room?.floor || 1,
    base_price: room?.base_price || 3500000,
    area_sqm: room?.area_sqm || 28,
    status: room?.status || 'vacant',
    has_balcony: room?.has_balcony || false,
    has_washing_machine: room?.has_washing_machine || false,
    has_kitchen: room?.has_kitchen || false,
    has_parking: room?.has_parking || false,
    description: room?.description || '',
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.room_number) {
      toast.error('Vui lòng nhập số phòng!')
      return
    }
    if (!formData.base_price || Number(formData.base_price) <= 0) {
      toast.error('Vui lòng nhập giá phòng hợp lệ!')
      return
    }
    onSave(formData)
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-100 max-w-lg w-full p-6 sm:p-7 overflow-y-auto max-h-[90vh]">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Home className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                {room ? `Chỉnh sửa Phòng ${room.room_number}` : 'Thêm Phòng Căn hộ Mới'}
              </h2>
              <p className="text-xs text-slate-500">Nhập đầy đủ thông tin để lưu vào hệ thống</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-xl hover:bg-slate-100 text-slate-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Thuộc Tòa nhà *</label>
            <select
              value={formData.building_id}
              onChange={(e) => setFormData({ ...formData, building_id: Number(e.target.value) })}
              className="select w-full"
            >
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name} - {b.address}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Số phòng *</label>
              <input
                type="text"
                value={formData.room_number}
                onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
                placeholder="vd: 101, 202..."
                required
                className="input"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Tầng</label>
              <input
                type="number"
                value={formData.floor}
                onChange={(e) => setFormData({ ...formData, floor: Number(e.target.value) })}
                className="input"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Giá thuê (VNĐ / tháng) *</label>
              <input
                type="number"
                step="50000"
                value={formData.base_price}
                onChange={(e) => setFormData({ ...formData, base_price: Number(e.target.value) })}
                required
                className="input"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Diện tích (m²)</label>
              <input
                type="number"
                step="0.5"
                value={formData.area_sqm}
                onChange={(e) => setFormData({ ...formData, area_sqm: Number(e.target.value) })}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Trạng thái phòng</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              className="select w-full"
            >
              <option value="vacant">Phòng trống (vacant)</option>
              <option value="occupied">Đang cho thuê (occupied)</option>
              <option value="maintenance">Đang sửa chữa / bảo trì (maintenance)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-2">Tiện ích đi kèm:</label>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <label className="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
                <input
                  type="checkbox"
                  checked={formData.has_balcony}
                  onChange={(e) => setFormData({ ...formData, has_balcony: e.target.checked })}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <Wind className="w-3.5 h-3.5 text-slate-600" />
                <span>Có ban công</span>
              </label>

              <label className="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
                <input
                  type="checkbox"
                  checked={formData.has_washing_machine}
                  onChange={(e) => setFormData({ ...formData, has_washing_machine: e.target.checked })}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <Shirt className="w-3.5 h-3.5 text-slate-600" />
                <span>Có máy giặt</span>
              </label>

              <label className="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
                <input
                  type="checkbox"
                  checked={formData.has_kitchen}
                  onChange={(e) => setFormData({ ...formData, has_kitchen: e.target.checked })}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <CookingPot className="w-3.5 h-3.5 text-slate-600" />
                <span>Bếp riêng</span>
              </label>

              <label className="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
                <input
                  type="checkbox"
                  checked={formData.has_parking}
                  onChange={(e) => setFormData({ ...formData, has_parking: e.target.checked })}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <Car className="w-3.5 h-3.5 text-slate-600" />
                <span>Chỗ để xe</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Mô tả thêm</label>
            <textarea
              rows={2}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Ghi chú về nội thất, cửa sổ, đồng hồ điện..."
              className="textarea w-full text-xs"
            />
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
            <button type="button" onClick={onClose} className="btn-secondary py-2 px-4 text-xs font-semibold">
              Hủy
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="btn-primary py-2 px-5 text-xs font-bold flex items-center gap-2"
            >
              {isSaving && <span className="spinner" />}
              {room ? 'Lưu thay đổi' : 'Tạo phòng'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* =========================================================================
   MODAL 2: CHI TIẾT PHÒNG & DANH SÁCH NHÂN KHẨU (ROOMMATES)
   ========================================================================= */
function RoomDetailModal({ room, roommates, onClose, onAddRoommate, isAddingRoommate, onStatusChange }) {
  const [activeTab, setActiveTab] = useState('info') // 'info' | 'roommates'
  const [isAddingNewRoommate, setIsAddingNewRoommate] = useState(false)
  const [newRoommate, setNewRoommate] = useState({
    full_name: '',
    phone: '',
    cccd_number: '',
    date_of_birth: '',
    gender: 'Nam',
    hometown: '',
    vehicle_plate: '',
  })

  const handleRoommateSubmit = (e) => {
    e.preventDefault()
    if (!newRoommate.full_name.trim()) {
      toast.error('Vui lòng nhập họ tên người ở cùng!')
      return
    }
    if (newRoommate.cccd_number && !/^\d{12}$/.test(newRoommate.cccd_number)) {
      toast.error('Số CCCD phải gồm đúng 12 chữ số!')
      return
    }
    onAddRoommate(newRoommate)
    setNewRoommate({
      full_name: '',
      phone: '',
      cccd_number: '',
      date_of_birth: '',
      gender: 'Nam',
      hometown: '',
      vehicle_plate: '',
    })
    setIsAddingNewRoommate(false)
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-100 max-w-2xl w-full p-6 sm:p-8 overflow-y-auto max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white font-mono font-black text-lg flex items-center justify-center shadow-lg shadow-indigo-600/30">
              {room.room_number}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black text-slate-900">Phòng {room.room_number}</h2>
                <span className="badge badge-indigo">Tầng {room.floor || 1}</span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">{room.building_name || 'Tòa nhà Căn hộ SAMS'}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-xl hover:bg-slate-100 text-slate-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-2xl mb-5 text-xs font-bold">
          <button
            onClick={() => setActiveTab('info')}
            className={`flex-1 py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'info' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Home className="w-4 h-4" /> Thông tin phòng & Tiện ích
          </button>
          <button
            onClick={() => setActiveTab('roommates')}
            className={`flex-1 py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'roommates' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Users className="w-4 h-4" /> Cư dân & Người ở cùng ({roommates.length})
          </button>
        </div>

        {/* TAB 1: THÔNG TIN PHÒNG */}
        {activeTab === 'info' && (
          <div className="space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100">
                <span className="text-xs text-slate-400">Giá thuê cơ bản</span>
                <p className="text-base font-black text-indigo-600 mt-0.5">
                  {new Intl.NumberFormat('vi-VN').format(room.base_price)} đ
                </p>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100">
                <span className="text-xs text-slate-400">Diện tích</span>
                <p className="text-base font-black text-slate-800 mt-0.5">{room.area_sqm || 25} m²</p>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100 col-span-2 sm:col-span-1">
                <span className="text-xs text-slate-400">Trạng thái</span>
                <div className="mt-1">
                  <select
                    value={room.status}
                    onChange={(e) => onStatusChange(e.target.value)}
                    className="text-xs font-bold py-1 px-2 border border-slate-200 rounded-lg bg-white"
                  >
                    <option value="vacant">Phòng trống</option>
                    <option value="occupied">Đang thuê</option>
                    <option value="maintenance">Đang bảo trì</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Tiện ích phòng */}
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Tiện ích trong phòng</h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                <div className={`p-3 rounded-2xl border flex items-center gap-2 ${room.has_balcony ? 'bg-indigo-50/50 border-indigo-200 text-indigo-900 font-bold' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
                  <Wind className="w-4 h-4 text-indigo-500" /> Ban công riêng
                </div>
                <div className={`p-3 rounded-2xl border flex items-center gap-2 ${room.has_washing_machine ? 'bg-indigo-50/50 border-indigo-200 text-indigo-900 font-bold' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
                  <Shirt className="w-4 h-4 text-indigo-500" /> Máy giặt riêng
                </div>
                <div className={`p-3 rounded-2xl border flex items-center gap-2 ${room.has_kitchen ? 'bg-indigo-50/50 border-indigo-200 text-indigo-900 font-bold' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
                  <CookingPot className="w-4 h-4 text-indigo-500" /> Bếp nấu ăn
                </div>
                <div className={`p-3 rounded-2xl border flex items-center gap-2 ${room.has_parking ? 'bg-indigo-50/50 border-indigo-200 text-indigo-900 font-bold' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
                  <Car className="w-4 h-4 text-indigo-500" /> Chỗ để xe máy
                </div>
              </div>
            </div>

            {/* Khách đại diện đang thuê */}
            {room.current_tenant_name && (
              <div className="p-4 bg-emerald-50/50 border border-emerald-100 rounded-2xl">
                <span className="text-xs text-emerald-800 font-bold uppercase tracking-wider">Cư dân đại diện thuê phòng</span>
                <div className="flex items-center justify-between mt-2">
                  <div>
                    <p className="text-sm font-black text-slate-900">{room.current_tenant_name}</p>
                    <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                      <Phone className="w-3.5 h-3.5 text-emerald-600" /> {room.current_tenant_phone || 'Chưa cập nhật SĐT'}
                    </p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-600 text-white">
                    Hợp đồng hiệu lực
                  </span>
                </div>
              </div>
            )}

            {room.description && (
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Mô tả phòng</h4>
                <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-2xl">{room.description}</p>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: DANH SÁCH NGƯỜI Ở CÙNG (ROOMMATES) */}
        {activeTab === 'roommates' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Khai báo nhân khẩu & tạm trú theo quy định quản lý căn hộ.
              </span>
              <button
                onClick={() => setIsAddingNewRoommate(!isAddingNewRoommate)}
                className="btn-primary py-1.5 px-3 text-xs font-bold rounded-xl flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Thêm người ở cùng
              </button>
            </div>

            {/* FORM THÊM NHÂN KHẨU */}
            {isAddingNewRoommate && (
              <form onSubmit={handleRoommateSubmit} className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3 animate-in fade-in duration-200">
                <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
                  Đăng ký nhân khẩu mới
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Họ và tên *</label>
                    <input
                      type="text"
                      required
                      placeholder="Nguyễn Văn B..."
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
                    <label className="block text-slate-700 font-semibold mb-1">Biển số xe</label>
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
                    onClick={() => setIsAddingNewRoommate(false)}
                    className="btn-secondary py-1 px-3 text-xs font-semibold"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    disabled={isAddingRoommate}
                    className="btn-primary py-1 px-3 text-xs font-bold"
                  >
                    {isAddingRoommate ? 'Đang lưu...' : 'Xác nhận thêm'}
                  </button>
                </div>
              </form>
            )}

            {/* DANH SÁCH ROOMMATES HIỆN TẠI */}
            {roommates.length === 0 ? (
              <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <Users className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-xs text-slate-500 font-medium">Chưa có người ở cùng nào được đăng ký trong phòng này.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {roommates.map((occupant) => (
                  <div
                    key={occupant.id}
                    className="p-3.5 bg-white border border-slate-100 rounded-2xl flex items-center justify-between shadow-xs hover:border-indigo-100 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-700 font-bold flex items-center justify-center text-xs">
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
        )}
      </div>
    </div>
  )
}
