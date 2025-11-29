from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
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
        user_name = request.form.get("user_name")
        password = request.form.get("password")

        user = User.query.filter_by(user_name=user_name, password=password).first()
        if user and user.role == "patient":
            return redirect(url_for('patient_dashboard'))
        elif user and user.role == "doctor":
            return redirect(url_for('doctor_dashboard'))
        elif user and user.role == "admin":
            return redirect(url_for('admin_dashboard'))
        return render_template('login.html', error="you'ar new user go & signup first")
    return render_template('login.html')

@app.route('/patient_dash')
def patient_dash():
    return render_template('patient_dash.html')

@app.route('/doctor_dash')
def doctor_dash():
    return render_template('doctor_dash.html')  

@app.route('/admin_dash')
def admin_dash():
    return render_template('admin_dash.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context(): 

        db.create_all() 
    app.run(debug=True)
 