from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ======================= KHỞI TẠO APP VÀ DB =======================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cliniccare-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()


# ======================= MODELS (GỘP TẠM THỜI) =======================
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

# ======================= INIT DATABASE (10 BÁC SĨ MẪU) =======================
def init_db():
    db.create_all()
    
    # 1. Khởi tạo User Admin và Patient
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password=generate_password_hash("123"), full_name="Quản trị viên", role="admin")
        db.session.add(admin)
        
    if not User.query.filter_by(username="patient1").first():
        patient = User(username="patient1", password=generate_password_hash("123"), full_name="Ngô Nhật Tuấn", role="patient")
        db.session.add(patient)

    # 2. KHỞI TẠO CÁC BÁC SĨ (USER VÀ DOCTOR)
    
    # Bác sĩ 1 (Cũ - Nhi khoa)
    if not User.query.filter_by(username='dr_vanhung').first():
        dr_vanhung_user = User(
            username='dr_vanhung', 
            password=generate_password_hash('123'),
            full_name='Bác sĩ Nguyễn Văn Hùng',
            role='doctor'
        )
        db.session.add(dr_vanhung_user)
        db.session.flush() 
        db.session.add(Doctor(id=dr_vanhung_user.id, name='Bác sĩ Nguyễn Văn Hùng', specialty='Nhi khoa'))
        
    # Bác sĩ 2 (Cũ - Nội tổng quát)
    if not User.query.filter_by(username='dr_thaonguyen').first():
        dr_thaonguyen_user = User(
            username='dr_thaonguyen', 
            password=generate_password_hash('123'),
            full_name='Bác sĩ Nguyễn Thị Thu Thảo',
            role='doctor'
        )
        db.session.add(dr_thaonguyen_user)
        db.session.flush() 
        db.session.add(Doctor(id=dr_thaonguyen_user.id, name='Bác sĩ Nguyễn Thị Thu Thảo', specialty='Nội tổng quát'))
        
    # Bác sĩ 3 (Cũ - Da liễu)
    if not User.query.filter_by(username='dr_kiutram').first():
        dr_kiutram_user = User(
            username='dr_kiutram', 
            password=generate_password_hash('123'),
            full_name='Bác sĩ Lê Ngọc Kiều Trâm',
            role='doctor'
        )
        db.session.add(dr_kiutram_user)
        db.session.flush() 
        db.session.add(Doctor(id=dr_kiutram_user.id, name='Bác sĩ Lê Ngọc Kiều Trâm', specialty='Da liễu'))

    # Bác sĩ 4 (Cũ - Răng - Hàm - Mặt)
    if not User.query.filter_by(username='dr_tuananh').first():
        dr_tuananh_user = User(
            username='dr_tuananh', 
            password=generate_password_hash('123'),
            full_name='Bác sĩ Lê Tuấn Anh',
            role='doctor'
        )
        db.session.add(dr_tuananh_user)
        db.session.flush() 
        db.session.add(Doctor(id=dr_tuananh_user.id, name='Bác sĩ Lê Tuấn Anh', specialty='Răng - Hàm - Mặt'))

    # Bác sĩ 5 (Cũ - Ngoại tổng quát)
    if not User.query.filter_by(username='dr_nhuquynh').first():
        dr_nhuquynh_user = User(
            username='dr_nhuquynh', 
            password=generate_password_hash('123'),
            full_name='Bác sĩ Trần Như Quỳnh',
            role='doctor'
        )
        db.session.add(dr_nhuquynh_user)
        db.session.flush() 
        db.session.add(Doctor(id=dr_nhuquynh_user.id, name='Bác sĩ Trần Như Quỳnh', specialty='Ngoại tổng quát'))
    
    # === 5 BÁC SĨ MỚI (CHUYÊN KHOA KHÁC) ===
    
    # Bác sĩ 6: Quang Hải (Tai Mũi Họng)
    if not User.query.filter_by(username='dr_quanghai').first():
        dr_quanghai_user = User(
            username='dr_quanghai',
            password=generate_password_hash('123'),
            full_name='Bác sĩ Trần Quang Hải',
            role='doctor'
        )
        db.session.add(dr_quanghai_user)
        db.session.flush()
        db.session.add(Doctor(id=dr_quanghai_user.id, name='Bác sĩ Trần Quang Hải', specialty='Tai Mũi Họng'))
        
    # Bác sĩ 7: Mai Chi (Mắt)
    if not User.query.filter_by(username='dr_maichi').first():
        dr_maichi_user = User(
            username='dr_maichi',
            password=generate_password_hash('123'),
            full_name='Bác sĩ Nguyễn Mai Chi',
            role='doctor'
        )
        db.session.add(dr_maichi_user)
        db.session.flush()
        db.session.add(Doctor(id=dr_maichi_user.id, name='Bác sĩ Nguyễn Mai Chi', specialty='Mắt'))
        
    # Bác sĩ 8: Văn Thanh (Xương Khớp)
    if not User.query.filter_by(username='dr_vanthanh').first():
        dr_vanthanh_user = User(
            username='dr_vanthanh',
            password=generate_password_hash('123'),
            full_name='Bác sĩ Hoàng Văn Thanh',
            role='doctor'
        )
        db.session.add(dr_vanthanh_user)
        db.session.flush()
        db.session.add(Doctor(id=dr_vanthanh_user.id, name='Bác sĩ Hoàng Văn Thanh', specialty='Cơ Xương Khớp'))

    # Bác sĩ 9: Phương Linh (Sản Phụ khoa)
    if not User.query.filter_by(username='dr_phuonglinh').first():
        dr_phuonglinh_user = User(
            username='dr_phuonglinh',
            password=generate_password_hash('123'),
            full_name='Bác sĩ Phạm Phương Linh',
            role='doctor'
        )
        db.session.add(dr_phuonglinh_user)
        db.session.flush()
        db.session.add(Doctor(id=dr_phuonglinh_user.id, name='Bác sĩ Phạm Phương Linh', specialty='Sản Phụ khoa'))

    # Bác sĩ 10: Minh Đức (Tiêu Hóa)
    if not User.query.filter_by(username='dr_minhduc').first():
        dr_minhduc_user = User(
            username='dr_minhduc',
            password=generate_password_hash('123'),
            full_name='Bác sĩ Đỗ Minh Đức',
            role='doctor'
        )
        db.session.add(dr_minhduc_user)
        db.session.flush()
        db.session.add(Doctor(id=dr_minhduc_user.id, name='Bác sĩ Đỗ Minh Đức', specialty='Tiêu Hóa'))

    db.session.commit()
    print("✅ Database initialized! Users and Doctors are ready.")

# ======================= UTILS =======================
def current_user():
    uid = session.get('user_id')
    if uid:
        return User.query.get(uid)
    return None

# ======================= ROUTES =======================
@app.route('/')
def home():
    user = current_user()
    return render_template('home.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form.get('full_name', '')
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại', 'danger')
            return redirect(url_for('register'))
        u = User(username=username, password=generate_password_hash(password),
                 full_name=fullname, role='patient')
        db.session.add(u)
        db.session.commit()
        flash('Đăng ký thành công. Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        u = User.query.filter_by(username=username).first()
        if u and check_password_hash(u.password, password):
            session['user_id'] = u.id
            flash('Đăng nhập thành công', 'success')
            return redirect(url_for('home'))
        flash('Sai tên đăng nhập hoặc mật khẩu', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Đã đăng xuất', 'info')
    return redirect(url_for('home'))

@app.route('/doctors')
def doctors():
    user = current_user()
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors, user=user)

@app.route('/booking/<int:doctor_id>', methods=['GET', 'POST'])
def booking(doctor_id):
    user = current_user()
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == 'POST':
        if not user:
            flash('Bạn cần đăng nhập để đặt lịch', 'warning')
            return redirect(url_for('login'))
        time = request.form['time']
        note = request.form.get('note', '')
        ap = Appointment(patient_id=user.id, doctor_id=doctor.id,
                         time=time, note=note, status='pending')
        db.session.add(ap)
        db.session.commit()
        flash('Đặt lịch thành công', 'success')
        return redirect(url_for('home'))
    return render_template('booking.html', doctor=doctor, user=user)

@app.route('/my_appointments')
def my_appointments():
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập', 'warning')
        return redirect(url_for('login'))
    
    if user.role == 'doctor':
        appts = Appointment.query.filter_by(doctor_id=user.id).all()
        for ap in appts:
            ap.patient_info = User.query.get(ap.patient_id)
            # Vì MedicalRecord nằm trong file này, không cần import
            ap.has_record = MedicalRecord.query.filter_by(appointment_id=ap.id).first() is not None
            
    else: # patient
        appts = Appointment.query.filter_by(patient_id=user.id).all()
        for ap in appts:
            ap.doctor_profile = Doctor.query.get(ap.doctor_id)
            ap.doctor_user = User.query.get(ap.doctor_id)
            ap.has_record = MedicalRecord.query.filter_by(appointment_id=ap.id).first() is not None 

    return render_template('appointments.html', appts=appts, user=user)

@app.route('/admin')
def admin_page():
    user = current_user()
    if not user or user.role != 'admin':
        flash('Không có quyền truy cập', 'danger')
        return redirect(url_for('home'))
    users = User.query.all()
    appts = Appointment.query.all()
    doctors = Doctor.query.all()
    return render_template('admin.html', users=users, appts=appts, doctors=doctors, user=user)

@app.route('/appointment/<int:ap_id>/action/<string:act>')
def appointment_action(ap_id, act):
    user = current_user()
    
    if not user or user.role == 'patient':
        flash('Không có quyền thực hiện', 'danger')
        return redirect(url_for('my_appointments')) 
    
    ap = Appointment.query.get_or_404(ap_id)

    if user.role == 'doctor' and ap.doctor_id != user.id:
        flash('Bạn không có quyền quản lý lịch hẹn này.', 'danger')
        return redirect(url_for('my_appointments'))
    
    if act == 'accept':
        ap.status = 'accepted'
        flash('Đã xác nhận lịch hẹn', 'success')
    elif act == 'reject':
        ap.status = 'rejected'
        flash('Đã từ chối lịch hẹn', 'info')
    else:
        flash('Hành động không hợp lệ', 'danger')
        return redirect(url_for('my_appointments'))

    db.session.commit()
    
    if user.role == 'admin':
        return redirect(url_for('admin_page'))
    else:
        return redirect(url_for('my_appointments'))
    
@app.route('/create_record/<int:ap_id>', methods=['GET', 'POST'])
def create_record(ap_id):
    user = current_user()
    ap = Appointment.query.get_or_404(ap_id)
    
    if not user or user.role != 'doctor' or ap.doctor_id != user.id:
        flash('Bạn không có quyền truy cập hoặc xử lý lịch hẹn này.', 'danger')
        return redirect(url_for('my_appointments'))
    
    if ap.status != 'accepted':
        flash('Chỉ có thể tạo hồ sơ khi lịch hẹn đã được xác nhận (Accepted).', 'warning')
        return redirect(url_for('my_appointments'))
        
    existing_record = MedicalRecord.query.filter_by(appointment_id=ap_id).first()
    if existing_record:
        flash('Hồ sơ bệnh án cho lịch hẹn này đã được tạo.', 'info')
        return redirect(url_for('my_appointments')) 

    patient = User.query.get(ap.patient_id)
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        
        if not diagnosis:
            flash('Vui lòng nhập Chẩn đoán.', 'danger')
            return redirect(url_for('create_record', ap_id=ap_id))

        record = MedicalRecord(
            appointment_id=ap.id,
            patient_id=ap.patient_id,
            doctor_id=user.id,
            diagnosis=diagnosis,
            treatment=treatment
        )
        db.session.add(record)
        
        ap.status = 'completed'
        
        db.session.commit()
        flash('✅ Hồ sơ bệnh án đã được tạo thành công!', 'success')
        return redirect(url_for('my_appointments'))
        
    return render_template('create_record.html', ap=ap, patient=patient, user=user)

# ======================= RUN APP =======================
if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, use_reloader=False)

    