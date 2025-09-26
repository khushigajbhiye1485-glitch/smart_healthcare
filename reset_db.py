# reset_db.py
from app import app, db
from models.user_model import User
from models.doctor_model import Doctor
from models.driver_model import Driver
from models.hospital_model import Hospital

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()

    print("Creating all tables fresh...")
    db.create_all()

    print("✅ Database has been reset successfully!")
