# app.py
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# load .env
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# import DB and models
from models import db
from models.user_model import User        # patients stored here
from models.doctor_model import Doctor
from models.driver_model import Driver
from models.hospital_model import Hospital

# init DB
db.init_app(app)
with app.app_context():
    db.create_all()


# -------------------------------
# Basic site routes
# -------------------------------
@app.route('/')
def language_selection():
    return render_template('language_selection.html')


@app.route('/set-language/<lang>')
def set_language(lang):
    session['language'] = lang
    return redirect(url_for('login_choice'))


@app.route('/login')
def login_choice():
    return render_template('login_choice.html')


# -------------------------------
# Patient: register + login
# -------------------------------
@app.route('/register/patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash("Please fill all fields")
            return redirect(url_for('register_patient'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for('register_patient'))

        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed, role='patient')
        db.session.add(user)
        db.session.commit()
        flash("Patient registered. Please login.")
        return redirect(url_for('login_patient'))

    return render_template('register_patient.html')


@app.route('/login/patient', methods=['GET', 'POST'])
def login_patient():
    # ✅ If already logged in as patient, skip login page
    if 'user_email' in session and session.get('user_role') == 'patient':
        return redirect(url_for('patient_symptoms'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email, role='patient').first()
        if user and check_password_hash(user.password, password):
            session['user_email'] = user.email
            session['user_role'] = 'patient'
            flash("Logged in as patient")
            return redirect(url_for('patient_symptoms'))
        flash("Invalid credentials")
        return redirect(url_for('login_patient'))

    return render_template('login_patient.html')



# -------------------------------
# Doctor: register + login
# -------------------------------
@app.route('/register/doctor', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        specialization = request.form.get('specialization', '').strip()
        if not (name and email and password and specialization):
            flash("Please fill all fields")
            return redirect(url_for('register_doctor'))

        if Doctor.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for('register_doctor'))

        hashed = generate_password_hash(password)
        doc = Doctor(name=name, email=email, password=hashed, specialization=specialization)
        db.session.add(doc)
        db.session.commit()
        flash("Doctor registered. Please login.")
        return redirect(url_for('login_doctor'))

    return render_template('register_doctor.html')


@app.route('/login/doctor', methods=['GET', 'POST'])
def login_doctor():
    if 'user_email' in session and session.get('user_role') == 'doctor':
     return redirect(url_for('doctor_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        doc = Doctor.query.filter_by(email=email).first()
        if doc and check_password_hash(doc.password, password):
            session['user_email'] = doc.email
            session['user_role'] = 'doctor'
            flash("Logged in as doctor")
            return redirect(url_for('doctor_dashboard'))
        flash("Invalid credentials")
        return redirect(url_for('login_doctor'))
    return render_template('login_doctor.html')


# Doctor dashboard (placeholder)
@app.route('/doctor/dashboard')
def doctor_dashboard():
    if session.get('user_role') != 'doctor':
        return redirect(url_for('login_doctor'))
    doc = Doctor.query.filter_by(email=session.get('user_email')).first()
    return render_template('doctor_dashboard.html', doctor=doc)


# -------------------------------
# Driver (Ambulance): register + login + dashboard
# -------------------------------
@app.route('/register/driver', methods=['GET', 'POST'])
def register_driver():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        if not (name and email and password):
            flash("Please fill all required fields")
            return redirect(url_for('register_driver'))

        if Driver.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for('register_driver'))

        hashed = generate_password_hash(password)
        driver = Driver(name=name, email=email, phone=phone, password=hashed, is_available=False)
        db.session.add(driver)
        db.session.commit()
        flash("Driver registered. Please login.")
        return redirect(url_for('login_driver'))

    return render_template('register_driver.html')


@app.route('/login/driver', methods=['GET', 'POST'])
def login_driver():
    if 'user_email' in session and session.get('user_role') == 'driver':
     return redirect(url_for('driver_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        driver = Driver.query.filter_by(email=email).first()
        if driver and check_password_hash(driver.password, password):
            session['user_email'] = driver.email
            session['user_role'] = 'driver'
            flash("Logged in as driver")
            return redirect(url_for('driver_dashboard'))
        flash("Invalid credentials")
        return redirect(url_for('login_driver'))
    return render_template('login_driver.html')


@app.route('/driver/dashboard', methods=['GET', 'POST'])
def driver_dashboard():
    # only for logged-in drivers
    if session.get('user_role') != 'driver' or 'user_email' not in session:
        return redirect(url_for('login_driver'))
    driver = Driver.query.filter_by(email=session.get('user_email')).first()
    if not driver:
        flash("Driver not found")
        return redirect(url_for('login_driver'))

    # Toggle availability via POST
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'toggle':
            driver.is_available = not driver.is_available
            db.session.commit()
            flash(f"Availability set to {driver.is_available}")
        # add accept/reject logic later (for real SOS assignment)
    return render_template('driver_dashboard.html', driver=driver)


# -------------------------------
# Logout
# -------------------------------
@app.route('/logout')
def logout():
    # If driver is logging out, set them unavailable
    if session.get('user_role') == 'driver' and 'user_email' in session:
        driver = Driver.query.filter_by(email=session['user_email']).first()
        if driver:
            driver.is_available = False
            db.session.commit()

    session.clear()
    flash("Logged out")
    return redirect(url_for('language_selection'))



# -------------------------------
# SOS API Route (unchanged)
# -------------------------------
@app.route('/api/send-sos', methods=['POST'])
def api_send_sos():
    data = request.json or request.form
    lat = data.get("lat")
    lon = data.get("lon")

    if not lat or not lon:
        return jsonify({"ok": False, "msg": "Missing location"})

    # Pick first available driver
    driver = Driver.query.filter_by(is_available=True).first()
    if not driver:
        return jsonify({"ok": False, "msg": "No available driver"})

    # Build OpenStreetMap link
    location_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"
    subject = "🚨 SOS Alert"
    body = (
        f"A patient needs urgent help!\n\n"
        f"Location: {location_url}\n\n"
        f"Driver Contact: {driver.phone}"
    )

    from services.notifications import send_email_notification
    success = send_email_notification(driver.email, subject, body)

    if success:
        return jsonify({"ok": True, "to": driver.email})
    else:
        return jsonify({"ok": False, "msg": "Failed to send email"})


# -------------------------------
# Keep other pages (symptoms/hospitals) as before
# -------------------------------
@app.route('/patient/symptoms', methods=['GET', 'POST'])
def patient_symptoms():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '')
        return redirect(url_for('symptom_processing', symptoms=symptoms))
    return render_template('patient_symptoms.html')


@app.route('/symptom-processing')
def symptom_processing():
    return render_template('symptom_processing.html')


@app.route('/hospitals')
def hospital_list():
    hospitals = Hospital.query.all()
    return render_template('hospital_list.html', hospitals=hospitals)


@app.route('/hospital/<int:hospital_id>')
def hospital_detail(hospital_id):
    h = Hospital.query.get_or_404(hospital_id)
    return render_template('hospital_detail.html', hospital=h)


@app.route('/map/<int:hospital_id>')
def map_view(hospital_id):
    h = Hospital.query.get_or_404(hospital_id)
    return render_template('map_view.html', hospital=h)


@app.route('/emergency')
def emergency():
    return render_template('emergency.html')


# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
