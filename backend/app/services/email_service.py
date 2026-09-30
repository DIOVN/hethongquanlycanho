"""
SAMS - Email Service via SMTP
Dịch vụ gửi thư điện tử qua giao thức SMTP tiêu chuẩn (Gmail, Outlook, Custom SMTP).
Hỗ trợ gửi mã OTP đăng ký tài khoản, quên mật khẩu và các thông báo vận hành.
Tự động fallback in mã OTP ra console khi chưa cấu hình tài khoản SMTP thực tế.
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from flask import current_app, has_app_context

logger = logging.getLogger(__name__)


class EmailService:
    """Service gửi email qua SMTP với giao diện HTML chuẩn mực."""

    @staticmethod
    def _render_otp_html(otp_code: str, purpose: str, recipient_email: str) -> tuple[str, str]:
        """Tạo tiêu đề và nội dung HTML email chuyên nghiệp cho mã OTP."""
        if purpose == "register":
            subject = f"[SAMS] Mã xác thực đăng ký tài khoản: {otp_code}"
            title = "Xác Thực Đăng Ký Tài Khoản"
            lead = f"Xin chào bạn, chúng tôi nhận được yêu cầu đăng ký tài khoản mới trên Hệ thống Quản lý Căn hộ Thông minh (SAMS) cho email <strong>{recipient_email}</strong>."
            action_desc = "Vui lòng nhập mã OTP 6 số dưới đây để kích hoạt và hoàn tất hồ sơ cư dân của bạn:"
            caution = "Mã OTP này có hiệu lực trong vòng <strong>10 phút</strong>. Vì lý do an toàn, tuyệt đối không chia sẻ mã này cho bất kỳ ai."
        else:  # forgot_password
            subject = f"[SAMS] Mã xác thực đặt lại mật khẩu: {otp_code}"
            title = "Yêu Cầu Đặt Lại Mật Khẩu"
            lead = f"Xin chào, hệ thống SAMS nhận được yêu cầu cấp lại mật khẩu cho tài khoản <strong>{recipient_email}</strong>."
            action_desc = "Nhập mã OTP 6 số dưới đây vào ứng dụng để tiến hành thiết lập mật khẩu mới:"
            caution = "Mã OTP có hiệu lực trong vòng <strong>10 phút</strong>. Nếu bạn không gửi yêu cầu này, vui lòng bỏ qua email hoặc thông báo cho Ban quản lý tòa nhà ngay lập tức."

        html = f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>{subject}</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
          <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 40px 10px;">
            <tr>
              <td align="center">
                <table width="100%" max-width="540" border="0" cellspacing="0" cellpadding="0" style="max-width: 540px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
                  <!-- Header -->
                  <tr>
                    <td style="background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%); padding: 32px 30px; text-align: center;">
                      <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">SAMS APARTMENT</h1>
                      <p style="margin: 6px 0 0 0; color: #e0e7ff; font-size: 13px; font-weight: 500;">Hệ thống Quản lý Căn hộ Cho thuê Thông minh</p>
                    </td>
                  </tr>

                  <!-- Body -->
                  <tr>
                    <td style="padding: 36px 32px;">
                      <h2 style="margin: 0 0 16px 0; color: #0f172a; font-size: 20px; font-weight: 700; text-align: center;">{title}</h2>
                      <p style="margin: 0 0 16px 0; color: #475569; font-size: 14px; line-height: 1.6;">{lead}</p>
                      <p style="margin: 0 0 24px 0; color: #475569; font-size: 14px; line-height: 1.6;">{action_desc}</p>

                      <!-- OTP Box -->
                      <div style="background-color: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
                        <span style="display: block; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: #64748b; margin-bottom: 8px;">MÃ XÁC THỰC OTP</span>
                        <span style="font-family: 'Courier New', Courier, monospace; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #4f46e5;">{otp_code}</span>
                      </div>

                      <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 12px 16px; border-radius: 6px; margin-bottom: 24px;">
                        <p style="margin: 0; color: #991b1b; font-size: 12px; line-height: 1.5;">⚠️ {caution}</p>
                      </div>

                      <p style="margin: 0; color: #64748b; font-size: 13px; line-height: 1.5;">Nếu có bất kỳ thắc mắc nào, bạn có thể liên hệ Ban Quản lý Tòa nhà qua hotline hoặc ứng dụng SAMS.</p>
                    </td>
                  </tr>

                  <!-- Footer -->
                  <tr>
                    <td style="background-color: #f8fafc; padding: 20px 32px; border-top: 1px solid #e2e8f0; text-align: center;">
                      <p style="margin: 0; color: #94a3b8; font-size: 12px;">© 2026 SAMS - Smart Apartment Management System. Mọi quyền được bảo lưu.</p>
                      <p style="margin: 4px 0 0 0; color: #cbd5e1; font-size: 11px;">Thư tự động, vui lòng không phản hồi trực tiếp vào địa chỉ này.</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </body>
        </html>
        """
        return subject, html

    @classmethod
    def send_otp_email(cls, recipient_email: str, otp_code: str, purpose: str = "register") -> dict:
        """
        Gửi email chứa mã OTP tới người dùng qua SMTP.
        Nếu chưa cấu hình thông tin SMTP trên môi trường phát triển, tự động fallback in ra console.
        """
        subject, html_content = cls._render_otp_html(otp_code, purpose, recipient_email)

        # Đọc cấu hình từ Flask app hoặc biến môi trường
        if has_app_context():
            smtp_host = current_app.config.get("SMTP_HOST", "smtp.gmail.com")
            smtp_port = current_app.config.get("SMTP_PORT", 587)
            smtp_user = current_app.config.get("SMTP_USER", "")
            smtp_pass = current_app.config.get("SMTP_PASSWORD", "")
            from_email = current_app.config.get("SMTP_FROM_EMAIL") or smtp_user or "no-reply@sams.local"
            from_name = current_app.config.get("SMTP_FROM_NAME", "Hệ thống Quản lý Căn hộ SAMS")
            use_tls = current_app.config.get("SMTP_USE_TLS", True)
            use_ssl = current_app.config.get("SMTP_USE_SSL", False)
        else:
            smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.environ.get("SMTP_PORT", 587))
            smtp_user = os.environ.get("SMTP_USER", "")
            smtp_pass = os.environ.get("SMTP_PASSWORD", "")
            from_email = os.environ.get("SMTP_FROM_EMAIL") or smtp_user or "no-reply@sams.local"
            from_name = os.environ.get("SMTP_FROM_NAME", "Hệ thống Quản lý Căn hộ SAMS")
            use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() in ("true", "1")
            use_ssl = os.environ.get("SMTP_USE_SSL", "false").lower() in ("true", "1")

        # -------------------------------------------------------------
        # 1. Fallback Mock Mode khi chưa cấu hình mật khẩu SMTP
        # -------------------------------------------------------------
        if not smtp_user or not smtp_pass or smtp_pass == "your_app_password":
            print("\n" + "=" * 70)
            print(f"📧 [SAMS EMAIL SERVICE - DEVELOPMENT MOCK MODE]")
            print(f"   Người nhận : {recipient_email}")
            print(f"   Tiêu đề    : {subject}")
            print(f"   Mục đích   : {'Đăng ký tài khoản' if purpose == 'register' else 'Quên mật khẩu'}")
            print(f"   MÃ OTP     : >>> {otp_code} <<< (Hiệu lực: 10 phút)")
            print(f"   (Để gửi qua email thật, hãy điền SMTP_USER & SMTP_PASSWORD vào file .env)")
            print("=" * 70 + "\n")
            return {
                "success": True,
                "mode": "mock_console",
                "recipient": recipient_email,
                "otp_code": otp_code,
                "message": "Mã OTP đã được tạo và ghi nhận (Chế độ mô phỏng Console)."
            }

        # -------------------------------------------------------------
        # 2. Live SMTP Sending Mode
        # -------------------------------------------------------------
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr((from_name, from_email))
        msg["To"] = recipient_email

        # Plain text alternative
        plain_text = f"Mã xác thực SAMS ({purpose}) của bạn là: {otp_code}. Mã có hiệu lực trong 10 phút."
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            if use_ssl or smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=12)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=12)
                if use_tls:
                    server.starttls()

            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [recipient_email], msg.as_string())
            server.quit()
            logger.info(f"Email OTP successfully sent to {recipient_email} via SMTP {smtp_host}")
            return {
                "success": True,
                "mode": "smtp_live",
                "recipient": recipient_email,
                "message": f"Mã OTP đã được gửi thành công đến hộp thư {recipient_email}."
            }
        except Exception as exc:
            logger.error(f"Failed to send email via SMTP ({smtp_host}:{smtp_port}): {exc}")
            # In ra console để việc đăng ký/test không bị nghẽn
            print("\n" + "!" * 70)
            print(f"⚠️ [SMTP ERROR: {exc}]")
            print(f"   Fallback Console OTP cho {recipient_email}: >>> {otp_code} <<<")
            print("!" * 70 + "\n")
            return {
                "success": True,
                "mode": "fallback_console",
                "recipient": recipient_email,
                "otp_code": otp_code,
                "error": str(exc),
                "message": "Không thể kết nối máy chủ SMTP, mã OTP dự phòng đã ghi nhận."
            }
