import { useState, useRef, useEffect } from 'react'
import {
  MessageSquare,
  X,
  Send,
  Sparkles,
  QrCode,
  ExternalLink,
  Bot,
  User,
  Wrench,
  BookOpen,
} from 'lucide-react'
import toast from 'react-hot-toast'
import chatService from '@/services/chatService'

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'model',
      text: 'Chào bạn! Mình là Trợ lý AI của tòa nhà SAMS. Bạn có thể hỏi mình về tiền phòng, hóa đơn tháng này, quy định nội quy tòa nhà hoặc báo hỏng hóc nhé!',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    if (isOpen) {
      scrollToBottom()
    }
  }, [messages, isOpen])

  const handleSend = async (textToSend) => {
    const query = (textToSend || inputMessage).trim()
    if (!query || loading) return

    const userMsg = {
      id: Date.now(),
      role: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    setMessages((prev) => [...prev, userMsg])
    setInputMessage('')
    setLoading(true)

    try {
      const data = await chatService.sendMessage(query)
      const botMsg = {
        id: Date.now() + 1,
        role: 'model',
        text: data.reply,
        attachedAction: data.attached_action,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, botMsg])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'model',
          text: 'Xin lỗi bạn, kết nối tới Trợ lý AI đang gặp gián đoạn. Bạn thử lại sau giây lát nhé!',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const quickPrompts = [
    { text: 'Hóa đơn tháng này của tôi?', icon: QrCode },
    { text: 'Nội quy giờ giấc tòa nhà?', icon: BookOpen },
    { text: 'Báo hỏng vòi nước/thiết bị', icon: Wrench },
  ]

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 group flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-indigo-600 to-primary-600 text-white shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-200"
        >
          <div className="relative">
            <Sparkles className="w-5 h-5 animate-spin-slow" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-indigo-600" />
          </div>
          <span className="text-sm font-semibold tracking-wide">Trợ lý AI 24/7</span>
        </button>
      )}

      {/* Slide-over / Modal Chat Window */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-[95vw] sm:w-[400px] h-[580px] bg-white rounded-3xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-indigo-700 via-indigo-600 to-primary-600 text-white flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="text-sm font-bold leading-tight">Trợ lý ảo Căn hộ SAMS</h4>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-[11px] text-indigo-100 font-medium">Gemini 1.5 Flash Online</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Prompts Bar */}
          <div className="p-2 bg-slate-50 border-b border-slate-100 flex items-center gap-1.5 overflow-x-auto scrollbar-none">
            {quickPrompts.map((q, idx) => {
              const Icon = q.icon
              return (
                <button
                  key={idx}
                  onClick={() => handleSend(q.text)}
                  className="flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium bg-white text-slate-700 border border-slate-200 rounded-full hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 transition-all shrink-0"
                >
                  <Icon className="w-3 h-3 text-indigo-600" />
                  {q.text}
                </button>
              )
            })}
          </div>

          {/* Message List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-gradient-to-b from-slate-50/50 to-white">
            {messages.map((m) => {
              const isModel = m.role === 'model'
              return (
                <div
                  key={m.id}
                  className={`flex gap-2.5 ${isModel ? 'items-start' : 'items-end justify-end'}`}
                >
                  {isModel && (
                    <div className="w-7 h-7 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-700 shrink-0 mt-0.5">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className={`max-w-[82%] space-y-2`}>
                    <div
                      className={`p-3 rounded-2xl text-xs leading-relaxed ${
                        isModel
                          ? 'bg-white border border-slate-200/80 text-slate-800 shadow-xs'
                          : 'bg-gradient-to-r from-indigo-600 to-primary-600 text-white shadow-xs rounded-br-xs'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{m.text}</div>
                    </div>

                    {/* Rich Action Card: VIETQR_PAYMENT_CARD */}
                    {m.attachedAction?.type === 'VIETQR_PAYMENT_CARD' && (
                      <div className="p-3 bg-indigo-50/70 border border-indigo-200 rounded-2xl shadow-xs">
                        <div className="flex items-center gap-2 mb-2">
                          <QrCode className="w-4 h-4 text-indigo-600" />
                          <span className="text-xs font-bold text-indigo-900">
                            Thanh toán VietQR 1-chạm
                          </span>
                        </div>
                        {m.attachedAction.vietqr_url && (
                          <div className="flex justify-center bg-white p-2 rounded-xl border border-indigo-100 mb-2">
                            <img
                              src={m.attachedAction.vietqr_url}
                              alt="VietQR"
                              className="w-36 h-36 object-contain"
                            />
                          </div>
                        )}
                        <div className="text-[11px] text-slate-600 space-y-0.5 mb-2">
                          <div>
                            Số tiền:{' '}
                            <strong className="text-indigo-700 font-bold">
                              {new Intl.NumberFormat('vi-VN', {
                                style: 'currency',
                                currency: 'VND',
                              }).format(m.attachedAction.amount || 0)}
                            </strong>
                          </div>
                          <div>
                            Nội dung: <span className="font-mono text-slate-800">{m.attachedAction.payment_ref}</span>
                          </div>
                        </div>
                        <a
                          href="/invoices"
                          className="btn btn-primary w-full text-[11px] py-1.5 rounded-lg flex items-center justify-center gap-1"
                        >
                          Xem chi tiết hóa đơn
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    )}

                    <div className={`text-[10px] text-slate-400 ${isModel ? 'text-left' : 'text-right'}`}>
                      {m.timestamp}
                    </div>
                  </div>

                  {!isModel && (
                    <div className="w-7 h-7 rounded-xl bg-slate-200 flex items-center justify-center text-slate-600 shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              )
            })}

            {loading && (
              <div className="flex items-center gap-2 text-slate-400 text-xs py-1">
                <div className="w-6 h-6 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" />
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Footer Input */}
          <div className="p-3 bg-white border-t border-slate-200">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                handleSend()
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                placeholder="Nhập câu hỏi cho trợ lý AI..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                className="flex-1 text-xs px-3.5 py-2.5 bg-slate-100/80 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="submit"
                disabled={loading || !inputMessage.trim()}
                className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-50 transition-colors shadow-xs"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
