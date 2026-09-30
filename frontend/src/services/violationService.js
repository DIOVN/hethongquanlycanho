import apiClient from '@/lib/apiClient'

export const violationService = {
  getViolations: async (params = {}) => {
    const res = await apiClient.get('/violations', { params })
    return res.data.data
  },

  getViolationDetail: async (id) => {
    const res = await apiClient.get(`/violations/${id}`)
    return res.data.data
  },

  createViolation: async (data) => {
    let res
    if (data instanceof FormData) {
      res = await apiClient.post('/violations', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    } else {
      res = await apiClient.post('/violations', data)
    }
    return res.data.data
  },

  acknowledgeViolation: async (id) => {
    const res = await apiClient.put(`/violations/${id}/acknowledge`)
    return res.data.data
  },

  resolveViolation: async (id) => {
    const res = await apiClient.put(`/violations/${id}/resolve`)
    return res.data.data
  },
}

export default violationService
