# seed_hospitals.py
from app import app, db
from models.hospital_model import Hospital

with app.app_context():
    db.drop_all()
    db.create_all()

    hospitals = [
        Hospital(
            name="City Heart Hospital",
            specialization="Cardiology",
            machines="ECG,MRI,CT",
            latitude=19.0760,
            longitude=72.8777
        ),
        Hospital(
            name="NeuroCare Clinic",
            specialization="Neurology",
            machines="EEG,CT",
            latitude=28.7041,
            longitude=77.1025
        ),
        Hospital(
            name="Bone & Joint Center",
            specialization="Orthopedics",
            machines="X-Ray,MRI",
            latitude=12.9716,
            longitude=77.5946
        ),
    ]

    db.session.add_all(hospitals)
    db.session.commit()
    print("✅ Hospitals seeded successfully!")
