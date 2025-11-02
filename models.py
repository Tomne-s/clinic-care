# models.py
# =============================================================
# KHÔNG CÓ DÒNG from app import db NỮA
# Sử dụng db được định nghĩa global trong app.py
# =============================================================

from flask_sqlalchemy import SQLAlchemy
# Chúng ta sẽ sử dụng một đối tượng db placeholder TẠM THỜI cho linter
# Hoặc, chỉ cần giả định db tồn tại và nó sẽ được resolve khi app.py chạy.

# Để tránh lỗi, hãy làm như sau:
try:
    from app import db
except ImportError:
    # Nếu Import vòng tròn vẫn xảy ra, chúng ta chỉ cần giả định
    # rằng db được định nghĩa trong ngữ cảnh chạy.
    # Trong môi trường Flask, nó thường tự resolve.
    db = SQLAlchemy() # Dùng placeholder nếu cần thiết cho IDE

# =============================================================
# CHỈ CẦN DÁN NỘI DUNG NÀY VÀO models.py
# =============================================================
from app import db # Thử lại lần cuối cùng với mã nguồn chuẩn này.

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), default='patient')

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(120))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    time = db.Column(db.String(120), nullable=False)
    note = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    diagnosis = db.Column(db.Text, nullable=False) 
    treatment = db.Column(db.Text)                
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    appointment = db.relationship('Appointment', backref=db.backref('record', uselist=False))
    patient = db.relationship('User', foreign_keys=[patient_id], backref='medical_records')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='records_created')