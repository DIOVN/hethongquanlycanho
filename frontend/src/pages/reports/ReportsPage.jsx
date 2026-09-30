import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  TrendingUp,
  DollarSign,
  PieChart as PieIcon,
  BarChart3,
  Plus,
  Receipt,
  FileCheck2,
  Calendar,
  Building2,
  AlertCircle,
  FileImage,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  XCircle,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
  PieChart,
  Pie,
} from 'recharts'
import toast from 'react-hot-toast'
import AppLayout from '@/components/layout/AppLayout'
import expenseService from '@/services/expenseService'
import contractService from '@/services/contractService'
import roomService from '@/services/roomService'
import MoveOutRefundModal from '@/components/contracts/MoveOutRefundModal'

export default function ReportsPage() {
  const queryClient = useQueryClient()
  const today = new Date()

  const [selectedMonth, setSelectedMonth] = useState(today.getMonth() + 1)
  const [selectedYear, setSelectedYear] = useState(today.getFullYear())
  const [selectedBuildingId, setSelectedBuildingId] = useState('')

  const [createExpenseOpen, setCreateExpenseOpen] = useState(false)
  const [settleModalContract, setSettleModalContract] = useState(null)

  // Expense form states
  const [expTitle, setExpTitle] = useState('')
  const [expCategory, setExpCategory] = useState('common_electricity')
  const [expAmount, setExpAmount] = useState('')
  const [expDate, setExpDate] = useState(today.toISOString().split('T')[0])
  const [expReceipt, setExpReceipt] = useState(null)
  const [submittingExp, setSubmittingExp] = useState(false)

  // Fetch Financial Summary
  const { data: summary, isLoading: loadingSummary, refetch: refetchSummary } = useQuery({
    queryKey: ['financialSummary', selectedMonth, selectedYear, selectedBuildingId],
    queryFn: () =>
      expenseService.getFinancialSummary({
        month: selectedMonth,
        year: selectedYear,
        building_id: selectedBuildingId || undefined,
      }),
  })

  // Fetch Expenses list
  const { data: expenses = [], isLoading: loadingExpenses, refetch: refetchExpenses } = useQuery({
    queryKey: ['expenses', selectedMonth, selectedYear, selectedBuildingId],
    queryFn: () =>
      expenseService.getExpenses({
        month: selectedMonth,
        year: selectedYear,
        building_id: selectedBuildingId || undefined,
      }),
  })

  // Fetch Active Contracts
  const { data: contracts = [], isLoading: loadingContracts, refetch: refetchContracts } = useQuery({
    queryKey: ['contracts'],
    queryFn: () => contractService.getContracts(),
  })

  // Fetch Buildings
  const { data: rooms = [] } = useQuery({
    queryKey: ['rooms'],
    queryFn: () => roomService.getRooms(),
  })

  const handleCreateExpense = async (e) => {
    e.preventDefault()
    if (!expTitle.trim() || !expAmount) {
      toast.error('Vui lòng nhập tên chi phí và số tiền')
      return
    }

    setSubmittingExp(true)
    try {
      const formData = new FormData()
      formData.append('building_id', selectedBuildingId || '1')
      formData.append('expense_category', expCategory)
      formData.append('title', expTitle.trim())
      formData.append('amount', expAmount)
      formData.append('expense_date', expDate)
      if (expReceipt) formData.append('receipt_image', expReceipt)

      await expenseService.createExpense(formData)
      toast.success('Đã ghi nhận chi phí vận hành OpEx thành công!')
      setCreateExpenseOpen(false)
      setExpTitle('')
      setExpAmount('')
      setExpReceipt(null)
      refetchSummary()
      refetchExpenses()
    } catch (err) {
      toast.error(err?.response?.data?.message || 'Lỗi ghi nhận chi phí')
    } finally {
      setSubmittingExp(false)
    }
  }

  // Format Recharts data
  const comparisonData = [
    {
      name: `Tháng ${selectedMonth}/${selectedYear}`,
      'Doanh thu thực thu': summary?.total_revenue || 0,
      'Chi phí OpEx': summary?.total_opex || 0,
      'Lợi nhuận ròng': summary?.net_profit || 0,
    },
  ]

  const categoryNameMap = {
    common_electricity: 'Điện chung & Bơm',
    water: 'Nước chung',
    internet: 'Cáp quang & WiFi',
    cleaning: 'Vệ sinh & Rác',
    security: 'Bảo vệ & Camera',
    maintenance: 'Sửa chữa & Bảo dưỡng',
    other: 'Khác',
  }

  const pieColors = ['#6366f1', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6']

  const categoryPieData = Object.entries(summary?.category_breakdown || {}).map(([key, val], idx) => ({
    name: categoryNameMap[key] || key,
    value: val,
    color: pieColors[idx % pieColors.length],
  }))

  const categoryBadge = (cat) => {
    return (
      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
        {categoryNameMap[cat] || cat}
      </span>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header Bar */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <TrendingUp className="w-7 h-7 text-indigo-600" />
              Báo Cáo Tài Chính & Lợi Nhuận Ròng (Net Profit)
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Phân tích doanh thu thực tế, kiểm soát chi phí vận hành (OpEx) và nghiệm thu quyết toán cọc trả phòng.
            </p>
          </div>

          {/* Month / Year Filter Controls */}
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
              className="px-3 py-2 text-xs font-semibold border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[44px]"
            >
              {[...Array(12)].map((_, i) => (
                <option key={i + 1} value={i + 1}>
                  Tháng {i + 1}
                </option>
              ))}
            </select>

            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              className="px-3 py-2 text-xs font-semibold border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[44px]"
            >
              {[2024, 2025, 2026, 2027].map((y) => (
                <option key={y} value={y}>
                  Năm {y}
                </option>
              ))}
            </select>

            <button
              onClick={() => setCreateExpenseOpen(true)}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 rounded-xl shadow-xs min-h-[44px]"
            >
              <Plus className="w-4 h-4" />
              Ghi nhận OpEx
            </button>
          </div>
        </div>

        {/* 5 Financial Summary KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Card 1: Revenue */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-xs font-semibold text-slate-500">Doanh thu thực thu</span>
            <div className="mt-2 text-2xl font-black text-slate-900">
              {Number(summary?.total_revenue || 0).toLocaleString('vi-VN')} đ
            </div>
            <p className="text-[11px] text-emerald-600 font-semibold mt-2 flex items-center gap-1">
              <ArrowUpRight className="w-3.5 h-3.5" />
              {summary?.paid_invoices_count || 0} hóa đơn đã thu
            </p>
          </div>

          {/* Card 2: OpEx */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-xs font-semibold text-slate-500">Chi phí vận hành (OpEx)</span>
            <div className="mt-2 text-2xl font-black text-rose-600">
              {Number(summary?.total_opex || 0).toLocaleString('vi-VN')} đ
            </div>
            <p className="text-[11px] text-slate-400 mt-2">
              {expenses.length} khoản chi phí
            </p>
          </div>

          {/* Card 3: Net Profit */}
          <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white p-5 rounded-2xl shadow-md border border-indigo-800/50">
            <span className="text-xs font-semibold text-indigo-200">Lợi nhuận ròng (Net Profit)</span>
            <div className="mt-2 text-2xl font-black text-emerald-400">
              {Number(summary?.net_profit || 0).toLocaleString('vi-VN')} đ
            </div>
            <p className="text-[11px] text-indigo-300 mt-2">
              Tỷ suất: <strong>{summary?.profit_margin_percent || 0}%</strong>
            </p>
          </div>

          {/* Card 4: Profit Margin */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-xs font-semibold text-slate-500">Tỷ suất lợi nhuận</span>
            <div className="mt-2 text-2xl font-black text-indigo-600">
              {summary?.profit_margin_percent || 0}%
            </div>
            <p className="text-[11px] text-slate-400 mt-2">
              Lợi nhuận / Doanh thu
            </p>
          </div>

          {/* Card 5: Pending Receivables */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-xs font-semibold text-slate-500">Khoản nợ chưa thu</span>
            <div className="mt-2 text-2xl font-black text-amber-600">
              {Number(summary?.pending_receivables || 0).toLocaleString('vi-VN')} đ
            </div>
            <p className="text-[11px] text-amber-600 font-semibold mt-2">
              {summary?.unpaid_invoices_count || 0} hóa đơn đang chờ
            </p>
          </div>
        </div>

        {/* Recharts Visualizations Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart 1: BarChart Revenue vs OpEx vs Net Profit */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-indigo-600" />
              <h3 className="text-base font-bold text-slate-900">
                So sánh Doanh thu vs Chi phí vs Lợi nhuận
              </h3>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparisonData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(val) => `${Number(val).toLocaleString('vi-VN')} đ`}
                    contentStyle={{ borderRadius: '12px', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="Doanh thu thực thu" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="Chi phí OpEx" fill="#f43f5e" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="Lợi nhuận ròng" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 2: OpEx Category Breakdown */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center gap-2 mb-4">
              <PieIcon className="w-5 h-5 text-indigo-600" />
              <h3 className="text-base font-bold text-slate-900">
                Cơ cấu Chi phí Vận hành (OpEx)
              </h3>
            </div>

            {categoryPieData.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-xs text-slate-400">
                Chưa có dữ liệu chi phí trong tháng này.
              </div>
            ) : (
              <div className="h-64 w-full flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryPieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      innerRadius={45}
                      paddingAngle={4}
                      label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    >
                      {categoryPieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(val) => `${Number(val).toLocaleString('vi-VN')} đ`}
                      contentStyle={{ borderRadius: '12px', fontSize: '12px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>

        {/* Section: OpEx Expenses Ledger Table */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Receipt className="w-5 h-5 text-indigo-600" />
              <h3 className="text-base font-bold text-slate-900">
                Sổ Nhật Ký Chi Phí Vận Hành (OpEx)
              </h3>
            </div>
            <span className="text-xs font-semibold text-slate-500">
              {expenses.length} khoản chi phí
            </span>
          </div>

          {loadingExpenses ? (
            <div className="p-8 text-center text-xs text-slate-400">Đang tải chi phí...</div>
          ) : expenses.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              Chưa có khoản chi phí nào trong kỳ này. Bấm &quot;Ghi nhận OpEx&quot; để thêm chi phí.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Ngày chi</th>
                    <th className="py-3 px-4 font-semibold">Khoản mục</th>
                    <th className="py-3 px-4 font-semibold">Tên chi phí</th>
                    <th className="py-3 px-4 font-semibold text-right">Số tiền</th>
                    <th className="py-3 px-4 font-semibold text-center">Chứng từ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {expenses.map((exp) => (
                    <tr key={exp.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-medium text-slate-600">
                        {exp.expense_date}
                      </td>
                      <td className="py-3 px-4">{categoryBadge(exp.expense_category)}</td>
                      <td className="py-3 px-4 font-bold text-slate-800">{exp.title}</td>
                      <td className="py-3 px-4 text-right font-black text-rose-600">
                        - {Number(exp.amount).toLocaleString('vi-VN')} đ
                      </td>
                      <td className="py-3 px-4 text-center">
                        {exp.receipt_image_url ? (
                          <a
                            href={exp.receipt_image_url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-semibold"
                          >
                            <FileImage className="w-3.5 h-3.5" />
                            Xem bill
                          </a>
                        ) : (
                          <span className="text-slate-300">Không có</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Section: Move-out Inspection & Deposit Refund Settlement */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileCheck2 className="w-5 h-5 text-indigo-600" />
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Nghiệm Thu Trả Phòng & Quyết Toán Hoàn Cọc
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Thực hiện chốt điện nước lẻ cuối kỳ, trừ hư hao và hoàn trả tiền cọc khi khách kết thúc hợp đồng.
                </p>
              </div>
            </div>
            <span className="text-xs font-semibold text-slate-500">
              {contracts.filter((c) => c.status === 'active').length} hợp đồng đang hiệu lực
            </span>
          </div>

          {loadingContracts ? (
            <div className="p-8 text-center text-xs text-slate-400">Đang tải danh sách hợp đồng...</div>
          ) : contracts.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              Chưa có hợp đồng nào trong hệ thống.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Phòng</th>
                    <th className="py-3 px-4 font-semibold">Khách thuê</th>
                    <th className="py-3 px-4 font-semibold">Thời hạn</th>
                    <th className="py-3 px-4 font-semibold text-right">Tiền cọc</th>
                    <th className="py-3 px-4 font-semibold text-center">Trạng thái</th>
                    <th className="py-3 px-4 font-semibold text-right">Hành động</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {contracts.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900">
                        Phòng {c.room_number || c.room_id}
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-semibold text-slate-800">{c.tenant_name || 'Khách thuê'}</span>
                        <span className="block text-[11px] text-slate-400">{c.tenant_phone || ''}</span>
                      </td>
                      <td className="py-3 px-4 text-slate-600">
                        {c.start_date} &rarr; {c.end_date}
                      </td>
                      <td className="py-3 px-4 text-right font-black text-indigo-700">
                        {Number(c.deposit_amount).toLocaleString('vi-VN')} đ
                      </td>
                      <td className="py-3 px-4 text-center">
                        {c.status === 'active' ? (
                          <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700">
                            Đang thuê
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-500">
                            Đã thanh lý
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        {c.status === 'active' ? (
                          <button
                            onClick={() => setSettleModalContract(c)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 shadow-xs min-h-[36px]"
                          >
                            <FileCheck2 className="w-3.5 h-3.5" />
                            Nghiệm thu hoàn cọc
                          </button>
                        ) : (
                          <span className="text-[11px] text-slate-400 italic">Đã chốt sổ</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal: Ghi nhận OpEx */}
        {createExpenseOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
            <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-xl border border-slate-100">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <Receipt className="w-5 h-5 text-indigo-600" />
                  Ghi nhận Chi phí Vận hành (OpEx)
                </h3>
                <button
                  onClick={() => setCreateExpenseOpen(false)}
                  className="p-1 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 min-h-[44px] min-w-[44px] flex items-center justify-center"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateExpense} className="mt-4 space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Tên khoản chi phí <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="VD: Tiền điện hành lang T10, sửa chữa bơm tầng hầm..."
                    value={expTitle}
                    onChange={(e) => setExpTitle(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Hạng mục</label>
                    <select
                      value={expCategory}
                      onChange={(e) => setExpCategory(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="common_electricity">Điện chung & Thang máy</option>
                      <option value="water">Nước chung tòa nhà</option>
                      <option value="internet">Cáp quang & WiFi</option>
                      <option value="cleaning">Dọn dẹp & Rác</option>
                      <option value="security">Bảo vệ & Giám sát</option>
                      <option value="maintenance">Bảo trì & Sửa chữa</option>
                      <option value="other">Khoản chi khác</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Số tiền (VNĐ) <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="number"
                      required
                      min="1000"
                      placeholder="VD: 500000"
                      value={expAmount}
                      onChange={(e) => setExpAmount(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Ngày chi</label>
                  <input
                    type="date"
                    value={expDate}
                    onChange={(e) => setExpDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Ảnh chứng từ / Hóa đơn</label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setExpReceipt(e.target.files[0] || null)}
                    className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                  />
                </div>

                <div className="pt-2 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setCreateExpenseOpen(false)}
                    className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl min-h-[44px]"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    disabled={submittingExp}
                    className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs disabled:opacity-50 min-h-[44px]"
                  >
                    {submittingExp ? 'Đang lưu...' : 'Lưu khoản chi'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Quyết toán hoàn cọc */}
        {settleModalContract && (
          <MoveOutRefundModal
            contract={settleModalContract}
            onClose={() => setSettleModalContract(null)}
            onSuccess={() => {
              refetchContracts()
              refetchSummary()
            }}
          />
        )}
      </div>
    </AppLayout>
  )
}
