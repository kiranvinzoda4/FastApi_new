import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
import uuid
from faker import Faker
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    AdminUserModel, CustomerModel, DeliveryGuyModel, VegetableModel,
    OrderModel, OrderItemModel, DeliveryGuyRatingModel, VegetableRatingModel,
    UnitTypeEnum, OrderStatusEnum,
    UserAddressesModel
)

fake = Faker()

# generate_order_code function removed - use the one from utils.py

def generate_indian_phone():
    return f"{random.choice(['6', '7', '8', '9'])}{fake.random_number(digits=9, fix_len=True)}"

def seed_data(db: Session):
    print("🔄 Seeding data...")

    # 1. Admins
    for _ in range(3):
        try:
            from app.libs.utils import create_password, generate_order_code
            db.add(AdminUserModel(
                id=str(uuid.uuid4()),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.user_name() + "@gmail.com",
                phone=generate_indian_phone(),
                password=create_password("TempPass123!"),  # Use environment variable in production
                otp=None
            ))
        except Exception as e:
            print(f"❌ Failed to create admin: {e}")

    # 2. Customers + Addresses
    customers = []
    for _ in range(10):
        customer_id = str(uuid.uuid4())
        customer = CustomerModel(
            id=customer_id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.user_name() + "@gmail.com",
            phone=generate_indian_phone(),
            password=create_password("TempPass123!"),
            otp=None
        )
        db.add(customer)

        address = UserAddressesModel(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            address_line_1=fake.street_address(),
            address_line_2=fake.secondary_address(),
            city=fake.city(),
            state=fake.state(),
            pincode=str(fake.random_number(digits=6, fix_len=True)),
            landmark=fake.word()
        )
        db.add(address)
        customers.append((customer, address))

    # 3. Delivery Guys
    delivery_guys = []
    for _ in range(5):
        guy = DeliveryGuyModel(
            id=str(uuid.uuid4()),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.user_name() + "@gmail.com",
            phone=generate_indian_phone(),
            aadhaar_number=str(fake.random_number(digits=12, fix_len=True)),
            pan_number=fake.bothify(text='?????####?'),
            address=fake.address(),
            password=create_password("TempPass123!"),
            otp=None
        )
        db.add(guy)
        delivery_guys.append(guy)

    # 4. Vegetables
    vegetables = []
    for _ in range(10):
        veg = VegetableModel(
            id=str(uuid.uuid4()),
            name=fake.word().capitalize(),
            description=fake.sentence(),
            price=round(random.uniform(10, 200), 2),
            quantity=random.randint(10, 100),
            unit_type=random.choice(list(UnitTypeEnum)),
            image_url="https://via.placeholder.com/150"
        )
        db.add(veg)
        vegetables.append(veg)

    db.commit()

    # 5. Orders & Items
    for _ in range(20):
        customer, address = random.choice(customers)
        delivery_guy = random.choice(delivery_guys)
        order = OrderModel(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            address_id=address.id,
            code=generate_order_code(),
            delivery_date=fake.future_date(),
            total_amount=0,
            payment_type='COD',
            status=random.choice(list(OrderStatusEnum)),
            delivery_guy_id=delivery_guy.id
        )
        db.add(order)
        db.commit()

        total = 0
        for _ in range(random.randint(1, 3)):
            veg = random.choice(vegetables)
            qty = random.randint(1, 5)
            price = float(veg.price)
            db.add(OrderItemModel(
                id=str(uuid.uuid4()),
                order_id=order.id,
                vegetable_id=veg.id,
                quantity=qty,
                price=price
            ))
            total += qty * price

        order.total_amount = round(total, 2)
        db.commit()

    # 6. Ratings
    for _ in range(15):
        db.add(DeliveryGuyRatingModel(
            id=str(uuid.uuid4()),
            customer_id=random.choice(customers)[0].id,
            delivery_guy_id=random.choice(delivery_guys).id,
            rating=random.randint(1, 5),
            comment=fake.sentence()
        ))

    for _ in range(15):
        db.add(VegetableRatingModel(
            id=str(uuid.uuid4()),
            customer_id=random.choice(customers)[0].id,
            vegetable_id=random.choice(vegetables).id,
            rating=random.randint(1, 5),
            comment=fake.sentence()
        ))

    db.commit()
    print("✅ Seeder completed.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
