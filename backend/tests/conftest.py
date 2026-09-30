"""
SAMS - Pytest Configuration & Test Fixtures
"""
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.room import Building, Room
from app.models.contract import Contract
from app.services.auth_service import AuthService
from datetime import date, timedelta


@pytest.fixture
def app():
    """Tạo test app với in-memory database."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client HTTP."""
    return app.test_client()


@pytest.fixture
def seed_data(app):
    """Seed building, rooms, landlord, and tenant."""
    # 1. Landlord user
    landlord = User(
        username="landlord1",
        email="quocdung.pham@gmail.com",
        password_hash=AuthService.hash_password("Pass123@"),
        full_name="Phạm Quốc Dũng",
        role="landlord",
        phone="0903123456",
        cccd_number="079085001234",
    )
    # 2. Tenant user
    tenant = User(
        username="tenant1",
        email="maianh.nguyen98@gmail.com",
        password_hash=AuthService.hash_password("Pass123@"),
        full_name="Nguyễn Mai Anh",
        role="tenant",
        phone="0918234567",
        cccd_number="038198004567",
    )
    db.session.add_all([landlord, tenant])
    db.session.commit()

    # 3. Building
    building = Building(
        name="Tòa nhà SAMS 1",
        address="123 Đường Điện Biên Phủ, Q. Bình Thạnh, TP.HCM",
        total_floors=5,
    )
    db.session.add(building)
    db.session.commit()

    # 4. Room 302
    room = Room(
        building_id=building.id,
        current_tenant_id=tenant.id,
        room_number="302",
        base_price=4500000.0,
        area_sqm=28.5,
        floor=3,
        status="occupied",
    )
    # Room 303 (vacant)
    vacant_room = Room(
        building_id=building.id,
        current_tenant_id=None,
        room_number="303",
        base_price=4200000.0,
        area_sqm=25.0,
        floor=3,
        status="vacant",
    )
    db.session.add_all([room, vacant_room])
    db.session.commit()

    # 5. Contract for room 302
    contract = Contract(
        room_id=room.id,
        tenant_id=tenant.id,
        start_date=date.today() - timedelta(days=60),
        end_date=date.today() + timedelta(days=305),
        monthly_rent=4500000.0,
        deposit_amount=4500000.0,
        status="active",
    )
    db.session.add(contract)
    db.session.commit()

    return {
        "landlord": landlord,
        "tenant": tenant,
        "building": building,
        "room": room,
        "vacant_room": vacant_room,
        "contract": contract,
    }


@pytest.fixture
def landlord_token(client, seed_data):
    """Lấy JWT token của Landlord."""
    res = client.post("/api/v1/auth/login", json={"username": "landlord1", "password": "Pass123@"})
    return res.get_json()["data"]["access_token"]


@pytest.fixture
def tenant_token(client, seed_data):
    """Lấy JWT token của Tenant."""
    res = client.post("/api/v1/auth/login", json={"username": "tenant1", "password": "Pass123@"})
    return res.get_json()["data"]["access_token"]
