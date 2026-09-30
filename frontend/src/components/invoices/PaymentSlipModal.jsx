import { useState } from 'react'
import { X, Upload, CheckCircle2, AlertCircle, FileImage } from 'lucide-react'
import toast from 'react-hot-toast'
import billingService from '@/services/billingService'

export default function PaymentSlipModal({ invoice, isOpen, onClose, onSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  if (!isOpen || !invoice) return null

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setSelectedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedFile) {
      toast.error('Vui lòng chọn ảnh biên lai giao dịch!')
      return
    }

    setSubmitting(true)
    try {
      await billingService.uploadPaymentSlip(invoice.id, selectedFile)
      toast.success('Đã tải lên biên lai! Ban quản lý sẽ đối soát sớm nhất.')
      if (onSuccess) onSuccess()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Tải biên lai thất bại.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-800">Tải biên lai chuyển khoản</h3>
              <p className="text-xs text-slate-500">
                Hóa đơn #{invoice.id} - Phòng {invoice.room_number || invoice.room_id}
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
          {/* Upload Area */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Ảnh chụp màn hình giao dịch ngân hàng / Ủy nhiệm chi
            </label>

            {previewUrl ? (
              <div className="relative rounded-2xl overflow-hidden border-2 border-dashed border-emerald-200 bg-emerald-50/30 p-2">
                <img
                  src={previewUrl}
                  alt="Biên lai xem trước"
                  className="w-full max-h-56 object-contain rounded-xl"
                />
                <button
                  type="button"
                  onClick={() => {
                    setSelectedFile(null)
                    setPreviewUrl(null)
                  }}
                  className="absolute top-4 right-4 bg-slate-900/70 hover:bg-slate-900 text-white p-1.5 rounded-full"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <label className="flex flex-col items-center justify-center w-full h-44 border-2 border-dashed border-slate-300 rounded-2xl cursor-pointer hover:bg-slate-50 hover:border-indigo-400 transition-colors">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <FileImage className="w-10 h-10 text-slate-400 mb-2" />
                  <p className="text-xs text-slate-600 font-medium">Bấm để tải ảnh lên</p>
                  <p className="text-[11px] text-slate-400 mt-1">PNG, JPG, JPEG (Tối đa 10MB)</p>
                </div>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            )}
          </div>

          <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-100 rounded-xl text-xs text-blue-700">
            <AlertCircle className="w-4 h-4 shrink-0 text-blue-600" />
            <span>
              Sau khi tải ảnh, trạng thái hóa đơn sẽ chuyển sang "Đang chờ đối soát". Chủ nhà sẽ duyệt trong 2-4 giờ.
            </span>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary text-xs px-4 py-2"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={submitting || !selectedFile}
              className="btn btn-primary text-xs px-5 py-2 flex items-center gap-1.5"
            >
              {submitting ? 'Đang gửi...' : 'Gửi xác nhận'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
