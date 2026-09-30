"""
SAMS - Operating Expenses (OpEx) Controller
Quản lý chi phí vận hành tòa nhà và báo cáo tài chính doanh thu / lợi nhuận ròng.
"""
from datetime import datetime, date, timezone
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.services.expense_service import ExpenseService
from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required, landlord_required
from app.utils.upload import save_uploaded_file

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/v1/expenses")


@expenses_bp.get("")
@landlord_required
def get_expenses():
    """Lấy danh sách các khoản chi phí OpEx theo bộ lọc."""
    building_id = request.args.get("building_id", type=int)
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    category = request.args.get("category")

    expenses = ExpenseService.get_expenses(
        building_id=building_id,
        month=month,
        year=year,
        category=category,
    )
    return success_response(data=expenses)


@expenses_bp.post("")
@landlord_required
def create_expense():
    """Ghi nhận chi phí vận hành mới (hỗ trợ multipart form-data kèm ảnh hóa đơn hoặc json)."""
    user_id = int(get_jwt_identity())

    if request.content_type and "multipart/form-data" in request.content_type:
        building_id = request.form.get("building_id", type=int)
        expense_category = request.form.get("expense_category")
        title = request.form.get("title")
        amount = request.form.get("amount", type=float)
        expense_date_str = request.form.get("expense_date")
        receipt_image_url = None

        if "receipt_image" in request.files and request.files["receipt_image"].filename:
            try:
                receipt_image_url = save_uploaded_file(request.files["receipt_image"], subfolder="receipts")
            except Exception as e:
                return error_response("UPLOAD_FAILED", f"Lỗi upload ảnh hóa đơn: {str(e)}", 400)
    else:
        payload = request.get_json(silent=True) or {}
        building_id = payload.get("building_id")
        expense_category = payload.get("expense_category")
        title = payload.get("title")
        amount = payload.get("amount")
        expense_date_str = payload.get("expense_date")
        receipt_image_url = payload.get("receipt_image_url")

    if not building_id or not expense_category or not title or amount is None:
        return error_response(
            "MISSING_FIELDS",
            "building_id, expense_category, title, amount là bắt buộc.",
            400,
        )

    try:
        exp_date = (
            datetime.strptime(expense_date_str, "%Y-%m-%d").date()
            if expense_date_str
            else date.today()
        )
    except ValueError:
        exp_date = date.today()

    try:
        expense = ExpenseService.create_expense(
            building_id=int(building_id),
            recorded_by=user_id,
            expense_category=expense_category,
            title=title,
            amount=float(amount),
            expense_date=exp_date,
            receipt_image_url=receipt_image_url,
        )
    except ValueError as ve:
        return error_response("VALIDATION_ERROR", str(ve), 400)
    except Exception as e:
        return error_response("INTERNAL_ERROR", f"Lỗi ghi nhận chi phí: {str(e)}", 500)

    return success_response(data=expense, status_code=201)


@expenses_bp.get("/summary")
@landlord_required
def get_financial_summary():
    """Lấy báo cáo tổng hợp Doanh thu - Chi phí OpEx - Lợi nhuận Ròng theo tháng/năm."""
    now = datetime.now(timezone.utc)
    month = request.args.get("month", default=now.month, type=int)
    year = request.args.get("year", default=now.year, type=int)
    building_id = request.args.get("building_id", type=int)

    summary = ExpenseService.get_financial_summary(
        month=month,
        year=year,
        building_id=building_id,
    )
    return success_response(data=summary)
