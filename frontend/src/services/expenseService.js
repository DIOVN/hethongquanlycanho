import apiClient from '@/lib/apiClient'

export const expenseService = {
  getExpenses: async (params = {}) => {
    const res = await apiClient.get('/expenses', { params })
    return res.data.data
  },

  createExpense: async (data) => {
    let res
    if (data instanceof FormData) {
      res = await apiClient.post('/expenses', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    } else {
      res = await apiClient.post('/expenses', data)
    }
    return res.data.data
  },

  getFinancialSummary: async (params = {}) => {
    const res = await apiClient.get('/expenses/summary', { params })
    return res.data.data
  },
}

export default expenseService
