import apiClient from '@/lib/apiClient'

export const authService = {
  // Gửi mã OTP đăng ký tài khoản
  sendRegisterOtp: async (email) => {
    const res = await apiClient.post('/auth/register/send-otp', { email })
    return res.data
  },

  // Đăng ký tài khoản kèm mã OTP
  register: async (payload) => {
    const res = await apiClient.post('/auth/register', payload)
    return res.data.data
  },

  // Gửi mã OTP quên mật khẩu
  forgotPassword: async (email) => {
    const res = await apiClient.post('/auth/forgot-password', { email })
    return res.data
  },

  // Đặt lại mật khẩu với OTP
  resetPassword: async ({ email, otp_code, new_password }) => {
    const res = await apiClient.post('/auth/reset-password', {
      email,
      otp_code,
      new_password,
    })
    return res.data
  },
}

export default authService
