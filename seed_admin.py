# seed_admin.py
from app import app, db
from models.admin_model import Admin

with app.app_context():
    # create default admin
    if not Admin.query.filter_by(email="rajurkarvedant8@gmail.com").first():
        admin = Admin(email="rajurkarvedant8@gmail.com")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created: rajurkarvedant8@gmail.com / admin123")
    else:
        print("Admin already exists.")
