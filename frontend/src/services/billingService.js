import apiClient from '@/lib/apiClient'

export const billingService = {
  // Lấy danh sách hóa đơn của khách thuê đăng nhập
  getMyInvoices: async () => {
    const res = await apiClient.get('/billing/my-invoices')
    return res.data.data
  },

  // Chủ nhà lấy danh sách tất cả hóa đơn theo bộ lọc
  getInvoices: async (params = {}) => {
    const res = await apiClient.get('/billing/invoices', { params })
    return res.data.data
  },

  // Chi tiết 1 hóa đơn
  getInvoiceDetail: async (id) => {
    const res = await apiClient.get(`/billing/invoices/${id}`)
    return res.data.data
  },

  // Khách tải ảnh chụp biên lai chuyển khoản
  uploadPaymentSlip: async (id, file) => {
    const formData = new FormData()
    formData.append('slip_image', file)
    const res = await apiClient.post(`/billing/${id}/payment-slip`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data.data
  },

  // Chủ nhà xác nhận thanh toán
  confirmPayment: async (id) => {
    const res = await apiClient.post(`/billing/invoices/${id}/confirm-payment`)
    return res.data.data
  },

  // Tạo hóa đơn nhanh tại chỗ (kèm ảnh công tơ)
  createQuickInvoice: async (formData) => {
    const res = await apiClient.post('/quick-invoices', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data.data
  },

  // Quét ảnh công tơ điện nước qua AI OCR
  scanMeterReading: async ({ imageFile, meterType, roomId }) => {
    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('meter_type', meterType)
    formData.append('room_id', roomId)
    const res = await apiClient.post('/meters/scan-reading', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data.data
  },

  // Khách/Chủ nhà chốt số đo vào CSDL
  confirmMeterReading: async (data) => {
    const res = await apiClient.post('/meters/confirm-reading', data)
    return res.data.data
  },
}

export default billingService
