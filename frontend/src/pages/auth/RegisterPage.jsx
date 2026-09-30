// SAMS - Register Page with Email OTP Verification
import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { ShieldCheck, Mail, ArrowLeft, RefreshCw, CheckCircle2, KeyRound, User, Phone, Lock, Hash } from 'lucide-react'
import toast from 'react-hot-toast'
import authService from '@/services/authService'
import useAuthStore from '@/stores/authStore'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()

  // Steps: 1 = Fill info, 2 = Verify OTP
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [countdown, setCountdown] = useState(60)
  const [canResend, setCanResend] = useState(false)
  const [formData, setFormData] = useState(null)
  const [otpCode, setOtpCode] = useState('')

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: {
      full_name: '',
      username: '',
      email: '',
      phone: '',
      cccd_number: '',
      password: '',
      confirm_password: '',
    },
  })

  const passwordVal = watch('password')

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

  // Bước 1: Gửi OTP đến email
  const onProceedToOtp = async (data) => {
    setLoading(true)
    try {
      await authService.sendRegisterOtp(data.email)
      setFormData(data)
      setStep(2)
      setCountdown(60)
      setCanResend(false)
      toast.success(`Mã xác thực OTP đã được gửi đến ${data.email}!`)
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Không thể gửi mã xác thực. Vui lòng thử lại.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  // Gửi lại mã OTP
  const handleResendOtp = async () => {
    if (!canResend || !formData?.email) return
    setLoading(true)
    try {
      await authService.sendRegisterOtp(formData.email)
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

  // Bước 2: Hoàn tất đăng ký với mã OTP
  const onCompleteRegistration = async (e) => {
    e.preventDefault()
    if (!otpCode || otpCode.trim().length !== 6) {
      toast.error('Vui lòng nhập đúng 6 chữ số mã OTP!')
      return
    }

    setLoading(true)
    try {
      const payload = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        phone: formData.phone || null,
        cccd_number: formData.cccd_number || null,
        otp_code: otpCode.trim(),
      }

      await authService.register(payload)
      toast.success('Đăng ký tài khoản thành công! Đang tự động đăng nhập...')

      // Tự động đăng nhập
      try {
        await login(formData.username, formData.password)
        navigate('/dashboard', { replace: true })
      } catch {
        navigate('/login')
      }
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Xác thực OTP thất bại. Vui lòng kiểm tra lại.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-900 via-slate-900 to-slate-950 p-4">
      <div className="w-full max-w-lg">
        {/* Branding Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center gap-2 text-2xl font-black text-white tracking-tight">
            <span className="w-10 h-10 rounded-2xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <ShieldCheck className="w-6 h-6 text-white" />
            </span>
            SAMS
          </Link>
          <p className="text-slate-400 mt-1 text-xs">Cổng Dịch Vụ Cư Dân & Quản Lý Căn Hộ</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-6 sm:p-8 border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
          {/* Header & Step Indicator */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                {step === 1 ? 'Đăng ký tài khoản' : 'Xác thực mã OTP'}
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                {step === 1 ? 'Bước 1: Điền thông tin cá nhân' : `Bước 2: Nhập mã OTP đã gửi qua email`}
              </p>
            </div>
            <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl text-xs font-bold text-slate-600">
              <span className={`px-2.5 py-1 rounded-lg transition-colors ${step === 1 ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400'}`}>
                1
              </span>
              <span className={`px-2.5 py-1 rounded-lg transition-colors ${step === 2 ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400'}`}>
                2
              </span>
            </div>
          </div>

          {/* STEP 1: Registration Form */}
          {step === 1 && (
            <form onSubmit={handleSubmit(onProceedToOtp)} className="space-y-4">
              {/* Họ tên */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Họ và tên cư dân *</label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    className={`input pl-9 ${errors.full_name ? 'input-error' : ''}`}
                    placeholder="Nguyễn Văn A..."
                    {...register('full_name', { required: 'Vui lòng nhập họ và tên' })}
                  />
                </div>
                {errors.full_name && <p className="text-xs text-rose-500 mt-1">{errors.full_name.message}</p>}
              </div>

              {/* Username & Email */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Tên đăng nhập *</label>
                  <div className="relative">
                    <Hash className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      className={`input pl-9 ${errors.username ? 'input-error' : ''}`}
                      placeholder="vd: nguyenvana"
                      {...register('username', {
                        required: 'Vui lòng nhập tên đăng nhập',
                        pattern: {
                          value: /^[a-zA-Z0-9_]+$/,
                          message: 'Chỉ gồm chữ cái, số và dấu gạch dưới',
                        },
                      })}
                    />
                  </div>
                  {errors.username && <p className="text-xs text-rose-500 mt-1">{errors.username.message}</p>}
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Email nhận mã OTP *</label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="email"
                      className={`input pl-9 ${errors.email ? 'input-error' : ''}`}
                      placeholder="name@gmail.com"
                      {...register('email', {
                        required: 'Vui lòng nhập địa chỉ email',
                        pattern: {
                          value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                          message: 'Email không hợp lệ',
                        },
                      })}
                    />
                  </div>
                  {errors.email && <p className="text-xs text-rose-500 mt-1">{errors.email.message}</p>}
                </div>
              </div>

              {/* Phone & CCCD */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Số điện thoại</label>
                  <div className="relative">
                    <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      className="input pl-9"
                      placeholder="0901234567"
                      {...register('phone')}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Số CCCD (12 số)</label>
                  <div className="relative">
                    <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      className="input pl-9"
                      placeholder="07909500xxxx"
                      maxLength={12}
                      {...register('cccd_number')}
                    />
                  </div>
                </div>
              </div>

              {/* Password & Confirm */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Mật khẩu (tối thiểu 8 ký tự) *</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="password"
                      className={`input pl-9 ${errors.password ? 'input-error' : ''}`}
                      placeholder="••••••••"
                      {...register('password', {
                        required: 'Vui lòng nhập mật khẩu',
                        minLength: { value: 8, message: 'Tối thiểu 8 ký tự' },
                      })}
                    />
                  </div>
                  {errors.password && <p className="text-xs text-rose-500 mt-1">{errors.password.message}</p>}
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Xác nhận mật khẩu *</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="password"
                      className={`input pl-9 ${errors.confirm_password ? 'input-error' : ''}`}
                      placeholder="••••••••"
                      {...register('confirm_password', {
                        required: 'Vui lòng xác nhận mật khẩu',
                        validate: (val) => val === passwordVal || 'Mật khẩu xác nhận không khớp',
                      })}
                    />
                  </div>
                  {errors.confirm_password && <p className="text-xs text-rose-500 mt-1">{errors.confirm_password.message}</p>}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full py-2.5 mt-2 flex items-center justify-center gap-2"
              >
                {loading ? <span className="spinner" /> : <Mail className="w-4 h-4" />}
                {loading ? 'Đang gửi mã OTP...' : 'Tiếp tục & Nhận mã OTP qua Email'}
              </button>
            </form>
          )}

          {/* STEP 2: Verify OTP Form */}
          {step === 2 && (
            <form onSubmit={onCompleteRegistration} className="space-y-5">
              <div className="p-3.5 bg-indigo-50 border border-indigo-100 rounded-2xl flex items-start gap-3">
                <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0">
                  <Mail className="w-4 h-4" />
                </div>
                <div className="text-xs">
                  <p className="font-semibold text-indigo-950">Mã xác thực đã được gửi tới:</p>
                  <p className="text-indigo-600 font-bold mt-0.5 break-all">{formData?.email}</p>
                  <p className="text-slate-500 mt-1 text-[11px]">
                    Vui lòng kiểm tra hộp thư đến (Inbox) hoặc thư rác (Spam).
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-2 text-center">
                  Nhập mã số xác thực gồm 6 chữ số:
                </label>
                <div className="flex justify-center">
                  <input
                    type="text"
                    maxLength={6}
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                    placeholder="000000"
                    autoFocus
                    className="w-56 text-center text-3xl font-black font-mono tracking-[0.5em] py-3 border-2 border-indigo-300 rounded-2xl focus:border-indigo-600 focus:ring-4 focus:ring-indigo-100 outline-none text-indigo-900 bg-indigo-50/20"
                  />
                </div>
              </div>

              {/* Countdown & Resend */}
              <div className="flex items-center justify-center gap-2 text-xs">
                {canResend ? (
                  <button
                    type="button"
                    onClick={handleResendOtp}
                    disabled={loading}
                    className="text-indigo-600 font-bold hover:underline flex items-center gap-1.5"
                  >
                    <RefreshCw className="w-3.5 h-3.5" /> Gửi lại mã OTP
                  </button>
                ) : (
                  <span className="text-slate-500">
                    Gửi lại mã sau <span className="font-mono font-bold text-indigo-600">{countdown}s</span>
                  </span>
                )}
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-2">
                <button
                  type="submit"
                  disabled={loading || otpCode.length !== 6}
                  className="btn-primary w-full py-2.5 flex items-center justify-center gap-2"
                >
                  {loading ? <span className="spinner" /> : <CheckCircle2 className="w-4 h-4" />}
                  {loading ? 'Đang xác thực...' : 'Xác nhận & Hoàn tất Đăng ký'}
                </button>

                <button
                  type="button"
                  onClick={() => setStep(1)}
                  disabled={loading}
                  className="btn-secondary w-full py-2 flex items-center justify-center gap-1.5 text-xs"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Sửa lại thông tin cá nhân
                </button>
              </div>
            </form>
          )}

          {/* Links */}
          <div className="text-center pt-4 border-t border-slate-100 mt-6">
            <p className="text-xs text-slate-500">
              Đã có tài khoản?{' '}
              <Link to="/login" className="text-indigo-600 font-bold hover:underline">
                Đăng nhập ngay
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
