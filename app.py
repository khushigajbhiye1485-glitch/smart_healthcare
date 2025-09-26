# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
from flask import session

load_dotenv()

# create app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init DB
from models import db
from models.user_model import User
from models.hospital_model import Hospital
from models.driver_model import Driver   # ✅ new driver model

db.init_app(app)

with app.app_context():
    db.create_all()

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def language_selection():
    return render_template('language_selection.html')  # Page 1: languages + SOS

@app.route('/set-language/<lang>')
def set_language(lang):
    session['language'] = lang   # store selection
    return redirect(url_for('login_choice'))


@app.route('/login')
def login_choice():
    return render_template('login_choice.html')

@app.route('/login/patient', methods=['GET','POST'])
def login_patient():
    if request.method == 'POST':
        return redirect(url_for('patient_symptoms'))
    return render_template('login_patient.html')

@app.route('/patient/symptoms', methods=['GET','POST'])
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
# SOS API Route
# -------------------------------
@app.route('/api/send-sos', methods=['POST'])
def api_send_sos():
    """
    Handles SOS request from patient device.
    Expects 'lat' and 'lon' from frontend (JS geolocation).
    Sends email to the first available driver in DB.
    """
    data = request.json or request.form
    lat = data.get("lat")
    lon = data.get("lon")

    if not lat or not lon:
        return jsonify({"ok": False, "msg": "Missing location"})

    # Pick first available driver
    from models.driver_model import Driver
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
if __name__ == '__main__':
    app.run(debug=True)
