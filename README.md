Hospital Management System (Flask + SQLite)

A lightweight and structured Hospital Management System built using Flask, SQLite, and Jinja2.
The system supports three user roles — Admin, Doctor, and Patient — each with separate dashboards and functionality.

 Features
 User Authentication

Patient signup & login

Doctor & Admin login

Secure session handling

Role-based access control

 Patient Features

View all departments

View doctors under each department

Check doctor availability (Morning/Evening slots)

Book appointments

Cancel appointments

View complete treatment history

Auto-assigned doctor details for each appointment

** Doctor Features**

View upcoming appointments

View assigned patients

Update treatment history (visit type, tests, diagnosis, medicines, prescription)

Mark appointment as Complete / Completed (toggle button)

Cancel patient appointments

Set weekly availability (toggle Available ↔ Not Available for Morning/Evening)

🛠 Admin Features

Admin dashboard

Add new doctors

View all doctors & patients

View all appointments with doctor–patient details

Department-wise organization of doctors

💊 Treatment Module

Each completed appointment stores:

Visit Type

Tests Done

Diagnosis

Prescription

Selected Medicine + Intake Time

Timestamp (prescribed_at)

 Project Structure
/templates
    root.html
    login.html
    signup.html
    patient/
        patient_dash.html
        doctor_availability.html
        doctor_details.html
        department_details.html
        history.html
    doctor/
        doctor_dash.html
        doctor_availability.html
        update_history.html
    admin/
        admin_dash.html
        add_doctor.html

/static
    /images
    /css

app.py
site.db
README.md

🛠 Technologies Used

Flask (Backend + Routing)

SQLite3 (Database)

SQLAlchemy ORM

HTML + CSS + Jinja2 Templates

JavaScript (Fetch API for slot toggle)

Bootstrap (light usage)

 How to Run
1. Install Dependencies
pip install flask flask_sqlalchemy

2. Run the Server
python app.py

3. Visit in Browser
http://127.0.0.1:5000/

👨‍💼 Default Admin Login
Role	Email	Password
Admin	admin1@example.com
	admin123
 Special Logic Implemented

Doctor availability saved in DB using a toggle mechanism

Patient sees only available & unbooked slots

Completed appointments update the treatment table

Cancel removes the appointment entry immediately (AJAX-like behavior)

Clean CSS & consistent UI similar to signup page

 Notes

Database auto-generates on first run

You can manually delete old rows from SQLite using:

DELETE FROM appointments WHERE id IN (1,2,3,4);
DELETE FROM treatments WHERE appointment_id IN (1,2,3,4);
