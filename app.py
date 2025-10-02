# app.py
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.distance import geodesic
import re # Added for the parse_coord function

# Services
from services.ai_recommender import analyze_symptoms
from services.symptom_mapping import match_specialty
from services.notifications import send_email_notification

# Models
from models import db
from models.user_model import User
from models.doctor_model import Doctor
from models.driver_model import Driver
from models.hospital_model import Hospital
from models.admin_model import Admin

# Load .env
load_dotenv()

# App config
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "devkey")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init DB
db.init_app(app)
with app.app_context():
    db.create_all()

# -------------------------------
# UTILITY FUNCTIONS (NEW)
# -------------------------------
def parse_coord(val):
    """
    Robustly parse many coordinate string formats into a float.
    Returns float or None.
    Examples handled:
      "20.93", "20.93 N", "20.93° N", "20.930743", "20.93°N", "20.93 N, 77.7 E"
    """
    if val is None:
        return None
    if isinstance(val, (float, int)):
        return float(val)
    s = str(val).strip()
    # quick empty check
    if s == "":
        return None
    # remove degree/minute/second symbols and direction letters & commas
    s = s.replace('°',' ').replace('º',' ').replace("'", " ").replace('"', " ")
    s = re.sub(r'[NSEWnsew,]', '', s)
    # remove any remaining non-numeric (except +,- and .)
    # but first replace comma decimals (if exist) with dot (rare)
    s = s.replace(',', '.')
    # strip spaces
    s = re.sub(r'\s+', '', s)
    # extract first numeric token
    m = re.search(r'[-+]?\d+\.\d+|[-+]?\d+', s)
    if not m:
        return None
    try:
        return float(m.group())
    except:
        return None
# -------------------------------
# Basic site routes
# -------------------------------
@app.route("/")
def language_selection():
    return render_template("language_selection.html")

@app.route("/set-language/<lang>")
def set_language(lang):
    session["language"] = lang
    return redirect(url_for("login_choice"))

@app.route("/login")
def login_choice():
    return render_template("login_choice.html")

# -------------------------------
# PATIENT: Register + Login
# -------------------------------
@app.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not (name and email and password):
            flash("Please fill all fields")
            return redirect(url_for("register_patient"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register_patient"))

        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed, role="patient")
        db.session.add(user)
        db.session.commit()
        flash("Patient registered. Please login.")
        return redirect(url_for("login_patient"))

    return render_template("register_patient.html")

@app.route("/login/patient", methods=["GET", "POST"])
def login_patient():
    if "user_email" in session and session.get("user_role") == "patient":
        return redirect(url_for("patient_symptoms"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email, role="patient").first()
        if user and check_password_hash(user.password, password):
            session["user_email"] = user.email
            session["user_role"] = "patient"
            flash("Logged in as patient")
            return redirect(url_for("patient_symptoms"))
        flash("Invalid credentials")
        return redirect(url_for("login_patient"))

    return render_template("login_patient.html")

# -------------------------------
# DOCTOR: Register + Login
# -------------------------------
@app.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        specialization = request.form.get("specialization", "").strip()

        if not (name and email and password and specialization):
            flash("Please fill all fields")
            return redirect(url_for("register_doctor"))

        if Doctor.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register_doctor"))

        hashed = generate_password_hash(password)
        doc = Doctor(name=name, email=email, password=hashed, specialization=specialization)
        db.session.add(doc)
        db.session.commit()
        flash("Doctor registered. Please login.")
        return redirect(url_for("login_doctor"))

    return render_template("register_doctor.html")

@app.route("/login/doctor", methods=["GET", "POST"])
def login_doctor():
    if "user_email" in session and session.get("user_role") == "doctor":
        return redirect(url_for("doctor_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        doc = Doctor.query.filter_by(email=email).first()
        if doc and check_password_hash(doc.password, password):
            session["user_email"] = doc.email
            session["user_role"] = "doctor"
            flash("Logged in as doctor")
            return redirect(url_for("doctor_dashboard"))
        flash("Invalid credentials")
        return redirect(url_for("login_doctor"))
    return render_template("login_doctor.html")

@app.route("/doctor/dashboard")
def doctor_dashboard():
    if session.get("user_role") != "doctor":
        return redirect(url_for("login_doctor"))
    doc = Doctor.query.filter_by(email=session.get("user_email")).first()
    return render_template("doctor_dashboard.html", doctor=doc)

# -------------------------------
# DRIVER (Ambulance): Register + Login
# -------------------------------
@app.route("/register/driver", methods=["GET", "POST"])
def register_driver():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not (name and email and password):
            flash("Please fill all required fields")
            return redirect(url_for("register_driver"))

        if Driver.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register_driver"))

        hashed = generate_password_hash(password)
        driver = Driver(name=name, email=email, phone=phone, password=hashed, is_available=False)
        db.session.add(driver)
        db.session.commit()
        flash("Driver registered. Please login.")
        return redirect(url_for("login_driver"))

    return render_template("register_driver.html")

@app.route("/login/driver", methods=["GET", "POST"])
def login_driver():
    if "user_email" in session and session.get("user_role") == "driver":
        return redirect(url_for("driver_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        driver = Driver.query.filter_by(email=email).first()
        if driver and check_password_hash(driver.password, password):
            session["user_email"] = driver.email
            session["user_role"] = "driver"
            flash("Logged in as driver")
            return redirect(url_for("driver_dashboard"))
        flash("Invalid credentials")
        return redirect(url_for("login_driver"))
    return render_template("login_driver.html")

@app.route("/driver/dashboard", methods=["GET", "POST"])
def driver_dashboard():
    if session.get("user_role") != "driver" or "user_email" not in session:
        return redirect(url_for("login_driver"))

    driver = Driver.query.filter_by(email=session.get("user_email")).first()
    if not driver:
        flash("Driver not found")
        return redirect(url_for("login_driver"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "toggle":
            driver.is_available = not driver.is_available
            db.session.commit()
            flash(f"Availability set to {driver.is_available}")
    return render_template("driver_dashboard.html", driver=driver)

# -------------------------------
# LOGOUT
# -------------------------------
@app.route("/logout")
def logout():
    if session.get("user_role") == "driver" and "user_email" in session:
        driver = Driver.query.filter_by(email=session["user_email"]).first()
        if driver:
            driver.is_available = False
            db.session.commit()

    session.clear()
    flash("Logged out")
    return redirect(url_for("language_selection"))

# -------------------------------
# ADMIN ROUTES
# -------------------------------
@app.route("/login/admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        admin = Admin.query.filter_by(email=email).first()
        # NOTE: Assuming Admin model has check_password method
        if admin and admin.check_password(password): 
            session["user_role"] = "admin"
            session["user_email"] = admin.email
            flash("Logged in as Admin", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login_admin"))

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("user_role") != "admin":
        flash("Unauthorized", "danger")
        return redirect(url_for("login_admin"))
    return render_template("admin_dashboard.html")

@app.route("/admin/hospitals")
def admin_hospitals():
    if session.get("user_role") != "admin":
        flash("Unauthorized", "danger")
        return redirect(url_for("login_admin"))

    hospitals = Hospital.query.all()
    return render_template("admin_hospitals.html", hospitals=hospitals)

@app.route("/admin/hospitals/add", methods=["GET", "POST"])
def add_hospital():
    if session.get("user_role") != "admin":
        flash("Unauthorized", "danger")
        return redirect(url_for("login_admin"))

    if request.method == "POST":
        name = request.form.get("name")
        specialization = request.form.get("specialization")
        machines = request.form.get("machines")
        # Use the robust parser for admin input as well
        latitude = parse_coord(request.form.get("latitude"))
        longitude = parse_coord(request.form.get("longitude"))

        if latitude is None or longitude is None:
            flash("Invalid Latitude or Longitude format.", "danger")
            return redirect(url_for("add_hospital"))

        new_h = Hospital(name=name, specialization=specialization, machines=machines,
                         latitude=latitude, longitude=longitude)
        db.session.add(new_h)
        db.session.commit()
        flash("Hospital added successfully!", "success")
        return redirect(url_for("admin_hospitals"))

    return render_template("admin_add_hospital.html")

@app.route("/admin/hospitals/edit/<int:hospital_id>", methods=["GET", "POST"])
def edit_hospital(hospital_id):
    if session.get("user_role") != "admin":
        flash("Unauthorized", "danger")
        return redirect(url_for("login_admin"))

    hospital = Hospital.query.get_or_404(hospital_id)

    if request.method == "POST":
        hospital.name = request.form.get("name")
        hospital.specialization = request.form.get("specialization")
        hospital.machines = request.form.get("machines")
        
        # Use the robust parser
        latitude = parse_coord(request.form.get("latitude"))
        longitude = parse_coord(request.form.get("longitude"))

        if latitude is None or longitude is None:
            flash("Invalid Latitude or Longitude format.", "danger")
            return redirect(url_for("edit_hospital", hospital_id=hospital_id))

        hospital.latitude = latitude
        hospital.longitude = longitude

        db.session.commit()
        flash("Hospital updated successfully!", "success")
        return redirect(url_for("admin_hospitals"))

    return render_template("admin_edit_hospital.html", hospital=hospital)

@app.route("/admin/hospitals/delete/<int:hospital_id>", methods=["POST"])
def delete_hospital(hospital_id):
    if session.get("user_role") != "admin":
        flash("Unauthorized", "danger")
        return redirect(url_for("login_admin"))

    hospital = Hospital.query.get_or_404(hospital_id)
    db.session.delete(hospital)
    db.session.commit()
    flash("Hospital deleted successfully!", "success")
    return redirect(url_for("admin_hospitals"))

# -------------------------------
# SOS API
# -------------------------------
@app.route("/api/send-sos", methods=["POST"])
def api_send_sos():
    data = request.json or request.form
    # Use the robust parser for coordinates
    lat = parse_coord(data.get("lat"))
    lon = parse_coord(data.get("lon"))

    if lat is None or lon is None:
        return jsonify({"ok": False, "msg": "Missing or invalid location"})

    driver = Driver.query.filter_by(is_available=True).first()
    if not driver:
        return jsonify({"ok": False, "msg": "No available driver"})

    # Ensure driver coordinates are valid if you plan to use them (though not in original logic)
    # location_url uses the original patient lat/lon
    location_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"
    subject = "🚨 SOS Alert"
    body = f"A patient needs urgent help!\n\nLocation: {location_url}\n\nDriver Contact: {driver.phone}"

    success = send_email_notification(driver.email, subject, body)
    if success:
        return jsonify({"ok": True, "to": driver.email})
    else:
        return jsonify({"ok": False, "msg": "Failed to send email"})

# -------------------------------
# Patient Symptom Input (UPDATED)
# -------------------------------
@app.route('/patient/symptoms', methods=['GET', 'POST'])
def patient_symptoms():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '').strip()
        
        # Accept lat/lon from form (hidden inputs filled by JS) OR manual inputs
        lat = request.form.get('lat') or request.form.get('latitude') or request.form.get('patient_lat')
        lon = request.form.get('lon') or request.form.get('longitude') or request.form.get('patient_lon')

        plat = parse_coord(lat)
        plon = parse_coord(lon)

        if plat is not None and plon is not None:
            # Save valid coords to session (NEW)
            session['patient_lat'] = plat
            session['patient_lon'] = plon
            current_app.logger.debug("Saved patient location: %s, %s", plat, plon)
        else:
            # Clear stored location if invalid (NEW)
            session.pop('patient_lat', None)
            session.pop('patient_lon', None)
            flash("Note: We couldn't get your location, so distances won't be calculated.", "info")

        # Map symptoms -> specialization
        specialization = match_specialty(symptoms)

        # Redirect to recommendation page (using query params, NOT POST)
        return redirect(url_for('recommend', specialization=specialization, symptoms=symptoms))
    return render_template('patient_symptoms.html')

# -------------------------------
# Recommendation Route (UPDATED/REPLACED)
# -------------------------------
@app.route('/recommend')
def recommend():
    specialization = request.args.get('specialization', '').strip()
    symptoms = request.args.get('symptoms', '').strip()

    # Get patient coords: session preferred, fallback to query params
    plat = parse_coord(session.get('patient_lat')) or parse_coord(request.args.get('lat'))
    plon = parse_coord(session.get('patient_lon')) or parse_coord(request.args.get('lon'))

    # Query hospitals (if specialization empty, return all)
    query = Hospital.query
    if specialization:
        query = query.filter(
            (Hospital.specialization.ilike(f"%{specialization}%")) |
            (Hospital.machines.ilike(f"%{specialization}%"))
        )
    hospitals = query.all()

    results = []
    for h in hospitals:
        hlat = parse_coord(h.latitude)
        hlon = parse_coord(h.longitude)

        distance_km = None
        # Calculate distance only if all 4 coordinates are valid
        if plat is not None and plon is not None and hlat is not None and hlon is not None:
            try:
                distance_km = geodesic((plat, plon), (hlat, hlon)).km
            except Exception as e:
                current_app.logger.warning("Distance calc failed for hospital %s: %s", getattr(h,'id',None), str(e))
                distance_km = None

        results.append({
            "id": h.id,
            "name": h.name,
            "specialization": h.specialization,
            "machines": h.machines,
            "latitude": hlat,
            "longitude": hlon,
            "distance": round(distance_km, 2) if distance_km is not None else None
        })

    # Sort: None distances go to the end
    results_sorted = sorted(results, key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))

    return render_template('recommend.html',
                           hospitals=results_sorted,
                           specialization=specialization,
                           symptoms=symptoms,
                           patient_lat=plat,
                           patient_lon=plon)

# -------------------------------
# HOSPITAL LIST + MAP (UPDATED hospital_list and map_view)
# -------------------------------
@app.route("/hospitals")
def hospital_list():
    # Use the robust parser on session data
    patient_lat = parse_coord(session.get("patient_lat"))
    patient_lon = parse_coord(session.get("patient_lon"))
    hospitals = Hospital.query.all()

    hospitals_with_distance = []
    for h in hospitals:
        # Use robust parser for hospital coords
        hlat = parse_coord(h.latitude)
        hlon = parse_coord(h.longitude)
        
        h_dict = h.__dict__ # Use dict for easy modification
        h_dict["distance"] = None

        if patient_lat is not None and patient_lon is not None and hlat is not None and hlon is not None:
            try:
                distance_km = geodesic((patient_lat, patient_lon), (hlat, hlon)).km
                h_dict["distance"] = round(distance_km, 2)
            except:
                pass # distance remains None

        hospitals_with_distance.append(h_dict)


    # Sort: None distances go to the end
    hospitals_sorted = sorted(hospitals_with_distance, key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
    
    # Note: If you want to use the SQLAlchemy objects directly instead of dicts, 
    # you'd need to ensure 'distance' is a transient property or use a structure like 'results' in /recommend.
    # For simplicity, returning the sorted list of dicts.

    return render_template("hospital_list.html", hospitals=hospitals_sorted)

@app.route("/hospital/<int:hospital_id>")
def hospital_detail(hospital_id):
    h = Hospital.query.get_or_404(hospital_id)
    return render_template("hospital_detail.html", hospital=h)

@app.route('/map/<int:hospital_id>')
def map_view(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)

    # 1. Allow overriding session via URL query
    qlat = request.args.get('lat')
    qlon = request.args.get('lon')
    
    if qlat and qlon:
        plat = parse_coord(qlat)
        plon = parse_coord(qlon)
        if plat is not None and plon is not None:
            # Optionally save to session if coming from a specific link
            session['patient_lat'] = plat
            session['patient_lon'] = plon
        
    # 2. Get the final patient coordinates from the session
    patient_lat = parse_coord(session.get('patient_lat'))
    patient_lon = parse_coord(session.get('patient_lon'))
    
    return render_template(
        "map_view.html",
        hospital=hospital,
        patient_lat=patient_lat,
        patient_lon=patient_lon
    )

# -------------------------------
@app.route("/emergency")
def emergency():
    return render_template("emergency.html")

# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)