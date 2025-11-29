from sqlalchemy.orm import aliased
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
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='Booked', nullable=False) 
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'), nullable=True, unique=True)

class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True)
    treatment_name = db.Column(db.String(100), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    prescribed_at = db.Column(db.DateTime, default=datetime.utcnow)


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

 