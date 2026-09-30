import { useState, useEffect } from 'react'
import {
  AlertTriangle,
  Volume2,
  Trash2,
  Flame,
  Users,
  Cigarette,
  HelpCircle,
  Plus,
  CheckCircle,
  Clock,
  Check,
  X,
  FileImage,
  RefreshCw,
} from 'lucide-react'
import toast from 'react-hot-toast'
import AppLayout from '@/components/layout/AppLayout'
import useAuthStore from '@/stores/authStore'
import violationService from '@/services/violationService'
import roomService from '@/services/roomService'

export default function ViolationsPage() {
  const { user } = useAuthStore()
  const isLandlord = user?.role === 'landlord' || user?.role === 'admin'

  const [violations, setViolations] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterSeverity, setFilterSeverity] = useState('all')

  // Create Violation Modal state
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [rooms, setRooms] = useState([])
  const [formData, setFormData] = useState({
    room_id: '',
    violation_type: 'noise',
    severity: 'reminder',
    title: '',
    description: '',
    penalty_amount: '200000',
  })
  const [evidenceFile, setEvidenceFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const fetchViolations = async () => {
    setLoading(true)
    try {
      const data = await violationService.getViolations(
        filterSeverity !== 'all' ? { severity: filterSeverity } : {}
      )
      setViolations(data || [])
    } catch {
      toast.error('Không thể tải danh sách vi phạm.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchViolations()
  }, [filterSeverity])

  useEffect(() => {
    if (createModalOpen && isLandlord) {
      roomService.getRooms().then((data) => {
        setRooms(data || [])
        if (data && data.length > 0) {
          setFormData((prev) => ({ ...prev, room_id: data[0].id }))
        }
      }).catch(() => {})
    }
  }, [createModalOpen, isLandlord])

  const handleAcknowledge = async (id) => {
    try {
      await violationService.acknowledgeViolation(id)
      toast.success('Đã xác nhận biên bản vi phạm.')
      fetchViolations()
    } catch {
      toast.error('Xác nhận thất bại.')
    }
  }

  const handleResolve = async (id) => {
    try {
      await violationService.resolveViolation(id)
      toast.success('Đã đóng biên bản vi phạm.')
      fetchViolations()
    } catch {
      toast.error('Thao tác thất bại.')
    }
  }

  const handleCreateSubmit = async (e) => {
    e.preventDefault()
    if (!formData.room_id || !formData.title.trim()) {
      toast.error('Vui lòng điền đủ thông tin!')
      return
    }

    setSubmitting(true)
    try {
      const dataToSend = new FormData()
      dataToSend.append('room_id', formData.room_id)
      dataToSend.append('violation_type', formData.violation_type)
      dataToSend.append('severity', formData.severity)
      dataToSend.append('title', formData.title)
      dataToSend.append('description', formData.description)
      if (formData.severity === 'penalty') {
        dataToSend.append('penalty_amount', formData.penalty_amount)
      }
      if (evidenceFile) {
        dataToSend.append('evidence_image', evidenceFile)
      }

      await violationService.createViolation(dataToSend)
      toast.success('Đã lập biên bản vi phạm thành công!')
      setCreateModalOpen(false)
      setFormData({
        room_id: rooms[0]?.id || '',
        violation_type: 'noise',
        severity: 'reminder',
        title: '',
        description: '',
        penalty_amount: '200000',
      })
      setEvidenceFile(null)
      fetchViolations()
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Lập biên bản thất bại.')
    } finally {
      setSubmitting(false)
    }
  }

  const categoryIcons = {
    noise: { icon: Volume2, label: 'Tiếng ồn sau 22h', color: 'text-amber-600 bg-amber-50' },
    hygiene: { icon: Trash2, label: 'Vệ sinh & Rác', color: 'text-emerald-600 bg-emerald-50' },
    fire_safety: { icon: Flame, label: 'PCCC & Cổng', color: 'text-rose-600 bg-rose-50' },
    guest_policy: { icon: Users, label: 'Quy định ở ghép', color: 'text-indigo-600 bg-indigo-50' },
    smoking: { icon: Cigarette, label: 'Hút thuốc cấm', color: 'text-purple-600 bg-purple-50' },
    other: { icon: HelpCircle, label: 'Vi phạm khác', color: 'text-slate-600 bg-slate-50' },
  }

  const severityBadges = {
    reminder: { label: 'Cấp 1 - Nhắc nhở', color: 'bg-blue-50 text-blue-700 border-blue-200' },
    warning: { label: 'Cấp 2 - Cảnh cáo', color: 'bg-amber-50 text-amber-700 border-amber-200' },
    penalty: { label: 'Cấp 3 - Phạt tiền', color: 'bg-rose-50 text-rose-700 border-rose-200' },
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-rose-100 flex items-center justify-center text-rose-600">
                <AlertTriangle className="w-5 h-5" />
              </div>
              Cảnh báo Vi phạm & Xử phạt Nội quy
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Hệ thống 3 cấp độ: Nhắc nhở nhẹ nhàng → Cảnh cáo hồ sơ → Phạt tiền tự động vào hóa đơn
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchViolations}
              className="btn btn-secondary text-xs px-3 py-2 flex items-center gap-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Làm mới
            </button>

            {isLandlord && (
              <button
                onClick={() => setCreateModalOpen(true)}
                className="btn btn-primary text-xs px-4 py-2 flex items-center gap-1.5 bg-rose-600 hover:bg-rose-700 shadow-sm"
              >
                <Plus className="w-4 h-4" />
                Lập biên bản vi phạm
              </button>
            )}
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1.5 bg-slate-100 rounded-2xl w-fit">
          {[
            { id: 'all', label: 'Tất cả' },
            { id: 'reminder', label: 'Cấp 1 - Nhắc nhở' },
            { id: 'warning', label: 'Cấp 2 - Cảnh cáo' },
            { id: 'penalty', label: 'Cấp 3 - Phạt tiền' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterSeverity(tab.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-xl transition-all ${
                filterSeverity === tab.id
                  ? 'bg-white text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Violations List */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-24 bg-white rounded-2xl border border-slate-200 animate-pulse" />
            ))}
          </div>
        ) : violations.length === 0 ? (
          <div className="card text-center py-16">
            <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-800">Không có vi phạm nào</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Tòa nhà đang duy trì nề nếp văn minh, an toàn và sạch đẹp.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {violations.map((v) => {
              const cat = categoryIcons[v.violation_type] || categoryIcons.other
              const Icon = cat.icon
              const sev = severityBadges[v.severity] || severityBadges.reminder

              return (
                <div
                  key={v.id}
                  className="card hover:shadow-card-hover transition-all duration-200 border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="flex items-start gap-3.5">
                    <div className={`w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 ${cat.color}`}>
                      <Icon className="w-6 h-6" />
                    </div>

                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm">{v.title}</span>
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                          Phòng {v.room_number || v.room_id}
                        </span>
                        <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${sev.color}`}>
                          {sev.label}
                        </span>
                        {v.status === 'acknowledged' && (
                          <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
                            Cư dân đã cam kết
                          </span>
                        )}
                        {v.status === 'penalized' && (
                          <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-purple-50 text-purple-700">
                            Đã đưa vào hóa đơn
                          </span>
                        )}
                        {v.status === 'resolved' && (
                          <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                            Đã giải quyết xong
                          </span>
                        )}
                      </div>

                      {v.description && (
                        <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
                          {v.description}
                        </p>
                      )}

                      <div className="flex items-center gap-4 text-[11px] text-slate-400">
                        <span>Lập lúc: {v.created_at ? new Date(v.created_at).toLocaleString('vi-VN') : 'Mới'}</span>
                        {v.evidence_image_url && (
                          <a
                            href={v.evidence_image_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-indigo-600 hover:underline flex items-center gap-1 font-medium"
                          >
                            <FileImage className="w-3.5 h-3.5" />
                            Xem ảnh bằng chứng
                          </a>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Actions & Penalties */}
                  <div className="flex items-center justify-between md:justify-end gap-3 pt-3 md:pt-0 border-t md:border-t-0 border-slate-100">
                    {v.severity === 'penalty' && v.penalty_amount > 0 && (
                      <div className="text-left md:text-right">
                        <span className="block text-[10px] text-slate-400 uppercase font-semibold">Tiền phạt</span>
                        <span className="text-sm font-bold text-rose-600">
                          {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(v.penalty_amount)}
                        </span>
                      </div>
                    )}

                    <div className="flex items-center gap-2">
                      {!isLandlord && v.status === 'pending' && (
                        <button
                          onClick={() => handleAcknowledge(v.id)}
                          className="btn btn-primary text-xs px-3 py-1.5 flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700"
                        >
                          <Check className="w-3.5 h-3.5" />
                          Đã đọc & Cam kết
                        </button>
                      )}

                      {isLandlord && v.status !== 'resolved' && (
                        <button
                          onClick={() => handleResolve(v.id)}
                          className="btn btn-secondary text-xs px-3 py-1.5"
                        >
                          Đóng biên bản
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Modal: Lập biên bản vi phạm */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-xl bg-rose-50 flex items-center justify-center text-rose-600">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-800">Lập biên bản vi phạm</h3>
                  <p className="text-xs text-slate-500">Gửi cảnh báo chính thức tới phòng vi phạm</p>
                </div>
              </div>
              <button
                onClick={() => setCreateModalOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="mt-4 space-y-3.5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Căn hộ vi phạm *
                  </label>
                  <select
                    value={formData.room_id}
                    onChange={(e) => setFormData({ ...formData, room_id: e.target.value })}
                    className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  >
                    {rooms.map((r) => (
                      <option key={r.id} value={r.id}>
                        Phòng {r.room_number}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Loại vi phạm *
                  </label>
                  <select
                    value={formData.violation_type}
                    onChange={(e) => setFormData({ ...formData, violation_type: e.target.value })}
                    className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="noise">Tiếng ồn / Hát karaoke sau 22h</option>
                    <option value="hygiene">Vứt rác bừa bãi / Hành lang</option>
                    <option value="fire_safety">An toàn PCCC / Quên khóa cổng</option>
                    <option value="guest_policy">Người lạ ngủ qua đêm không khai báo</option>
                    <option value="smoking">Hút thuốc khu vực cấm</option>
                    <option value="other">Vi phạm khác</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Mức độ xử lý (3 cấp độ) *
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'reminder', label: 'Cấp 1: Nhắc nhở' },
                    { id: 'warning', label: 'Cấp 2: Cảnh cáo' },
                    { id: 'penalty', label: 'Cấp 3: Phạt tiền' },
                  ].map((s) => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => setFormData({ ...formData, severity: s.id })}
                      className={`py-2 px-2 text-xs font-semibold rounded-xl border text-center transition-all ${
                        formData.severity === s.id
                          ? s.id === 'penalty'
                            ? 'bg-rose-50 border-rose-500 text-rose-700'
                            : 'bg-indigo-50 border-indigo-500 text-indigo-700'
                          : 'bg-white border-slate-200 text-slate-600'
                      }`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {formData.severity === 'penalty' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Số tiền phạt (VNĐ)
                  </label>
                  <input
                    type="number"
                    step="10000"
                    value={formData.penalty_amount}
                    onChange={(e) => setFormData({ ...formData, penalty_amount: e.target.value })}
                    className="w-full text-xs font-semibold bg-white border border-rose-200 rounded-xl px-3 py-2 text-rose-700 focus:outline-none focus:ring-2 focus:ring-rose-500"
                  />
                  <p className="text-[11px] text-slate-400 mt-1">
                    Khoản phạt sẽ tự động cộng vào hóa đơn tháng tiếp theo của phòng.
                  </p>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Tiêu đề biên bản *
                </label>
                <input
                  type="text"
                  placeholder="VD: Hát karaoke loa kéo sau 23h đêm"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Mô tả chi tiết sự việc
                </label>
                <textarea
                  rows={2}
                  placeholder="Ghi nhận phản ánh từ các phòng lân cận..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full text-xs bg-white border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Ảnh chụp bằng chứng (nếu có)
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setEvidenceFile(e.target.files[0] || null)}
                  className="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setCreateModalOpen(false)}
                  className="btn btn-secondary text-xs px-4 py-2"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn-primary text-xs px-5 py-2 bg-rose-600 hover:bg-rose-700"
                >
                  {submitting ? 'Đang lưu...' : 'Lập biên bản'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  )
}
