import apiClient from '@/lib/apiClient'

export const contractService = {
  getContracts: async (params = {}) => {
    const res = await apiClient.get('/contracts', { params })
    return res.data.data
  },

  getContractDetail: async (contractId) => {
    const res = await apiClient.get(`/contracts/${contractId}`)
    return res.data.data
  },

  createContract: async (data) => {
    const res = await apiClient.post('/contracts', data)
    return res.data.data
  },

  previewRefund: async (contractId, params = {}) => {
    const res = await apiClient.get(`/contracts/${contractId}/refund-preview`, { params })
    return res.data.data
  },

  settleRefund: async (contractId, data) => {
    const res = await apiClient.post(`/contracts/${contractId}/settle-refund`, data)
    return res.data.data
  },
}

export default contractService
