import { useState } from 'react'
import { X, Copy, Check, Download, QrCode, Upload, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'

export default function VietQRModal({ invoice, isOpen, onClose, onOpenPaymentSlip }) {
  const [copiedField, setCopiedField] = useState(null)

  if (!isOpen || !invoice) return null

  const handleCopy = (text, fieldName) => {
    navigator.clipboard.writeText(text)
    setCopiedField(fieldName)
    toast.success(`Đã sao chép ${fieldName}!`)
    setTimeout(() => setCopiedField(null), 2000)
  }

  const qrImageUrl =
    invoice.vietqr_image_url ||
    invoice.vietqr_url ||
    `https://img.vietqr.io/image/970422-0987654321-compact2.png?amount=${Math.round(invoice.total_amount)}&addInfo=${encodeURIComponent(invoice.payment_ref || '')}`

  const amountFormatted = new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(invoice.total_amount || 0)

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <QrCode className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-800">Mã thanh toán VietQR</h3>
              <p className="text-xs text-slate-500">Chuyển khoản 24/7 Napas</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* QR Code Container */}
        <div className="mt-4 flex flex-col items-center">
          <div className="p-3 bg-white rounded-2xl border-2 border-indigo-100 shadow-sm relative group">
            <img
              src={qrImageUrl}
              alt="Mã thanh toán VietQR"
              className="w-64 h-64 object-contain rounded-xl"
            />
          </div>
          <p className="text-[11px] text-slate-400 mt-2 text-center">
            Mở app ngân hàng bất kỳ để quét mã (Số tiền & Nội dung tự điền)
          </p>
        </div>

        {/* Detail Fields for Manual Copy */}
        <div className="mt-4 space-y-2.5 bg-slate-50 p-3.5 rounded-2xl border border-slate-200/60 text-xs">
          {/* Số tiền */}
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Số tiền:</span>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-slate-900 text-sm text-indigo-600">
                {amountFormatted}
              </span>
              <button
                onClick={() => handleCopy(Math.round(invoice.total_amount).toString(), 'số tiền')}
                className="p-1 hover:bg-slate-200 rounded text-slate-500"
              >
                {copiedField === 'số tiền' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Ngân hàng */}
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Ngân hàng:</span>
            <span className="font-semibold text-slate-800">MBBank (Ngân hàng Quân Đội)</span>
          </div>

          {/* Số tài khoản */}
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Số tài khoản:</span>
            <div className="flex items-center gap-1.5">
              <span className="font-mono font-semibold text-slate-800">0987654321</span>
              <button
                onClick={() => handleCopy('0987654321', 'số tài khoản')}
                className="p-1 hover:bg-slate-200 rounded text-slate-500"
              >
                {copiedField === 'số tài khoản' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Nội dung chuyển khoản */}
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Nội dung CK:</span>
            <div className="flex items-center gap-1.5">
              <span className="font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                {invoice.payment_ref || `SAMS P${invoice.room_id} T${invoice.month}`}
              </span>
              <button
                onClick={() => handleCopy(invoice.payment_ref || `SAMS P${invoice.room_id} T${invoice.month}`, 'nội dung chuyển khoản')}
                className="p-1 hover:bg-slate-200 rounded text-slate-500"
              >
                {copiedField === 'nội dung chuyển khoản' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-5 grid grid-cols-2 gap-3">
          <a
            href={qrImageUrl}
            target="_blank"
            rel="noopener noreferrer"
            download={`VietQR_Invoice_${invoice.id}.png`}
            className="btn btn-secondary text-xs flex items-center justify-center gap-1.5 py-2.5 rounded-xl"
          >
            <Download className="w-4 h-4 text-slate-500" />
            Tải mã QR
          </a>

          <button
            onClick={() => {
              onClose()
              if (onOpenPaymentSlip) onOpenPaymentSlip(invoice)
            }}
            className="btn btn-primary text-xs flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
          >
            <Upload className="w-4 h-4" />
            Tải biên lai CK
          </button>
        </div>
      </div>
    </div>
  )
}
