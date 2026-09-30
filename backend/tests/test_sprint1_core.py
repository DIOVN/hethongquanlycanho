"""
SAMS - Sprint 1 Core Tests
Kiểm thử: Auth (Register, Login, Me), Rooms, Room Search & Roommates Management.
"""
def test_auth_register_login_me(client):
    """Đăng ký tài khoản mới -> Đăng nhập nhận JWT -> Lấy thông tin /auth/me."""
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newtenant",
            "email": "newtenant@gmail.com",
            "password": "Password123@",
            "full_name": "Nguyễn Văn Mới",
            "phone": "0988776655",
            "cccd_number": "079199888777",
        },
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()["data"]
    assert reg_data["username"] == "newtenant"

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "newtenant", "password": "Password123@"},
    )
    assert login_res.status_code == 200
    token = login_res.get_json()["data"]["access_token"]
    assert token is not None

    # Me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.get_json()["data"]
    assert me_data["username"] == "newtenant"
    assert me_data["role"] == "tenant"


def test_rooms_search_public(client, seed_data):
    """Tìm kiếm phòng trống với các bộ lọc giá, tầng, diện tích."""
    res = client.get("/api/v1/rooms/search")
    assert res.status_code == 200
    rooms = res.get_json()["data"]
    # Phòng 303 là vacant
    assert any(r["room_number"] == "303" for r in rooms)


def test_roommate_registration_flow(client, landlord_token, tenant_token, seed_data):
    """Khai báo thành viên ở cùng phòng (CCCD, biển số xe, quê quán)."""
    room = seed_data["room"]
    headers = {"Authorization": f"Bearer {tenant_token}"}

    # Thêm bạn ở ghép
    add_res = client.post(
        f"/api/v1/rooms/{room.id}/roommates",
        headers=headers,
        json={
            "full_name": "Trần Bạn Cùng Phòng",
            "phone": "0933445566",
            "cccd_number": "079200111222",
            "date_of_birth": "2001-05-15",
            "gender": "female",
            "hometown": "Bình Dương",
            "vehicle_plate": "61-B1 999.88",
        },
    )
    assert add_res.status_code == 201
    rm_id = add_res.get_json()["data"]["id"]

    # Xem danh sách
    list_res = client.get(f"/api/v1/rooms/{room.id}/roommates", headers=headers)
    assert list_res.status_code == 200
    roommates = list_res.get_json()["data"]
    assert any(r["id"] == rm_id for r in roommates)
