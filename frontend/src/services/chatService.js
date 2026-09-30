import apiClient from '@/lib/apiClient'

export const chatService = {
  sendMessage: async (message, roomId = null) => {
    const res = await apiClient.post('/chat/message', {
      message,
      room_id: roomId,
    })
    return res.data.data
  },
}

export default chatService
