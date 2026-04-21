from datetime import date, datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import (
    Profile, Appointment, Vaccine, Schedule, VaccineCentre,
    Inventory, stored_at
)

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/appointments/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        profile_id     = request.form.get('profile_id')
        booking_method = request.form.get('booking_method')
        time_slot      = request.form.get('time_slot')

        if booking_method == 'by_schedule':
            schedule_id = request.form.get('schedule_id')
            vaccine_id  = request.form.get('vaccine_id')
        else:
            schedule_id = request.form.get('schedule_id_vaccine')
            vaccine_id  = request.form.get('vaccine_id_direct')

        # Validate profile belongs to current user
        profile = Profile.query.get_or_404(profile_id)
        if profile.user_id != current_user.user_id:
            flash('Unauthorized access', 'error')
            return redirect(url_for('appointments.book_appointment'))

        schedule = Schedule.query.get_or_404(schedule_id)

        # Block past time slots for today
        if schedule.date == datetime.now().date():
            slot_time = datetime.strptime(time_slot, '%H:%M').time()
            if slot_time <= datetime.now().time():
                flash('Khung giờ bạn chọn đã đi qua trong ngày hôm nay. Vui lòng chọn khung giờ khác.', 'error')
                return redirect(url_for('appointments.book_appointment'))

        if vaccine_id not in [str(v.vaccine_id) for v in schedule.vaccines]:
            flash('Selected vaccine is not available in this schedule', 'error')
            return redirect(url_for('appointments.book_appointment'))

        existing_appointments = Appointment.query.filter_by(
            schedule_id=schedule_id,
            time_slot=time_slot
        ).count()
        if existing_appointments >= 10:
            flash('This time slot is full', 'error')
            return redirect(url_for('appointments.book_appointment'))

        # Check inventory
        inventory_item = (
            db.session.query(Inventory)
            .join(stored_at, Inventory.inventory_id == stored_at.c.inventory_id)
            .filter(stored_at.c.vaccine_id == vaccine_id)
            .filter(Inventory.quantity > 0)
            .order_by(Inventory.expiration_date.asc())
            .first()
        )
        if not inventory_item:
            flash('Vắc-xin này hiện tại đã hết trong kho.', 'error')
            return redirect(url_for('appointments.book_appointment'))

        appointment = Appointment(
            appointment_date=schedule.date,
            time_slot=time_slot,
            vaccine_id=vaccine_id,
            profile_id=profile_id,
            schedule_id=schedule_id
        )
        inventory_item.quantity -= 1
        db.session.add(appointment)
        db.session.commit()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    # GET
    profiles     = Profile.query.filter_by(user_id=current_user.user_id).all()
    current_date = datetime.now().date()
    schedules    = Schedule.query.filter(Schedule.date >= current_date).order_by(Schedule.date).all()
    vaccines     = Vaccine.query.all()

    schedule_vaccines = {
        s.schedule_id: [{'id': v.vaccine_id, 'name': v.name, 'price': v.price, 'min_age': v.min_age, 'max_age': v.max_age} for v in s.vaccines]
        for s in schedules
    }
    vaccine_schedules = {
        v.vaccine_id: [
            {'id': s.schedule_id, 'date': s.date.strftime('%d/%m/%Y'), 'centre_name': s.centre.name}
            for s in Schedule.query.filter(
                Schedule.date >= current_date,
                Schedule.vaccines.contains(v)
            ).all()
        ]
        for v in vaccines
    }

    return render_template(
        'book_appointment.html',
        profiles=profiles,
        schedules=schedules,
        vaccines=vaccines,
        schedule_vaccines=schedule_vaccines,
        vaccine_schedules=vaccine_schedules,
        today=date.today()
    )


@appointments_bp.route('/appointments/<int:appointment_id>/cancel')
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    profile     = Profile.query.get(appointment.profile_id)

    if profile.user_id != current_user.user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.dashboard'))

    if appointment.status not in ('Pending', 'Confirmed'):
        flash('Chỉ có thể hủy lịch hẹn đang chờ hoặc đã xác nhận.', 'error')
        return redirect(url_for('main.dashboard'))

    if appointment.appointment_date < datetime.now().date():
        flash('Cannot cancel past appointments', 'error')
        return redirect(url_for('main.dashboard'))

    inventory_item = (
        db.session.query(Inventory)
        .join(stored_at, Inventory.inventory_id == stored_at.c.inventory_id)
        .filter(stored_at.c.vaccine_id == appointment.vaccine_id)
        .filter(Inventory.quantity >= 0)
        .first()
    )
    if inventory_item:
        inventory_item.quantity += 1

    appointment.status = 'Cancelled'
    db.session.commit()
    flash('Lịch hẹn đã được hủy thành công!', 'success')
    return redirect(url_for('main.dashboard'))
