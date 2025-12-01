from sqlalchemy.orm import aliased
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
app.secret_key = "supersecretkey123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)


from datetime import datetime

class User(db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    experience = db.Column(db.Integer, nullable=True)

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    department = db.relationship("Department",back_populates="doctors")


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    
    doctors = db.relationship("User", back_populates="department")


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20)) 
    time = db.Column(db.String(50))
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='Booked', nullable=False) 
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'), nullable=True, unique=True)

class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    visit_type = db.Column(db.String(100))
    tests_done = db.Column(db.String(255))
    diagnosis = db.Column(db.String(255))
    prescription = db.Column(db.String(255))
    medicines = db.Column(db.String(255))
    prescribed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Medicine(db.Model):
    __tablename__ = 'medicines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    intake_time = db.Column(db.String(50), nullable=False)

class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    morning = db.Column(db.String(20), default="available")
    evening = db.Column(db.String(20), default="available")


@app.route('/')
def root():
    return render_template('root.html')

@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = "patient"

        user = User.query.filter(User.user_name == user_name, User.email == email).first()
        if user:
            return redirect(url_for('login'))

        new_user = User(user_name=user_name, email=email, password=password, role="patient")
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email, password=password).first()
        if user and user.role == "patient":
            session['name'] = user.user_name
            session['id'] = user.id
            session['role'] = user.role
            return redirect(url_for('patient_dash'))
        
        elif user and user.role == "doctor":
            session['name'] = user.user_name
            session['id'] = user.id
            session['role'] = user.role
            return redirect(url_for('doctor_dash'))
        
        elif user and user.role == "admin":
            session['name'] = user.user_name
            session['id'] = user.id
            session['role'] = user.role
            return redirect(url_for('admin_dash'))
        return render_template('login.html', error="you'ar new user go & signup first")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/patient_dash')
def patient_dash():
    departments = Department.query.all()

    appointments = Appointment.query.filter_by(patient_id=session.get("id")).all()

    formatted = []
    for appt in appointments:
        doctor = User.query.get(appt.doctor_id)
        dept = Department.query.get(doctor.department_id)

        formatted.append({
            "id": appt.id,
            "doctor_name": doctor.user_name,
            "department": dept.name,
            "date": appt.date,
            "time": appt.time
        })

    return render_template(
        "patient_dash.html",
        departments=departments,
        appointments=formatted
    )

@app.route('/patient/history')
def patient_history():

    patient_id = session.get('id')

    patient = User.query.get(patient_id)

    history = Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id)\
        .filter(Appointment.patient_id == patient_id).all()

    if history:
        appt = Appointment.query.get(history[0].appointment_id)
        doctor = User.query.get(appt.doctor_id)
        department = Department.query.get(doctor.department_id)
    else:
        doctor = None
        department = None

    return render_template(
        "patient/history.html",
        patient=patient,
        doctor=doctor,
        department=department,
        history=history
    )

@app.route('/doctor/availability', methods=['GET'])
def doctor_availability():
    if session.get("role") != "doctor":
        return redirect(url_for('login'))

    doctor_id = session["id"]

    from datetime import datetime, timedelta
    days = [(datetime.now() + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(7)]

    availability = {}
    for d in days:
        rec = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=d).first()
        availability[d] = rec

    return render_template(
        "doctor/doctor_availability.html",
        days=days,
        availability=availability
    )


@app.route('/doctor/<int:doctor_id>/availability')
def doctor_availability_patient(doctor_id):

    doctor = User.query.get_or_404(doctor_id)

    from datetime import datetime, timedelta
    days = [(datetime.now() + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(7)]

    availability = {}
    for d in days:
        rec = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=d).first()
        availability[d] = rec

    booked_morning = {}
    booked_evening = {}

    for d in days:
        booked_morning[d] = Appointment.query.filter_by(
            doctor_id=doctor_id, date=d, time="morning"
        ).first() is not None

        booked_evening[d] = Appointment.query.filter_by(
            doctor_id=doctor_id, date=d, time="evening"
        ).first() is not None

    return render_template(
        "patient/doctor_availability.html",
        doctor=doctor,
        days=days,
        availability=availability,
        booked_morning=booked_morning,
        booked_evening=booked_evening
    )




@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    doctor_id = request.form.get("doctor_id")
    date = request.form.get("date")
    time = request.form.get("time")
    patient_id = session.get("id")

    av = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=date).first()

    if not av:
        return "Doctor has not provided availability!", 400

    if time == "morning" and av.morning != "available":
        return "This morning slot is not available!", 400

    if time == "evening" and av.evening != "available":
        return "This evening slot is not available!", 400

    exists = Appointment.query.filter_by(
        doctor_id=doctor_id, date=date, time=time
    ).first()

    if exists:
        return "Slot already booked!", 400

    new_appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        date=date,
        time=time,
        status="Booked"
    )

    db.session.add(new_appointment)
    db.session.commit()

    return redirect(url_for('patient_dash'))



@app.route('/doctor/<int:doctor_id>/details')
def doctor_details(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    department = Department.query.get(doctor.department_id)
    
    return render_template(
        'patient/doctor_details.html',
        doctor=doctor,
        department=department
    )


@app.route("/doctor/toggle_slot", methods=["POST"])
def toggle_slot():
    doctor_id = session["id"]
    date = request.form.get("date")
    time = request.form.get("time") 
    record = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=date).first()

    if not record:
        record = DoctorAvailability(doctor_id=doctor_id, date=date)
        db.session.add(record)

    if time == "morning":
        record.morning = "not" if record.morning == "available" else "available"
    else:
        record.evening = "not" if record.evening == "available" else "available"

    db.session.commit()
    return "OK"


@app.route('/doctor/cancel/<int:appointment_id>')
def doctor_cancel(appointment_id):

    appt = Appointment.query.get_or_404(appointment_id)

    if appt.doctor_id != session.get("id"):
        return redirect(url_for('doctor_dash'))

    db.session.delete(appt)
    db.session.commit()

    return redirect(url_for('doctor_dash'))


@app.route('/doctor/toggle_complete/<int:appointment_id>')
def toggle_complete(appointment_id):

    appt = Appointment.query.get_or_404(appointment_id)

    if appt.doctor_id != session.get("id"):
        return redirect(url_for('doctor_dash'))

    if appt.status == "Booked":
        appt.status = "Completed"
    else:
        appt.status = "Booked"

    db.session.commit()

    return redirect(url_for('doctor_dash'))



@app.route('/department/<int:dept_id>')
def department_details(dept_id):
    department = Department.query.get_or_404(dept_id)

    doctors = User.query.filter_by(role="doctor", department_id=dept_id).all()

    return render_template(
        "patient/department_details.html",
        department=department,
        doctors=doctors
    )




@app.route('/doctor_dash')
def doctor_dash():
    doctor_id = session.get("id")

    appointments = (
        db.session.query(Appointment, User)
        .join(User, Appointment.patient_id == User.id)
        .filter(Appointment.doctor_id == doctor_id)
        .with_entities(
            Appointment.id,
            Appointment.status,
            User.user_name.label("patient_name")
        )
        .all()
    )

    assigned_patients = (
        User.query.join(Appointment, Appointment.patient_id == User.id)
        .filter(Appointment.doctor_id == doctor_id)
        .distinct()
        .all()
    )

    return render_template(
        "doctor_dash.html",
        appointments=appointments,
        patients=assigned_patients
    )


@app.route('/doctor/update_history/<int:appointment_id>', methods=['GET', 'POST'])
def update_history(appointment_id):

    appointment = Appointment.query.get_or_404(appointment_id)
    patient = User.query.get(appointment.patient_id)
    doctor = User.query.get(appointment.doctor_id)
    department = Department.query.get(doctor.department_id)
    medicines = Medicine.query.all()

    if request.method == 'POST':
        visit_type = request.form.get("visit_type")
        tests_done = request.form.get("tests_done")
        diagnosis = request.form.get("diagnosis")
        prescription = request.form.get("prescription")

        med_id = request.form.get("medicine_id")
        selected_medicine = Medicine.query.get(med_id)

        med_string = f"{selected_medicine.name} ({selected_medicine.intake_time})" if selected_medicine else ""

        new_record = Treatment(
            appointment_id=appointment.id,
            visit_type=visit_type,
            tests_done=tests_done,
            diagnosis=diagnosis,
            prescription=prescription,
            medicines=selected_medicine.name + " (" + selected_medicine.intake_time + ")"
        )

        db.session.add(new_record)

        appointment.status = "Completed"
        db.session.commit()

        return redirect(url_for('doctor_dash'))

    return render_template(
        "doctor/update_history.html",
        appointment=appointment,
        patient=patient,
        doctor=doctor,
        department=department,
        medicines=medicines
    )



 

@app.route('/admin_dash')
def admin_dash():

    if session.get("role") != "admin":
        return redirect(url_for('login'))

    doctors = User.query.filter_by(role="doctor").all()
    patients = User.query.filter_by(role="patient").all()

    patient = aliased(User)
    doctor = aliased(User)

    appointments = (
        db.session.query(
            Appointment.id,
            Appointment.patient_id,
            patient.user_name.label("patient_name"),
            doctor.user_name.label("doctor_name"),
            Department.name.label("department"),
            Appointment.date,
            Appointment.time
        )
        .join(patient, Appointment.patient_id == patient.id)
        .join(doctor, Appointment.doctor_id == doctor.id)
        .outerjoin(Department, doctor.department_id == Department.id)
        .all()
    )

    return render_template(
        "admin_dash.html",
        doctors=doctors,
        patients=patients,
        appointments=appointments
    )

@app.route('/patient_history/<int:patient_id>')
def patient_history_admin(patient_id):

    patient = User.query.get_or_404(patient_id)

    latest_appt = (
        Appointment.query
        .filter_by(patient_id=patient_id)
        .order_by(Appointment.id.desc())
        .first()
    )

    doctor = None
    department = None

    if latest_appt:
        doctor = User.query.get(latest_appt.doctor_id)
        if doctor:
            department = Department.query.get(doctor.department_id)

    history = (
        Treatment.query
        .join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(Appointment.patient_id == patient_id)
        .all()
    )

    return render_template(
        "patient/history.html",
        patient=patient,
        doctor=doctor,
        department=department,
        history=history
    )

@app.route('/cancel', methods=['POST'])
def cancel():
    appointment_id = request.json.get("appointment_id")
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != session.get("id"):
        return {"success": False}, 403

    db.session.delete(appointment)
    db.session.commit()

    return {"success": True}



@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        experience = request.form.get("experience")
        department_id = request.form.get("department_id")

        doctor = User(
            user_name=full_name,
            email=f"{full_name.replace(' ','').lower()}@hospital.com",
            password="doctor123",
            role="doctor",
            experience=experience,
            department_id=department_id
        )
        db.session.add(doctor)
        db.session.commit()

        return redirect(url_for('admin_dash'))
    
    departments = Department.query.all()
    return render_template("add_doctor.html", departments=departments)



if __name__ == '__main__':  
    with app.app_context():
        db.create_all()

        current_admin = User.query.filter_by(role="admin").first()
        if not current_admin:
            admin_user = User(
                user_name="admin1",
                email="admin1@example.com",
                password="admin123",
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)

 