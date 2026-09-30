# BỘ QUY TẮC THIẾT KẾ & LẬP TRÌNH CHỐNG "AI SLOP" (STRICT ANTI-AI-SLOP DESIGN RULES)
**Áp dụng cho:** Toàn bộ AI Coding Assistants, Subagents và Kỹ sư phát triển dự án SAMS  
**Chuyên môn:** `/ui-ux-designer`, `/tailwind-design-system`, `/frontend-developer`  
**Mục tiêu:** Tuyệt đối loại bỏ các sản phẩm giao diện cẩu thả, rập khuôn, thiếu thực tế, màu sắc vô hồn hoặc trải nghiệm giả tạo ("AI Slop"), xây dựng giao diện chuẩn công nghiệp, sắc sảo, thẩm mỹ cao và chuẩn nghiệp vụ căn hộ cho thuê.

---

## 1. ĐỊNH NGHĨA "AI SLOP" TRONG THIẾT KẾ VÀ CODE FRONTEND
"AI Slop" là thuật ngữ chỉ các sản phẩm do AI sinh ra mang tính chất hời hợt, sáo rỗng, bao gồm:
1. **Visual Slop:** Dùng gradient tím/hồng neon bừa bãi; các thẻ card bo góc tròn trịa vô tội vạ; icon lơ lửng vô nghĩa; độ tương phản kém (chữ xám mờ trên nền trắng); thiếu cấu trúc phân cấp thị giác.
2. **UX Slop:** Bấm nút không có phản hồi/loading; tải dữ liệu không có skeleton mà để màn hình trắng; không có empty states; dùng popup `alert()` mặc định của trình duyệt; vỡ giao diện trên di động.
3. **Code Slop:** Hard-code mã màu hex tùy tiện (`bg-[#4f46e5]`); dùng arbitrary classes bừa bãi (`w-[347px]`, `mt-[23px]`); bỏ qua accessibility (`focus-visible`); phá vỡ Dark Mode; lạm dụng `@apply` bừa bãi.

---

## 2. BẢN QUY TẮC THIẾT KẾ NGHIÊM NGẶT (STRICT MANDATES)

### 🔴 QUY TẮC 1: CẤM GRADIENT NEON VÔ NGHĨA & BẮT BUỘC SEMANTIC DESIGN TOKENS
- **CẤM:** 
  - `bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500` hoặc các dải màu tím/hồng neon generic thường thấy ở các template AI tạo mẫu rẻ tiền.
  - Hard-code mã màu hex trực tiếp trong file JSX/TSX: `bg-[#1e293b]`, `text-[#0f172a]`, `border-[#e2e8f0]`.
- **BẮT BUỘC:**
  - Sử dụng 100% **Semantic Design Tokens** định nghĩa qua HSL CSS Variables:
    - Nền & Chữ: `bg-background`, `text-foreground`
    - Thẻ nội dung: `bg-card`, `text-card-foreground`, `border-border`
    - Điểm nhấn chính: `bg-primary`, `text-primary-foreground`
    - Trạng thái phụ/làm dịu: `bg-muted`, `text-muted-foreground`
    - Cảnh báo/xóa: `bg-destructive`, `text-destructive-foreground`
  - Bảng màu chủ đạo của SAMS là **Slate & Deep Indigo** (chuyên nghiệp, sang trọng, tin cậy cho tài chính và quản lý bất động sản).
  - Mọi component phải tự động hiển thị hoàn hảo ở cả **Light Mode** và **Dark Mode**.

### 🔴 QUY TẮC 2: CẤM BO GÓC BỪA BÃI & THIẾT LẬP PHÂN TẦNG ĐỘ NỔI (SHAPE & ELEVATION)
- **CẤM:**
  - Lạm dụng `rounded-3xl` hoặc `rounded-full` cho các khối Card lớn chứa bảng dữ liệu hay form nhập liệu.
  - Đổ bóng đen kịt, đậm lè (`shadow-2xl shadow-black/80`).
- **BẮT BUỘC:**
  - Khối Card, Container, Bảng dữ liệu: Sử dụng `rounded-lg` (8px) hoặc `rounded-xl` (12px).
  - Nút bấm (Button), Ô nhập liệu (Input), Select dropdown: Sử dụng `rounded-md` (6px).
  - Badge trạng thái, Avatar: Sử dụng `rounded-full`.
  - Thay vì đổ bóng nặng nề, hãy dùng kỹ thuật viền tinh tế kết hợp bóng nhẹ:
    `border border-border/60 bg-card shadow-sm hover:shadow transition-shadow`

### 🔴 QUY TẮC 3: BẮT BUỘC ĐỦ 5 TRẠNG THÁI GIAO DIỆN (THE 5 MANDATORY UI STATES)
Mọi component hoặc màn hình tương tác dữ liệu BẮT BUỘC phải cài đặt đủ 5 trạng thái:
1. **Loading State:** Khi đang fetch dữ liệu, BẮT BUỘC dùng **Skeleton Loader** (`animate-pulse bg-muted rounded`). CẤM để màn hình trắng hoặc chữ "Loading..." trơ trọi.
2. **Empty State:** Khi không có dữ liệu (chưa có phòng, chưa có hóa đơn), BẮT BUỘC hiển thị:
   - Icon minh họa trực quan từ Lucide React (màu `text-muted-foreground/60`).
   - Tiêu đề ngắn gọn: *"Chưa có hóa đơn nào trong tháng này"*.
   - Lời giải thích nhẹ nhàng và Nút hành động (CTA) hướng dẫn người dùng bước tiếp theo.
3. **Error State:** Khi API lỗi hoặc mất mạng: Hiển thị hộp thông báo viền đỏ dịu (`border-destructive/30 bg-destructive/10 text-destructive`), có nút "Thử lại" (Retry).
4. **Interactive / Submitting State:** Nút bấm khi đang gửi request BẮT BUỘC:
   - Khóa nút: `disabled={isSubmitting}`
   - Hiển thị spinner quay tròn: `<Loader2 className="mr-2 h-4 w-4 animate-spin" />`
   - Đổi nhãn nút: *"Đang xử lý..."*
5. **Success State:** CẤM dùng `alert()` của trình duyệt. BẮT BUỘC dùng **Toast Notification** (Shadcn Toast/Sonner) thông báo thành công ở góc màn hình, tự ẩn sau 3 giây.

### 🔴 QUY TẮC 4: BẮT BUỘC MOBILE-FIRST & CHUẨN THAO TÁC CẢM ỨNG (TOUCH TARGETS)
Khách thuê thao tác chính trên điện thoại thông minh (tra cứu hóa đơn, quét QR, chụp ảnh công tơ):
- **CẤM:**
  - Layout bị tràn ngang, xuất hiện thanh cuộn ngang khó chịu trên mobile.
  - Nút bấm quá nhỏ, đặt sát nhau khiến ngón tay cái dễ bấm nhầm.
- **BẮT BUỘC:**
  - Mọi phần tử bấm được (Button, Tab, Input) phải có chiều cao tối thiểu **44px** (`h-11` hoặc `min-h-[44px]`).
  - Bảng dữ liệu nhiều cột trên desktop phải tự động chuyển thành **Card View xếp dọc** khi hiển thị trên màn hình nhỏ `< 640px` (breakpoint `sm:`).
  - Kiểm thử giao diện trực tiếp trên khung màn hình di động chuẩn: 375px (iPhone SE) và 390px (iPhone 14/15/16).

### 🔴 QUY TẮC 5: CẤM DỮ LIỆU GIẢ VÔ LÝ & MINH HỌA TRẺ CON
- **CẤM:**
  - Dùng hình vẽ 3D hoạt hình pastel bóng bẩy kiểu meme AI không phù hợp với ngữ cảnh quản lý tài chính/căn hộ.
  - Điền dữ liệu test vô lý: "Phòng 9999", "Giá 1$", "Tên: asdfghjkl".
- **BẮT BUỘC:**
  - Sử dụng bộ Icon nhất quán duy nhất: **Lucide React** với `strokeWidth={1.75}` hoặc `2`.
  - Dữ liệu hiển thị phải phản ánh đúng thực tế Việt Nam:
    - Tiền tệ: Luôn định dạng có dấu chấm phân cách hàng nghìn kèm đơn vị VNĐ (Ví dụ: `3.500.000 đ`).
    - Số điện / nước: Định dạng số thực 1 chữ số thập phân kèm đơn vị (`85.5 kWh`, `12.0 m³`).
    - Ngày tháng: Định dạng chuẩn Việt Nam `DD/MM/YYYY`.

### 🔴 QUY TẮC 6: CHUẨN MỰC TAILWIND CSS & THÀNH PHẦN CVA
- **CẤM:**
  - Dùng arbitrary values tràn lan: `w-[327px]`, `mt-[19px]`, `p-[13px]`.
  - Lạm dụng `@apply` trong file CSS.
  - Quên trạng thái Accessible Focus.
- **BẮT BUỘC:**
  - Tuân thủ Spacing Scale chuẩn của Tailwind: `1` (4px), `2` (8px), `3` (12px), `4` (16px), `6` (24px), `8` (32px)...
  - Sử dụng thư viện **Class Variance Authority (CVA)** kết hợp hàm `cn(clsx, twMerge)` để định nghĩa variants:
    ```typescript
    import { cva, type VariantProps } from 'class-variance-authority'
    import { cn } from '@/lib/utils'

    const badgeVariants = cva(
      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
      {
        variants: {
          variant: {
            default: "bg-primary text-primary-foreground",
            success: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20",
            warning: "bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/20",
            destructive: "bg-destructive/15 text-destructive border border-destructive/20",
          }
        },
        defaultVariants: { variant: "default" }
      }
    )
    ```
  - Mọi input và button phải có focus ring chuẩn trợ năng:
    `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`

### 🔴 QUY TẮC 7: TRẢI NGHIỆM AI TRỰC QUAN & CHAT STREAMING SẮC SẢO
- **CẤM:**
  - Khung chat đơ cứng, người dùng không biết AI đang suy nghĩ hay bị treo.
  - In ra toàn bộ kết quả tra cứu hóa đơn dạng văn bản thuần túy không có cấu trúc.
- **BẮT BUỘC:**
  - Khi AI đang xử lý: Hiển thị bong bóng Typing Indicator với hiệu ứng chấm nhảy mượt mà (`animate-bounce`).
  - Hỗ trợ **Streaming Markdown Rendering**: Chữ xuất hiện mượt mà từng từ kèm con trỏ nhấp nháy (`animate-pulse`).
  - Hỗ trợ **Rich Interactive Cards** ngay trong dòng tin nhắn:
    - Khi AI trả lời về hóa đơn: Render thẻ hóa đơn thu nhỏ có số tiền nổi bật, hạn nộp và nút *"Xem mã VietQR"* để mở popup thanh toán ngay trong khung chat.
    - Khi AI tạo ticket báo hỏng thành công: Render thẻ ticket có mã số, trạng thái *"Chờ xử lý"* và thời gian dự kiến kỹ thuật viên đến.

---

## 3. CHECKLIST KIỂM ĐỊNH TRƯỚC KHI COMMIT MÃ NGUỒN GIAO DIỆN

Trước khi bàn giao bất kỳ trang hoặc component giao diện nào, lập trình viên/AI phải tự kiểm tra 8 câu hỏi:
- [ ] 1. Component có hoạt động chuẩn trên cả Dark Mode và Light Mode không?
- [ ] 2. Đã có Skeleton Loader khi đang tải dữ liệu chưa?
- [ ] 3. Nếu danh sách rỗng, đã có Empty State với icon và nút gợi ý hành động chưa?
- [ ] 4. Nút submit có hiển thị spinner và khóa click khi đang gửi dữ liệu không?
- [ ] 5. Có bất kỳ popup `alert()` nào của trình duyệt sót lại không? (Phải thay bằng Toast/Modal).
- [ ] 6. Nút bấm trên di động có đạt chiều cao tối thiểu 44px không?
- [ ] 7. Các con số tiền tệ đã được format chuẩn VNĐ (`3.500.000 đ`) chưa?
- [ ] 8. Có sử dụng mã màu hex hard-code hay arbitrary classes vô căn cứ không?

**BẤT KỲ ĐOẠN CODE NÀO VI PHẠM CÁC QUY TẮC TRÊN ĐỀU BỊ COI LÀ "AI SLOP" VÀ KHÔNG ĐẠT TIÊU CHUẨN NGHIỆM THU.**
