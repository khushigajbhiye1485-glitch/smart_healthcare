from app import app, db
from models.driver_model import Driver

with app.app_context():
    db.drop_all()
    db.create_all()

    # ✅ Replace with your and your friends' real emails
    drivers = [
        Driver(name="Ambulance Driver 1", email="desianimator333@gmail.com", phone="9999999999", is_available=True),
        Driver(name="Ambulance Driver 2", email="yourfriend2@gmail.com", phone="8888888888", is_available=False)
    ]

    db.session.add_all(drivers)
    db.session.commit()
    print("✅ Drivers seeded successfully!")
