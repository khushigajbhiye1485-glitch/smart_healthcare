from . import db

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    specialties = db.Column(db.String(300))   # e.g. "Cardiology"
    facilities = db.Column(db.String(500))    # e.g. "ICU, ECG"
    contact = db.Column(db.String(50))
