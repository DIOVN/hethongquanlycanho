// SAMS - Forgot Password Page with Email OTP Verification
import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { KeyRound, Mail, ArrowLeft, RefreshCw, CheckCircle2, Lock, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'
import authService from '@/services/authService'

export default function ForgotPasswordPage() {
  const navigate = useNavigate()

  // Steps: 1 = Enter Email, 2 = Enter OTP & New Password, 3 = Success
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [targetEmail, setTargetEmail] = useState('')
  const [countdown, setCountdown] = useState(60)
  const [canResend, setCanResend] = useState(false)

  const {
    register: regEmail,
    handleSubmit: handleEmailSubmit,
    formState: { errors: errorsEmail },
  } = useForm({ defaultValues: { email: '' } })

  const {
    register: regReset,
    handleSubmit: handleResetSubmit,
    watch: watchReset,
    formState: { errors: errorsReset },
  } = useForm({
    defaultValues: {
      otp_code: '',
      new_password: '',
      confirm_password: '',
    },
  })

  const newPass = watchReset('new_password')

  // Timer countdown cho nút gửi lại OTP
  useEffect(() => {
    let timer
    if (step === 2 && countdown > 0) {
      timer = setInterval(() => {
        setCountdown((prev) => prev - 1)
      }, 1000)
    } else if (countdown === 0) {
      setCanResend(true)
    }
    return () => clearInterval(timer)
  }, [step, countdown])

  // Bước 1: Gửi OTP quên mật khẩu
  const onSendOtp = async (data) => {
    setLoading(true)
    try {
      await authService.forgotPassword(data.email)
      setTargetEmail(data.email)
      setStep(2)
      setCountdown(60)
      setCanResend(false)
      toast.success(`Mã OTP đặt lại mật khẩu đã được gửi đến ${data.email}!`)
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Không tìm thấy tài khoản hoặc không thể gửi mã.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  // Gửi lại mã OTP
  const handleResendOtp = async () => {
    if (!canResend || !targetEmail) return
    setLoading(true)
    try {
      await authService.forgotPassword(targetEmail)
      setCountdown(60)
      setCanResend(false)
      toast.success('Đã gửi lại mã OTP mới!')
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Gửi lại mã OTP thất bại.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  // Bước 2: Xác minh OTP và đổi mật khẩu
  const onResetPassword = async (data) => {
    setLoading(true)
    try {
      await authService.resetPassword({
        email: targetEmail,
        otp_code: data.otp_code.trim(),
        new_password: data.new_password,
      })
      toast.success('Đặt lại mật khẩu thành công!')
      setStep(3)
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Đặt lại mật khẩu thất bại. Kiểm tra lại mã OTP.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-900 via-slate-900 to-slate-950 p-4">
      <div className="w-full max-w-md">
        {/* Branding Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center gap-2 text-2xl font-black text-white tracking-tight">
            <span className="w-10 h-10 rounded-2xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <ShieldCheck className="w-6 h-6 text-white" />
            </span>
            SAMS
          </Link>
          <p className="text-slate-400 mt-1 text-xs">Cổng Khôi Phục Tài Khoản Cư Dân</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-6 sm:p-8 border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
          {/* STEP 1: Enter Email */}
          {step === 1 && (
            <div>
              <div className="text-center mb-6">
                <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <KeyRound className="w-6 h-6" />
                </div>
                <h2 className="text-xl font-bold text-slate-800">Quên mật khẩu?</h2>
                <p className="text-xs text-slate-500 mt-1">
                  Nhập địa chỉ email đăng ký để nhận mã xác thực OTP khôi phục mật khẩu.
                </p>
              </div>

              <form onSubmit={handleEmailSubmit(onSendOtp)} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Email đăng ký của bạn</label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="email"
                      className={`input pl-9 ${errorsEmail.email ? 'input-error' : ''}`}
                      placeholder="name@gmail.com"
                      autoFocus
                      {...regEmail('email', {
                        required: 'Vui lòng nhập địa chỉ email',
                        pattern: {
                          value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                          message: 'Email không đúng định dạng',
                        },
                      })}
                    />
                  </div>
                  {errorsEmail.email && <p className="text-xs text-rose-500 mt-1">{errorsEmail.email.message}</p>}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full py-2.5 flex items-center justify-center gap-2"
                >
                  {loading ? <span className="spinner" /> : <Mail className="w-4 h-4" />}
                  {loading ? 'Đang gửi mã...' : 'Gửi mã xác thực OTP'}
                </button>
              </form>
            </div>
          )}

          {/* STEP 2: Enter OTP & New Password */}
          {step === 2 && (
            <div>
              <div className="mb-5 pb-3 border-b border-slate-100">
                <h2 className="text-lg font-bold text-slate-800">Nhập mã OTP & Mật khẩu mới</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Đã gửi mã xác nhận 6 số đến: <span className="font-semibold text-indigo-600">{targetEmail}</span>
                </p>
              </div>

              <form onSubmit={handleResetSubmit(onResetPassword)} className="space-y-4">
                {/* OTP Input */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1 text-center">
                    Mã xác thực OTP (6 chữ số) *
                  </label>
                  <div className="flex justify-center mb-2">
                    <input
                      type="text"
                      maxLength={6}
                      placeholder="000000"
                      autoFocus
                      className="w-48 text-center text-2xl font-black font-mono tracking-[0.4em] py-2.5 border-2 border-indigo-300 rounded-xl focus:border-indigo-600 focus:ring-4 focus:ring-indigo-100 outline-none text-indigo-900 bg-indigo-50/20"
                      {...regReset('otp_code', {
                        required: 'Vui lòng nhập mã OTP',
                        minLength: { value: 6, message: 'OTP gồm 6 chữ số' },
                      })}
                    />
                  </div>
                  {errorsReset.otp_code && (
                    <p className="text-xs text-rose-500 text-center">{errorsReset.otp_code.message}</p>
                  )}

                  {/* Resend Countdown */}
                  <div className="flex items-center justify-center gap-2 text-xs mt-1">
                    {canResend ? (
                      <button
                        type="button"
                        onClick={handleResendOtp}
                        disabled={loading}
                        className="text-indigo-600 font-bold hover:underline flex items-center gap-1"
                      >
                        <RefreshCw className="w-3 h-3" /> Gửi lại mã
                      </button>
                    ) : (
                      <span className="text-slate-400">
                        Gửi lại mã sau <span className="font-mono font-bold text-indigo-600">{countdown}s</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* New Password */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Mật khẩu mới (tối thiểu 8 ký tự) *</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="password"
                      className={`input pl-9 ${errorsReset.new_password ? 'input-error' : ''}`}
                      placeholder="••••••••"
                      {...regReset('new_password', {
                        required: 'Vui lòng nhập mật khẩu mới',
                        minLength: { value: 8, message: 'Tối thiểu 8 ký tự' },
                      })}
                    />
                  </div>
                  {errorsReset.new_password && (
                    <p className="text-xs text-rose-500 mt-1">{errorsReset.new_password.message}</p>
                  )}
                </div>

                {/* Confirm Password */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Xác nhận mật khẩu mới *</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="password"
                      className={`input pl-9 ${errorsReset.confirm_password ? 'input-error' : ''}`}
                      placeholder="••••••••"
                      {...regReset('confirm_password', {
                        required: 'Vui lòng xác nhận mật khẩu',
                        validate: (val) => val === newPass || 'Mật khẩu xác nhận không khớp',
                      })}
                    />
                  </div>
                  {errorsReset.confirm_password && (
                    <p className="text-xs text-rose-500 mt-1">{errorsReset.confirm_password.message}</p>
                  )}
                </div>

                {/* Actions */}
                <div className="pt-2 space-y-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary w-full py-2.5 flex items-center justify-center gap-2"
                  >
                    {loading ? <span className="spinner" /> : <CheckCircle2 className="w-4 h-4" />}
                    {loading ? 'Đang cập nhật...' : 'Xác nhận Đặt lại Mật khẩu'}
                  </button>

                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    disabled={loading}
                    className="btn-secondary w-full py-2 flex items-center justify-center gap-1.5 text-xs"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" /> Dùng email khác
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* STEP 3: Success Screen */}
          {step === 3 && (
            <div className="text-center py-4 space-y-4">
              <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-3xl flex items-center justify-center mx-auto border border-emerald-100 shadow-sm animate-in zoom-in-75 duration-300">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-800">Đặt lại mật khẩu thành công!</h3>
                <p className="text-xs text-slate-500 mt-1">
                  Mật khẩu tài khoản của bạn đã được cập nhật an toàn. Bây giờ bạn có thể đăng nhập bằng mật khẩu mới.
                </p>
              </div>
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="btn-primary w-full py-2.5"
              >
                Đăng nhập ngay
              </button>
            </div>
          )}

          {/* Footer Back Link */}
          {step !== 3 && (
            <div className="text-center pt-4 border-t border-slate-100 mt-6">
              <Link to="/login" className="text-xs text-slate-500 hover:text-indigo-600 font-semibold inline-flex items-center gap-1">
                <ArrowLeft className="w-3.5 h-3.5" /> Quay lại trang Đăng nhập
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
