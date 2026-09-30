import apiClient from '@/lib/apiClient'

export const roomService = {
  getRooms: async (params = {}) => {
    const res = await apiClient.get('/rooms', { params })
    return res.data.data
  },

  getRoomDetail: async (id) => {
    const res = await apiClient.get(`/rooms/${id}`)
    return res.data.data
  },

  searchRooms: async (params = {}) => {
    const res = await apiClient.get('/rooms/search', { params })
    return res.data.data
  },

  getMyRoom: async () => {
    const res = await apiClient.get('/rooms/my-room')
    return res.data.data
  },

  getRoommates: async (roomId) => {
    const res = await apiClient.get(`/rooms/${roomId}/roommates`)
    return res.data.data
  },

  addRoommate: async (roomId, data) => {
    const res = await apiClient.post(`/rooms/${roomId}/roommates`, data)
    return res.data.data
  },

  updateRoommateStatus: async (roommateId, status) => {
    const res = await apiClient.patch(`/roommates/${roommateId}/status`, { status })
    return res.data.data
  },

  getBuildings: async () => {
    const res = await apiClient.get('/rooms/buildings')
    return res.data.data
  },

  createRoom: async (data) => {
    const res = await apiClient.post('/rooms', data)
    return res.data.data
  },

  updateRoom: async (id, data) => {
    const res = await apiClient.put(`/rooms/${id}`, data)
    return res.data.data
  },

  updateRoomStatus: async (id, status) => {
    const res = await apiClient.patch(`/rooms/${id}/status`, { status })
    return res.data.data
  },
}

export default roomService
