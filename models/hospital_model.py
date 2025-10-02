# models/hospital_model.py
from . import db

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)   # e.g. "Cardiology"
    machines = db.Column(db.String(250), nullable=True)          # comma-separated e.g. "MRI,CT,ECG"
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
