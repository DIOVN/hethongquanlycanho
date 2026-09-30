import { useState, useEffect } from 'react'
import {
  XCircle,
  FileCheck2,
  DollarSign,
  Zap,
  Droplets,
  Plus,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Calculator,
} from 'lucide-react'
import toast from 'react-hot-toast'
import contractService from '@/services/contractService'

export default function MoveOutRefundModal({ contract, onClose, onSuccess }) {
  const [finalElec, setFinalElec] = useState('')
  const [finalWater, setFinalWater] = useState('')
  const [deductions, setDeductions] = useState([])
  const [note, setNote] = useState('')
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [previewData, setPreviewData] = useState(null)

  // Fetch preview when inputs change
  useEffect(() => {
    let isMounted = true
    const fetchPreview = async () => {
      if (!contract?.id) return
      setLoadingPreview(true)
      try {
        const params = {}
        if (finalElec !== '') params.final_electricity_reading = parseFloat(finalElec)
        if (finalWater !== '') params.final_water_reading = parseFloat(finalWater)

        const data = await contractService.previewRefund(contract.id, params)
        if (isMounted) {
          setPreviewData(data)
        }
      } catch (err) {
        console.error('Preview error:', err)
      } finally {
        if (isMounted) setLoadingPreview(false)
      }
    }

    const timer = setTimeout(fetchPreview, 300)
    return () => {
      isMounted = false
      clearTimeout(timer)
    }
  }, [contract?.id, finalElec, finalWater])

  const handleAddDeduction = () => {
    setDeductions([...deductions, { description: '', amount: '' }])
  }

  const handleUpdateDeduction = (index, field, value) => {
    const updated = [...deductions]
    updated[index][field] = value
    setDeductions(updated)
  }

  const handleRemoveDeduction = (index) => {
    setDeductions(deductions.filter((_, i) => i !== index))
  }

  const totalDeductionsAmount = deductions.reduce(
    (sum, d) => sum + (parseFloat(d.amount) || 0),
    0
  )

  const initialDeposit = previewData?.initial_deposit || contract?.deposit_amount || 0
  const utilityCost = previewData?.final_utilities?.total_utility_cost || 0
  const unpaidInvoices = previewData?.unpaid_invoices_total || 0
  const netRefund = initialDeposit - utilityCost - unpaidInvoices - totalDeductionsAmount

  const handleSettleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const validDeductions = deductions
        .filter((d) => d.description.trim() && parseFloat(d.amount) > 0)
        .map((d) => ({
          description: d.description.trim(),
          amount: parseFloat(d.amount),
        }))

      await contractService.settleRefund(contract.id, {
        final_electricity_reading: finalElec !== '' ? parseFloat(finalElec) : null,
        final_water_reading: finalWater !== '' ? parseFloat(finalWater) : null,
        deductions: validDeductions,
        note: note.trim() || undefined,
      })

      toast.success('Đã hoàn tất nghiệm thu & quyết toán trả phòng!')
      if (onSuccess) onSuccess()
      onClose()
    } catch (err) {
      toast.error(err?.response?.data?.message || 'Lỗi khi quyết toán trả phòng')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl border border-slate-100 my-8">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700">
              Quyết toán chuyển đi & Hoàn cọc
            </span>
            <h2 className="text-xl font-bold text-slate-900 mt-1 flex items-center gap-2">
              <FileCheck2 className="w-6 h-6 text-indigo-600" />
              Nghiệm thu Phòng {contract?.room_number || contract?.room_id}
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Khách thuê: <strong>{contract?.tenant_name || 'Khách thuê'}</strong> (SĐT:{' '}
              {contract?.tenant_phone || 'N/A'})
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 min-h-[44px] min-w-[44px] flex items-center justify-center"
          >
            <XCircle className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSettleSubmit} className="mt-5 space-y-6">
          {/* Section 1: Final Utility Meters */}
          <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200/80 space-y-3">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <Calculator className="w-4 h-4 text-indigo-600" />
              1. Chốt chỉ số điện nước cuối kỳ
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-amber-500" />
                  Chỉ số điện cuối (kWh)
                </label>
                <input
                  type="number"
                  step="0.1"
                  placeholder={`Trước đó: ${previewData?.final_utilities?.electricity?.previous_reading || 0}`}
                  value={finalElec}
                  onChange={(e) => setFinalElec(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Tiền điện phát sinh:{' '}
                  {Number(previewData?.final_utilities?.electricity?.cost || 0).toLocaleString('vi-VN')} đ
                </span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                  <Droplets className="w-3.5 h-3.5 text-blue-500" />
                  Chỉ số nước cuối (m³)
                </label>
                <input
                  type="number"
                  step="0.1"
                  placeholder={`Trước đó: ${previewData?.final_utilities?.water?.previous_reading || 0}`}
                  value={finalWater}
                  onChange={(e) => setFinalWater(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Tiền nước phát sinh:{' '}
                  {Number(previewData?.final_utilities?.water?.cost || 0).toLocaleString('vi-VN')} đ
                </span>
              </div>
            </div>
          </div>

          {/* Section 2: Deductions for damage or cleaning */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                2. Khấu trừ hư tổn tài sản & Vệ sinh (nếu có)
              </h3>
              <button
                type="button"
                onClick={handleAddDeduction}
                className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 inline-flex items-center gap-1 px-2.5 py-1 rounded-lg hover:bg-indigo-50"
              >
                <Plus className="w-3.5 h-3.5" />
                Thêm mục trừ
              </button>
            </div>

            {deductions.length === 0 ? (
              <p className="text-xs text-slate-400 italic">
                Chưa có khoản khấu trừ hư hao nào. Bấm &quot;Thêm mục trừ&quot; nếu đồ đạc bị hư hỏng hoặc phòng chưa dọn dẹp.
              </p>
            ) : (
              <div className="space-y-2">
                {deductions.map((d, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Mô tả (VD: Vỡ mặt bàn kính, vệ sinh toilet...)"
                      value={d.description}
                      onChange={(e) => handleUpdateDeduction(index, 'description', e.target.value)}
                      className="flex-1 px-3 py-2 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <input
                      type="number"
                      placeholder="Số tiền trừ (đ)"
                      value={d.amount}
                      onChange={(e) => handleUpdateDeduction(index, 'amount', e.target.value)}
                      className="w-36 px-3 py-2 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveDeduction(index)}
                      className="p-2 text-slate-400 hover:text-rose-600 rounded-xl hover:bg-rose-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section 3: Note */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Ghi chú biên bản bàn giao
            </label>
            <textarea
              rows={2}
              placeholder="VD: Đã kiểm tra đầy đủ chìa khóa, remote, tài sản nguyên vẹn..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Section 4: Live Math Breakdown Card */}
          <div className="rounded-2xl p-5 bg-gradient-to-br from-slate-900 to-indigo-950 text-white shadow-lg space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
              Bảng tổng hợp quyết toán hoàn cọc
            </h4>

            <div className="space-y-1.5 text-xs text-slate-300">
              <div className="flex justify-between">
                <span>Tiền cọc ban đầu (+)</span>
                <span className="font-semibold text-white">
                  {Number(initialDeposit).toLocaleString('vi-VN')} đ
                </span>
              </div>
              <div className="flex justify-between">
                <span>Tiền điện nước cuối kỳ (-)</span>
                <span className="font-semibold text-amber-300">
                  - {Number(utilityCost).toLocaleString('vi-VN')} đ
                </span>
              </div>
              {unpaidInvoices > 0 && (
                <div className="flex justify-between">
                  <span>Hóa đơn cũ còn nợ (-)</span>
                  <span className="font-semibold text-rose-300">
                    - {Number(unpaidInvoices).toLocaleString('vi-VN')} đ
                  </span>
                </div>
              )}
              {totalDeductionsAmount > 0 && (
                <div className="flex justify-between">
                  <span>Khấu trừ hư hại / dọn phòng (-)</span>
                  <span className="font-semibold text-rose-300">
                    - {Number(totalDeductionsAmount).toLocaleString('vi-VN')} đ
                  </span>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-indigo-800/60 flex items-center justify-between">
              <div>
                <span className="text-xs text-indigo-200">
                  {netRefund >= 0 ? 'Số tiền cọc thực trả lại khách:' : 'Khách phải nộp thêm:'}
                </span>
                <p className={`text-2xl font-black ${netRefund >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {Number(Math.abs(netRefund)).toLocaleString('vi-VN')} đ
                </p>
              </div>
              <div className="text-right text-[11px] text-indigo-300">
                Phòng sẽ chuyển về: <span className="font-bold text-white uppercase">vacant</span>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl min-h-[44px]"
            >
              Đóng
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 rounded-xl shadow-md disabled:opacity-50 min-h-[44px] flex items-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              {submitting ? 'Đang quyết toán...' : 'Xác nhận Quyết toán & Trả phòng'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
