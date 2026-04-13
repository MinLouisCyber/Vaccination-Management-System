from datetime import date, datetime

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import (
    Profile, Appointment, Vaccine, VaccineCentre,
    ROLE_ADMIN, ROLE_VACCINE_ADMIN, ROLE_USER
)
from utils.pdf import generate_certificate_pdf
from flask import send_file

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    return render_template('home.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == ROLE_ADMIN:
        chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        chart_data   = [10, 20, 30, 40, 50]
        vaccines     = Vaccine.query.all()
        centres      = VaccineCentre.query.all()
        today_appointments = Appointment.query.filter(
            Appointment.appointment_date == date.today()
        ).count()
        recent_activities = [
            {"description": "Vaccine stock updated", "timestamp": datetime.now()},
            {"description": "Schedules Updated",     "timestamp": datetime.now()},
        ]
        return render_template(
            'admin_dashboard.html',
            vaccines=vaccines,
            centres=centres,
            today_appointments=today_appointments,
            recent_activities=recent_activities,
            chart_labels=chart_labels,
            chart_data=chart_data,
        )

    elif current_user.role == ROLE_VACCINE_ADMIN:
        return render_template('vaccine_admin_dashboard.html')

    else:
        profiles     = Profile.query.filter_by(user_id=current_user.user_id).all()
        appointments = Appointment.query.join(Profile).filter(
            Profile.user_id == current_user.user_id
        ).all()
        today = date.today()
        vaccination_history = [a for a in appointments if a.status == 'Completed']
        upcoming_reminders  = [
            a for a in appointments
            if a.status in ('Pending', 'Confirmed') and a.appointment_date >= today
        ]
        return render_template(
            'user_dashboard.html',
            profiles=profiles,
            appointments=appointments,
            today=today,
            vaccination_history=vaccination_history,
            upcoming_reminders=upcoming_reminders,
        )


# ── Profile ──────────────────────────────────────────────────────────────────

@main_bp.route('/profile/create', methods=['GET', 'POST'])
@login_required
def create_profile():
    from flask import request
    if request.method == 'POST':
        profile = Profile(
            gender=request.form.get('gender'),
            fname=request.form.get('fname'),
            mname=request.form.get('mname'),
            lname=request.form.get('lname'),
            age=int(request.form.get('age')),
            user_id=current_user.user_id
        )
        db.session.add(profile)
        db.session.commit()
        flash('Profile created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('create_profile.html')


@main_bp.route('/profile/<int:profile_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(profile_id):
    from flask import request
    profile = Profile.query.get_or_404(profile_id)
    if profile.user_id != current_user.user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        profile.gender = request.form.get('gender')
        profile.fname  = request.form.get('fname')
        profile.mname  = request.form.get('mname')
        profile.lname  = request.form.get('lname')
        profile.age    = int(request.form.get('age'))
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('edit_profile.html', profile=profile)


# ── Certificates ─────────────────────────────────────────────────────────────

@main_bp.route('/certificates')
@login_required
def view_certificates():
    profiles = Profile.query.filter_by(user_id=current_user.user_id).all()
    profile_appointments = {}
    for profile in profiles:
        profile_appointments[profile.profile_id] = (
            Appointment.query
            .filter_by(profile_id=profile.profile_id, status='Completed')
            .all()
        )

    current_date_str = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template(
        'certificates.html',
        profiles=profiles,
        profile_appointments=profile_appointments,
        current_date_str=current_date_str
    )


@main_bp.route('/download_certificate/<int:appointment_id>')
@login_required
def download_certificate(appointment_id):
    from models import Schedule, VaccineCentre
    appointment = (
        Appointment.query
        .join(Profile)
        .join(Vaccine)
        .join(Schedule)
        .join(VaccineCentre)
        .filter(Appointment.appointment_id == appointment_id)
        .first_or_404()
    )

    if appointment.profile.user_id != current_user.user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.view_certificates'))

    if appointment.status != 'Completed':
        flash('Chỉ có thể tải chứng nhận cho các mũi tiêm đã hoàn thành.', 'error')
        return redirect(url_for('main.view_certificates'))

    pdf_buffer = generate_certificate_pdf(appointment.profile, appointment)
    return send_file(
        pdf_buffer,
        download_name=f'vaccination_certificate_{appointment.appointment_id}.pdf',
        mimetype='application/pdf'
    )
