import apiClient from '@/lib/apiClient'

export const ticketService = {
  getTickets: async (params = {}) => {
    const res = await apiClient.get('/tickets', { params })
    return res.data.data
  },

  createTicket: async (data) => {
    let res
    if (data instanceof FormData) {
      res = await apiClient.post('/tickets', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    } else {
      res = await apiClient.post('/tickets', data)
    }
    return res.data.data
  },

  updateTicketStatus: async (ticketId, data) => {
    const res = await apiClient.put(`/tickets/${ticketId}/status`, data)
    return res.data.data
  },
}

export default ticketService
