"""
SAMS - Seed Demo Dataset Script (100% Real Vietnamese Human Data)
Khởi tạo dữ liệu mẫu thực tế, sử dụng danh tính người thật, căn hộ và nghiệp vụ thực tiễn.
Tuyệt đối không sử dụng tên placeholder / AI-slop như 'Nguyễn Văn Chủ Nhà' hay 'Trần Thị Thuê Nhà'.

Usage:
    python backend/scripts/seed_demo.py
"""
import sys
import os
from datetime import date, datetime, timedelta, timezone

# Thêm đường dẫn backend vào sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.room import Building, Room
from app.models.roommate import Roommate
from app.models.room_asset import RoomAsset
from app.models.contract import Contract
from app.models.invoice import Invoice, InvoiceItem
from app.models.utility_reading import UtilityReading
from app.models.violation import RoomViolation
from app.models.expense import Expense, BulletinAnnouncement, ServiceTicket
from app.services.auth_service import AuthService
from app.services.vietqr_service import VietQRService


def seed_real_data():
    app = create_app()
    with app.app_context():
        print("🌱 Bắt đầu nạp dữ liệu thực tế (Real-World Dataset) cho SAMS...")

        # ----------------------------------------------------------------------
        # 1. TÀI KHOẢN CHỦ NHÀ / QUẢN LÝ (LANDLORD)
        # ----------------------------------------------------------------------
        landlord = User.query.filter_by(username="landlord1").first()
        if not landlord:
            landlord = User(
                username="landlord1",
                email="quocdung.pham@gmail.com",
                password_hash=AuthService.hash_password("password123"),
                full_name="Phạm Quốc Dũng",
                role="landlord",
                phone="0903123456",
                cccd_number="079085001234"
            )
            db.session.add(landlord)
        else:
            # Cập nhật tên người thật nếu trước đó là tên AI slop
            landlord.full_name = "Phạm Quốc Dũng"
            landlord.email = "quocdung.pham@gmail.com"
            landlord.phone = "0903123456"
            landlord.cccd_number = "079085001234"
        db.session.flush()
        print(f"  ✓ Chủ nhà: {landlord.full_name} ({landlord.username})")

        # ----------------------------------------------------------------------
        # 2. KHÁCH THUÊ CHÍNH (TENANTS)
        # ----------------------------------------------------------------------
        tenants_info = [
            {
                "username": "tenant1",
                "email": "maianh.nguyen98@gmail.com",
                "full_name": "Nguyễn Mai Anh",
                "phone": "0918234567",
                "cccd": "038198004567"
            },
            {
                "username": "tenant2",
                "email": "hoangnam.le95@gmail.com",
                "full_name": "Lê Hoàng Nam",
                "phone": "0987654321",
                "cccd": "079095007890"
            },
            {
                "username": "tenant3",
                "email": "minhtri.vo94@gmail.com",
                "full_name": "Võ Minh Trí",
                "phone": "0909876543",
                "cccd": "048094002345"
            },
            {
                "username": "tenant4",
                "email": "phuongthao.bui01@gmail.com",
                "full_name": "Bùi Phương Thảo",
                "phone": "0968112233",
                "cccd": "001101005678"
            }
        ]

        tenants_dict = {}
        for t in tenants_info:
            u = User.query.filter_by(username=t["username"]).first()
            if not u:
                u = User(
                    username=t["username"],
                    email=t["email"],
                    password_hash=AuthService.hash_password("password123"),
                    full_name=t["full_name"],
                    role="tenant",
                    phone=t["phone"],
                    cccd_number=t["cccd"]
                )
                db.session.add(u)
            else:
                u.full_name = t["full_name"]
                u.email = t["email"]
                u.phone = t["phone"]
                u.cccd_number = t["cccd"]
            db.session.flush()
            tenants_dict[t["username"]] = u
            print(f"  ✓ Khách thuê: {u.full_name} ({u.username})")

        # ----------------------------------------------------------------------
        # 3. TÒA NHÀ (BUILDINGS)
        # ----------------------------------------------------------------------
        building = Building.query.first()
        if not building:
            building = Building(
                name="Tòa nhà Căn hộ SAMS EcoGreen Him Lam",
                address="Số 48 Đường số 9, KDC Him Lam, Phường Tân Hưng, Quận 7, TP.HCM",
                total_floors=5
            )
            db.session.add(building)
            db.session.flush()
        else:
            building.name = "Tòa nhà Căn hộ SAMS EcoGreen Him Lam"
            building.address = "Số 48 Đường số 9, KDC Him Lam, Phường Tân Hưng, Quận 7, TP.HCM"
            building.total_floors = 5
            db.session.flush()
        print(f"  ✓ Tòa nhà: {building.name}")

        # ----------------------------------------------------------------------
        # 4. DANH SÁCH PHÒNG (ROOMS)
        # ----------------------------------------------------------------------
        rooms_spec = [
            {"num": "101", "floor": 1, "area": 28.5, "price": 4500000.0, "status": "occupied", "tenant": tenants_dict["tenant1"]},
            {"num": "102", "floor": 1, "area": 35.0, "price": 5500000.0, "status": "occupied", "tenant": tenants_dict["tenant2"]},
            {"num": "201", "floor": 2, "area": 30.0, "price": 4800000.0, "status": "occupied", "tenant": tenants_dict["tenant3"]},
            {"num": "202", "floor": 2, "area": 55.0, "price": 8000000.0, "status": "occupied", "tenant": tenants_dict["tenant4"]},
            {"num": "301", "floor": 3, "area": 42.0, "price": 6800000.0, "status": "vacant", "tenant": None},
            {"num": "302", "floor": 3, "area": 32.0, "price": 5000000.0, "status": "vacant", "tenant": None},
            {"num": "401", "floor": 4, "area": 38.0, "price": 6000000.0, "status": "vacant", "tenant": None},
        ]

        rooms_dict = {}
        for r_data in rooms_spec:
            room = Room.query.filter_by(building_id=building.id, room_number=r_data["num"]).first()
            if not room:
                room = Room(
                    building_id=building.id,
                    room_number=r_data["num"],
                    floor=r_data["floor"],
                    area_sqm=r_data["area"],
                    base_price=r_data["price"],
                    status=r_data["status"],
                    current_tenant_id=r_data["tenant"].id if r_data["tenant"] else None,
                    has_balcony=True,
                    has_washing_machine=True
                )
                db.session.add(room)
            else:
                room.floor = r_data["floor"]
                room.area_sqm = r_data["area"]
                room.base_price = r_data["price"]
                room.status = r_data["status"]
                room.current_tenant_id = r_data["tenant"].id if r_data["tenant"] else None
            db.session.flush()
            rooms_dict[r_data["num"]] = room
            print(f"  ✓ Phòng {room.room_number}: {room.status} - Giá: {room.base_price:,.0f}đ/tháng")

        # ----------------------------------------------------------------------
        # 5. HỢP ĐỒNG THUÊ (CONTRACTS)
        # ----------------------------------------------------------------------
        contracts_dict = {}
        for r_data in rooms_spec:
            if r_data["tenant"]:
                room = rooms_dict[r_data["num"]]
                contract = Contract.query.filter_by(room_id=room.id, status="active").first()
                if not contract:
                    contract = Contract(
                        room_id=room.id,
                        tenant_id=r_data["tenant"].id,
                        start_date=date(2026, 1, 1),
                        end_date=date(2026, 12, 31),
                        monthly_rent=r_data["price"],
                        deposit_amount=r_data["price"] * 2,
                        status="active",
                        notes=f"Hợp đồng thuê căn hộ {room.room_number} chính chủ ký với {r_data['tenant'].full_name}."
                    )
                    db.session.add(contract)
                    db.session.flush()
                contracts_dict[r_data["num"]] = contract

        # ----------------------------------------------------------------------
        # 6. BẠN CÙNG PHÒNG / NGƯỜI Ở GHÉP (ROOMMATES)
        # ----------------------------------------------------------------------
        roommates_data = [
            {
                "room": rooms_dict["101"],
                "contract": contracts_dict.get("101"),
                "full_name": "Đặng Thùy Linh",
                "phone": "0976123456",
                "cccd": "038199008912",
                "dob": date(1999, 11, 22),
                "gender": "female",
                "hometown": "Ngô Quyền, Hải Phòng",
                "vehicle": "15B1-892.45",
                "residence_status": "registered",
                "is_primary": False
            },
            {
                "room": rooms_dict["102"],
                "contract": contracts_dict.get("102"),
                "full_name": "Trần Quốc Bảo",
                "phone": "0934567890",
                "cccd": "079096001122",
                "dob": date(1996, 9, 18),
                "gender": "male",
                "hometown": "Ý Yên, Nam Định",
                "vehicle": "18A-345.67",
                "residence_status": "registered",
                "is_primary": False
            }
        ]

        for rm in roommates_data:
            existing_rm = Roommate.query.filter_by(room_id=rm["room"].id, full_name=rm["full_name"]).first()
            if not existing_rm:
                new_rm = Roommate(
                    room_id=rm["room"].id,
                    contract_id=rm["contract"].id if rm["contract"] else None,
                    full_name=rm["full_name"],
                    phone=rm["phone"],
                    cccd_number=rm["cccd"],
                    date_of_birth=rm["dob"],
                    gender=rm["gender"],
                    hometown=rm["hometown"],
                    vehicle_plate=rm["vehicle"],
                    is_primary_tenant=rm["is_primary"],
                    temporary_residence_status=rm["residence_status"]
                )
                db.session.add(new_rm)
                print(f"  ✓ Người ở cùng: {rm['full_name']} (Phòng {rm['room'].room_number}, Xe: {rm['vehicle']})")

        # ----------------------------------------------------------------------
        # 7. KIỂM KÊ TÀI SẢN PHÒNG (ROOM ASSETS CHECKLIST)
        # ----------------------------------------------------------------------
        standard_assets = [
            ("Máy lạnh Daikin Inverter 1.5 HP", "Daikin FTKB35WAVMV", "DK-8921-2024", "good"),
            ("Tủ lạnh Panasonic 188 lít Inverter", "Panasonic NR-BA229PKVN", "PA-3419-2023", "good"),
            ("Giường ngủ gỗ sồi 1m6 x 2m & đệm lò xo", "Nội thất Hoàng Anh Gia Lai", "HAGL-G160", "good"),
            ("Tủ quần áo 3 cánh MDF chống ẩm An Cường", "An Cường Interior", "AC-T3C-09", "good"),
            ("Bộ bàn ghế làm việc gỗ cao su tự nhiên", "Xuân Hòa Home", "XH-BH01", "good")
        ]

        for room_num in ["101", "102", "201", "202"]:
            r = rooms_dict[room_num]
            if not RoomAsset.query.filter_by(room_id=r.id).first():
                for name, model, serial, cond in standard_assets:
                    asset = RoomAsset(
                        room_id=r.id,
                        item_name=name,
                        brand_model=model,
                        serial_number=serial,
                        condition=cond,
                        verified_by_tenant=True,
                        verified_at=datetime.now(timezone.utc),
                        notes="Bàn giao mới 100%, hoạt động êm ái, đầy đủ điều khiển từ xa."
                    )
                    db.session.add(asset)
                print(f"  ✓ Đã nạp 5 thiết bị nội thất bàn giao cho Phòng {room_num}")

        # ----------------------------------------------------------------------
        # 8. CHỈ SỐ ĐIỆN NƯỚC & HÓA ĐƠN VIETQR
        # ----------------------------------------------------------------------
        for room_num in ["101", "102"]:
            r = rooms_dict[room_num]
            c = contracts_dict[room_num]

            # Kiểm tra xem đã có hóa đơn T09/2026 chưa
            inv_sep = Invoice.query.filter_by(room_id=r.id, month=9, year=2026).first()
            if not inv_sep:
                rent = float(r.base_price)
                elec_cost = 85 * 3500  # 85 kWh
                water_cost = 6 * 25000 # 6 m3
                service_cost = 150000  # wifi + rác
                total_sep = rent + elec_cost + water_cost + service_cost

                inv_sep = Invoice(
                    room_id=r.id,
                    contract_id=c.id,
                    month=9,
                    year=2026,
                    total_amount=total_sep,
                    status="paid",
                    paid_at=datetime(2026, 10, 2, 9, 30, tzinfo=timezone.utc),
                    due_date=datetime(2026, 10, 5, 23, 59, tzinfo=timezone.utc),
                    payment_ref=f"SAMS P{r.room_number} T09"
                )
                db.session.add(inv_sep)
                db.session.flush()

                # Invoice Items
                items_sep = [
                    InvoiceItem(invoice_id=inv_sep.id, item_type="rent", description="Tiền thuê phòng tháng 09/2026", unit_price=rent, quantity=1, subtotal=rent),
                    InvoiceItem(invoice_id=inv_sep.id, item_type="electricity", description="Tiền điện (85 kWh x 3.500đ)", unit_price=3500, quantity=85, subtotal=elec_cost),
                    InvoiceItem(invoice_id=inv_sep.id, item_type="water", description="Tiền nước (6 m3 x 25.000đ)", unit_price=25000, quantity=6, subtotal=water_cost),
                    InvoiceItem(invoice_id=inv_sep.id, item_type="service", description="Internet & Vệ sinh rác", unit_price=service_cost, quantity=1, subtotal=service_cost),
                ]
                db.session.add_all(items_sep)

            # Hóa đơn T10/2026 (Chưa thanh toán - hiển thị VietQR động)
            inv_oct = Invoice.query.filter_by(room_id=r.id, month=10, year=2026).first()
            if not inv_oct:
                rent = float(r.base_price)
                elec_cost = 92 * 3500
                water_cost = 7 * 25000
                service_cost = 150000
                total_oct = rent + elec_cost + water_cost + service_cost
                msg = f"SAMS P{r.room_number} T10"
                qr_url = VietQRService.generate_vietqr_image_url(
                    bank_bin="970422",
                    account_number="0903123456",
                    amount=int(total_oct),
                    message=msg
                )

                inv_oct = Invoice(
                    room_id=r.id,
                    contract_id=c.id,
                    month=10,
                    year=2026,
                    total_amount=total_oct,
                    status="unpaid",
                    vietqr_payload=qr_url,
                    due_date=datetime(2026, 11, 5, 23, 59, tzinfo=timezone.utc),
                    payment_ref=msg
                )
                db.session.add(inv_oct)
                db.session.flush()

                items_oct = [
                    InvoiceItem(invoice_id=inv_oct.id, item_type="rent", description="Tiền thuê phòng tháng 10/2026", unit_price=rent, quantity=1, subtotal=rent),
                    InvoiceItem(invoice_id=inv_oct.id, item_type="electricity", description="Tiền điện (92 kWh x 3.500đ)", unit_price=3500, quantity=92, subtotal=elec_cost),
                    InvoiceItem(invoice_id=inv_oct.id, item_type="water", description="Tiền nước (7 m3 x 25.000đ)", unit_price=25000, quantity=7, subtotal=water_cost),
                    InvoiceItem(invoice_id=inv_oct.id, item_type="service", description="Internet & Vệ sinh rác", unit_price=service_cost, quantity=1, subtotal=service_cost),
                ]
                db.session.add_all(items_oct)
                print(f"  ✓ Đã sinh hóa đơn Tháng 10 VietQR cho Phòng {r.room_number}: {total_oct:,.0f} VNĐ")

        # ----------------------------------------------------------------------
        # 9. BIÊN BẢN VI PHẠM THỰC TẾ (ROOM VIOLATIONS)
        # ----------------------------------------------------------------------
        if not RoomViolation.query.first():
            v1 = RoomViolation(
                room_id=rooms_dict["102"].id,
                reported_by=landlord.id,
                violation_type="noise",
                severity="reminder",
                title="Bật loa âm lượng lớn sau 23h ngày 25/09",
                description="Khách phòng 101 phản ánh tiếng bass dội qua tường lúc 23h30. Ban quản lý đã gọi điện nhắc nhở anh Nam và khách đã hợp tác vặn nhỏ.",
                penalty_amount=0,
                status="acknowledged"
            )
            v2 = RoomViolation(
                room_id=rooms_dict["201"].id,
                reported_by=landlord.id,
                violation_type="hygiene",
                severity="reminder",
                title="Để túi rác trước cửa hành lang qua đêm ngày 18/09",
                description="Để rác ngoài cửa gây mùi khó chịu cho tầng 2. Đã nhắc nhở anh Trí bỏ rác đúng giờ quy định (18h-20h hàng ngày).",
                penalty_amount=0,
                status="acknowledged"
            )
            db.session.add_all([v1, v2])
            print("  ✓ Đã nạp 2 biên bản vi phạm nội quy thực tế (Nhắc nhở tiếng ồn & vệ sinh)")

        # ----------------------------------------------------------------------
        # 10. YÊU CẦU BÁO HỎNG (SERVICE TICKETS)
        # ----------------------------------------------------------------------
        if not ServiceTicket.query.first():
            t1 = ServiceTicket(
                room_id=rooms_dict["101"].id,
                tenant_id=tenants_dict["tenant1"].id,
                category="repair",
                title="Dàn lạnh máy lạnh Daikin bị rỉ giọt nước",
                description="Máy lạnh chạy khoảng 30 phút thì có nước nhỏ giọt xuống bàn làm việc. Nhờ ban quản lý cho thợ qua kiểm tra giúp em.",
                priority="high",
                status="resolved",
                repair_cost=150000.0
            )
            t2 = ServiceTicket(
                room_id=rooms_dict["201"].id,
                tenant_id=tenants_dict["tenant3"].id,
                category="repair",
                title="Vòi xịt vệ sinh phòng tắm bị rỉ nước ở ren nối",
                description="Khớp nối dây kim loại bị rỉ nước liên tục làm ướt sàn nhà vệ sinh.",
                priority="medium",
                status="in_progress"
            )
            t3 = ServiceTicket(
                room_id=rooms_dict["102"].id,
                tenant_id=tenants_dict["tenant2"].id,
                category="repair",
                title="Bóng đèn Led tuýp ban công bị chớp nháy",
                description="Bật công tắc ban công đèn nhấp nháy liên tục không sáng rõ.",
                priority="low",
                status="pending"
            )
            db.session.add_all([t1, t2, t3])
            print("  ✓ Đã nạp 3 phiếu yêu cầu bảo trì / sửa chữa thực tế")

        # ----------------------------------------------------------------------
        # 11. BẢNG TIN TÒA NHÀ (BULLETIN ANNOUNCEMENTS)
        # ----------------------------------------------------------------------
        if not BulletinAnnouncement.query.first():
            b1 = BulletinAnnouncement(
                building_id=building.id,
                author_id=landlord.id,
                title="Thông báo súc rửa bể nước ngầm & bể mái định kỳ",
                content="Ban quản lý tòa nhà sẽ tiến hành thau rửa bể nước sinh hoạt vào Thứ Bảy (05/10/2026) từ 08:30 đến 11:30 sáng. Trong thời gian này sẽ tạm ngắt nước cục bộ. Kính đề nghị cư dân tích trữ nước sinh hoạt trước.",
                priority="important",
                effective_date=date(2026, 10, 5)
            )
            b2 = BulletinAnnouncement(
                building_id=building.id,
                author_id=landlord.id,
                title="Quy định an toàn PCCC & sạc xe máy điện tại hầm xe",
                content="Theo chỉ đạo PCCC địa phương, cư dân chỉ được sạc xe điện tại khu vực ổ cắm có trang bị Aptomat tự ngắt riêng tại vách hầm phía Đông. Nghiêm cấm câu mắc dây sạc tự chế qua đêm.",
                priority="emergency",
                effective_date=date(2026, 10, 1)
            )
            b3 = BulletinAnnouncement(
                building_id=building.id,
                author_id=landlord.id,
                title="Lịch thu gom rác sinh hoạt và tổng vệ sinh hành lang",
                content="Thời gian thu gom rác hàng ngày là từ 18:00 đến 19:30. Cư dân vui lòng buộc kín miệng túi rác và mang trực tiếp xuống thùng rác chung tại tầng trệt, không để rác ở hành lang.",
                priority="normal",
                effective_date=date(2026, 9, 20)
            )
            db.session.add_all([b1, b2, b3])
            print("  ✓ Đã nạp 3 thông báo bảng tin tòa nhà chân thực")

        # ----------------------------------------------------------------------
        # 12. CHI PHÍ VẬN HÀNH TÒA NHÀ (OPEX EXPENSES)
        # ----------------------------------------------------------------------
        if not Expense.query.first():
            expenses_list = [
                Expense(
                    building_id=building.id,
                    recorded_by=landlord.id,
                    expense_category="common_electricity",
                    title="Tiền điện chiếu sáng hành lang, thang máy và máy bơm T09/2026 - EVN HCMC",
                    amount=1450000.0,
                    expense_date=date(2026, 9, 28)
                ),
                Expense(
                    building_id=building.id,
                    recorded_by=landlord.id,
                    expense_category="water",
                    title="Hóa đơn nước sinh hoạt khối dùng chung Sawaco T09/2026",
                    amount=380000.0,
                    expense_date=date(2026, 9, 29)
                ),
                Expense(
                    building_id=building.id,
                    recorded_by=landlord.id,
                    expense_category="internet",
                    title="Gói cước cáp quang Viettel NetDoanhNghiep 500Mbps T09/2026",
                    amount=440000.0,
                    expense_date=date(2026, 9, 25)
                ),
                Expense(
                    building_id=building.id,
                    recorded_by=landlord.id,
                    expense_category="cleaning",
                    title="Dịch vụ thu gom rác sinh hoạt và lau sàn hành lang 3 lần/tuần T09/2026",
                    amount=600000.0,
                    expense_date=date(2026, 9, 30)
                )
            ]
            db.session.add_all(expenses_list)
            print("  ✓ Đã nạp 4 hóa đơn chi phí vận hành OpEx thực tế")

        db.session.commit()
        print("\n🎉 TOÀN BỘ DỮ LIỆU THỰC TẾ (REAL-WORLD DATASET) ĐÃ ĐƯỢC NẠP THÀNH CÔNG 100%!")


if __name__ == "__main__":
    seed_real_data()
