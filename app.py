from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)


### -----models----- ###
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'admin', 'doctor', 'nurse', 'patient'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    #connection established between department and user  many to one 
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    #reverse relationship 
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
    status = db.Column(db.String(50), default='Booked', nullable=False)  # e.g., 'scheduled', 'completed', 'canceled'
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'), nullable=True, unique=True)

class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True)
    treatment_name = db.Column(db.String(100), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    prescribed_at = db.Column(db.DateTime, default=datetime.utcnow)



## run the app and create the database
if __name__ == '__main__':
    with app.app_context(): #needed for db operations

        db.create_all() #create the database and tables
    app.run(debug=True)


