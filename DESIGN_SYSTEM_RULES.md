# SAMS DESIGN SYSTEM & ANTI-AI SLOP RULES
Tài liệu quy định các tiêu chuẩn thiết kế và lập trình giao diện React + Tailwind CSS cho dự án SAMS.

Chi tiết xem tại:
- File luật tự động nạp cho AI: [.agents/rules/anti_ai_slop_design_rules.md](file:///c:/Users/kaedee206/Documents/hethongquanlycanho/.agents/rules/anti_ai_slop_design_rules.md)
- Đặc tả yêu cầu phần mềm: [SRS.md (Mục 9)](file:///c:/Users/kaedee206/Documents/hethongquanlycanho/SRS.md)
- Kế hoạch triển khai: [implementation_plan.md](file:///C:/Users/kaedee206/.gemini/antigravity-ide/brain/bf91d6c9-c4dc-46a1-adaf-c7431354d556/implementation_plan.md)

### 7 ĐIỀU RĂN CHỐNG AI SLOP:
1. **Cấm Gradient tím/hồng neon vô nghĩa:** 100% sử dụng HSL Semantic Tokens (`bg-background`, `text-foreground`, `bg-card`, `border-border`, `bg-primary`, `bg-muted`). Bảng màu chủ đạo: Slate & Deep Indigo. Hỗ trợ Dark/Light mode tự nhiên.
2. **Cấm bo góc bừa bãi:** Card/Modal dùng `rounded-lg` (8px) hoặc `rounded-xl` (12px). Nút bấm/Input dùng `rounded-md` (6px). Viền tinh tế `border border-border/60 shadow-sm`. Cấm đổ bóng đen xì dày đặc.
3. **Bắt buộc đủ 5 trạng thái:** Loading (Skeleton), Empty (Icon + CTA), Error (Banner viền đỏ), Submitting (Spinner quay + disabled), Success (Toast notification, cấm `alert()`).
4. **Bắt buộc Mobile-First & Touch Targets:** Chiều cao vùng chạm tối thiểu 44px (`h-11`). Bảng phức tạp tự chuyển thành Card View trên màn hình nhỏ. Không tràn thanh cuộn ngang.
5. **Cấm minh họa 3D trẻ con & số liệu giả:** Thống nhất duy nhất 1 bộ icon vector Lucide React. Số tiền luôn định dạng phân cách hàng nghìn VNĐ (`3.500.000 đ`).
6. **Chuẩn mực Tailwind CVA & Accessibility:** Cấm arbitrary classes (`w-[347px]`). Đóng gói components qua Class Variance Authority (CVA) + `cn()`. Mọi phần tử tương tác bắt buộc có focus ring.
7. **Trải nghiệm AI Streaming chuyên nghiệp:** Typing indicator chấm nhảy (`animate-bounce`), streaming markdown rendering mượt mà, render Rich Cards (hóa đơn VietQR, ticket) trực tiếp trong bong bóng chat.
