import { useState, useEffect } from 'react'
import {
  X,
  Camera,
  Sparkles,
  Zap,
  Droplets,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
  FileText,
} from 'lucide-react'
import toast from 'react-hot-toast'
import roomService from '@/services/roomService'
import billingService from '@/services/billingService'

export default function QuickInvoiceModal({ isOpen, onClose, onSuccess }) {
  const [rooms, setRooms] = useState([])
  const [selectedRoomId, setSelectedRoomId] = useState('')
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [year, setYear] = useState(new Date().getFullYear())

  // Electricity
  const [elecFile, setElecFile] = useState(null)
  const [elecPreview, setElecPreview] = useState(null)
  const [elecReading, setElecReading] = useState('')
  const [elecOcrLoading, setElecOcrLoading] = useState(false)

  // Water
  const [waterFile, setWaterFile] = useState(null)
  const [waterPreview, setWaterPreview] = useState(null)
  const [waterReading, setWaterReading] = useState('')
  const [waterOcrLoading, setWaterOcrLoading] = useState(false)

  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (isOpen) {
      roomService.getRooms().then((data) => {
        setRooms(data || [])
        if (data && data.length > 0) {
          setSelectedRoomId(data[0].id)
        }
      }).catch(() => {})
    }
  }, [isOpen])

  if (!isOpen) return null

  // Trigger OCR for Electricity
  const handleOcrElectricity = async (file) => {
    if (!file || !selectedRoomId) return
    setElecOcrLoading(true)
    try {
      const res = await billingService.scanMeterReading({
        imageFile: file,
        meterType: 'electricity',
        roomId: selectedRoomId,
      })
      if (res?.detected_reading !== undefined) {
        setElecReading(res.detected_reading.toString())
        toast.success(`Gemini Vision đã đọc: ${res.detected_reading} kWh (Độ tin cậy: ${Math.round(res.confidence * 100)}%)`)
      }
    } catch {
      toast.error('Nhận diện số điện thất bại. Bạn có thể nhập tay.')
    } finally {
      setElecOcrLoading(false)
    }
  }

  // Trigger OCR for Water
  const handleOcrWater = async (file) => {
    if (!file || !selectedRoomId) return
    setWaterOcrLoading(true)
    try {
      const res = await billingService.scanMeterReading({
        imageFile: file,
        meterType: 'water',
        roomId: selectedRoomId,
      })
      if (res?.detected_reading !== undefined) {
        setWaterReading(res.detected_reading.toString())
        toast.success(`Gemini Vision đã đọc: ${res.detected_reading} m3 (Độ tin cậy: ${Math.round(res.confidence * 100)}%)`)
      }
    } catch {
      toast.error('Nhận diện số nước thất bại. Bạn có thể nhập tay.')
    } finally {
      setWaterOcrLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedRoomId) {
      toast.error('Vui lòng chọn phòng cần lập hóa đơn!')
      return
    }

    setSubmitting(true)
    try {
      const formData = new FormData()
      formData.append('room_id', selectedRoomId)
      formData.append('month', month)
      formData.append('year', year)
      if (elecReading) formData.append('electricity_reading', elecReading)
      if (elecFile) formData.append('electricity_image', elecFile)
      if (waterReading) formData.append('water_reading', waterReading)
      if (waterFile) formData.append('water_image', waterFile)

      const result = await billingService.createQuickInvoice(formData)
      toast.success(`Phát hành hóa đơn P.${result.room_number} thành công!`)
      if (onSuccess) onSuccess(result)
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Lập hóa đơn thất bại.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center text-white shadow-md shadow-orange-100">
              <Camera className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-800">
                Tạo hóa đơn nhanh tại chỗ (AI OCR)
              </h3>
              <p className="text-xs text-slate-500">
                Chụp ảnh công tơ thực địa, tự tính điện nước & xuất VietQR
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* Room & Period Picker */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Chọn phòng *
              </label>
              <select
                value={selectedRoomId}
                onChange={(e) => setSelectedRoomId(e.target.value)}
                className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              >
                {rooms.map((r) => (
                  <option key={r.id} value={r.id}>
                    Phòng {r.room_number} ({r.status === 'occupied' ? 'Đang thuê' : 'Trống'})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Tháng
              </label>
              <select
                value={month}
                onChange={(e) => setMonth(Number(e.target.value))}
                className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                  <option key={m} value={m}>Tháng {m}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Năm
              </label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
                className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Section: Electricity Meter */}
          <div className="p-4 rounded-2xl bg-amber-50/50 border border-amber-200/60">
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                <Zap className="w-4 h-4 text-amber-600" />
                Công tơ Điện (kWh) - 3.500đ/kWh
              </span>
              {elecOcrLoading && (
                <span className="flex items-center gap-1 text-[11px] text-amber-700 animate-pulse font-medium">
                  <Sparkles className="w-3.5 h-3.5" />
                  Gemini đang đọc số...
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 items-center">
              <div>
                <label className="flex items-center justify-center h-24 border-2 border-dashed border-amber-300 rounded-xl cursor-pointer hover:bg-amber-100/40 transition-colors bg-white relative overflow-hidden">
                  {elecPreview ? (
                    <img src={elecPreview} alt="Đồng hồ điện" className="w-full h-full object-cover" />
                  ) : (
                    <div className="flex flex-col items-center text-amber-700">
                      <Camera className="w-6 h-6 mb-1 text-amber-500" />
                      <span className="text-[11px] font-medium">Chụp / Chọn ảnh điện</span>
                    </div>
                  )}
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    className="hidden"
                    onChange={(e) => {
                      const f = e.target.files[0]
                      if (f) {
                        setElecFile(f)
                        setElecPreview(URL.createObjectURL(f))
                        handleOcrElectricity(f)
                      }
                    }}
                  />
                </label>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Chỉ số điện chốt:
                </label>
                <div className="flex items-center gap-1.5">
                  <input
                    type="number"
                    step="0.1"
                    placeholder="VD: 1428.5"
                    value={elecReading}
                    onChange={(e) => setElecReading(e.target.value)}
                    className="flex-1 text-xs font-semibold px-3 py-2 bg-white border border-amber-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                  <span className="text-xs text-slate-500 font-medium">kWh</span>
                </div>
              </div>
            </div>
          </div>

          {/* Section: Water Meter */}
          <div className="p-4 rounded-2xl bg-sky-50/50 border border-sky-200/60">
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center gap-1.5 text-xs font-bold text-sky-900">
                <Droplets className="w-4 h-4 text-sky-600" />
                Công tơ Nước (m3) - 25.000đ/m3
              </span>
              {waterOcrLoading && (
                <span className="flex items-center gap-1 text-[11px] text-sky-700 animate-pulse font-medium">
                  <Sparkles className="w-3.5 h-3.5" />
                  Gemini đang đọc số...
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 items-center">
              <div>
                <label className="flex items-center justify-center h-24 border-2 border-dashed border-sky-300 rounded-xl cursor-pointer hover:bg-sky-100/40 transition-colors bg-white relative overflow-hidden">
                  {waterPreview ? (
                    <img src={waterPreview} alt="Đồng hồ nước" className="w-full h-full object-cover" />
                  ) : (
                    <div className="flex flex-col items-center text-sky-700">
                      <Camera className="w-6 h-6 mb-1 text-sky-500" />
                      <span className="text-[11px] font-medium">Chụp / Chọn ảnh nước</span>
                    </div>
                  )}
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    className="hidden"
                    onChange={(e) => {
                      const f = e.target.files[0]
                      if (f) {
                        setWaterFile(f)
                        setWaterPreview(URL.createObjectURL(f))
                        handleOcrWater(f)
                      }
                    }}
                  />
                </label>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Chỉ số nước chốt:
                </label>
                <div className="flex items-center gap-1.5">
                  <input
                    type="number"
                    step="0.1"
                    placeholder="VD: 45.0"
                    value={waterReading}
                    onChange={(e) => setWaterReading(e.target.value)}
                    className="flex-1 text-xs font-semibold px-3 py-2 bg-white border border-sky-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
                  />
                  <span className="text-xs text-slate-500 font-medium">m3</span>
                </div>
              </div>
            </div>
          </div>

          {/* Automatic inclusion note */}
          <div className="flex items-center gap-2 p-3 bg-slate-50 border border-slate-200/80 rounded-xl text-xs text-slate-600">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              Hệ thống sẽ tự động gộp tiền phòng, dịch vụ (150.000đ) và các khoản phạt vi phạm tồn đọng vào hóa đơn.
            </span>
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary text-xs px-4 py-2"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn btn-primary text-xs px-5 py-2 flex items-center gap-1.5 bg-gradient-to-r from-indigo-600 to-primary-600 shadow-md"
            >
              <FileText className="w-4 h-4" />
              {submitting ? 'Đang phát hành...' : 'Xuất bản hóa đơn & VietQR'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
