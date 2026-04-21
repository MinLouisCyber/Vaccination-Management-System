from datetime import date, datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models import (
    Appointment, Profile, User, Vaccine, Schedule, VaccineCentre,
    Inventory, ROLE_ADMIN, ROLE_VACCINE_ADMIN
)
from utils.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Vaccines ─────────────────────────────────────────────────────────────────

@admin_bp.route('/vaccines', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def manage_vaccines():
    if request.method == 'POST':
        vaccine = Vaccine(
            name=request.form.get('name'),
            description=request.form.get('description'),
            min_age=int(request.form.get('min_age')),
            max_age=int(request.form.get('max_age')),
            price=float(request.form.get('price', 0.0)) if request.form.get('price') else 0.0
        )
        db.session.add(vaccine)
        db.session.commit()
        flash('Vaccine added successfully!', 'success')
        return redirect(url_for('admin.manage_vaccines'))

    vaccines = Vaccine.query.all()
    return render_template('admin/manage_vaccines.html', vaccines=vaccines)


@admin_bp.route('/vaccines/edit/<int:vaccine_id>', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def edit_vaccine(vaccine_id):
    vaccine = Vaccine.query.get_or_404(vaccine_id)

    if request.method == 'POST':
        vaccine.name        = request.form.get('name')
        vaccine.description = request.form.get('description')
        vaccine.min_age     = request.form.get('min_age')
        vaccine.max_age     = request.form.get('max_age')
        vaccine.price       = float(request.form.get('price', 0.0)) if request.form.get('price') else 0.0
        db.session.commit()
        flash('Vaccine updated successfully!', 'success')
        return redirect(url_for('admin.manage_vaccines'))

    return render_template('edit_vaccine.html', vaccine=vaccine)


@admin_bp.route('/vaccines/delete/<int:vaccine_id>', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN])
def delete_vaccine(vaccine_id):
    vaccine = Vaccine.query.get_or_404(vaccine_id)

    if Schedule.query.join(Schedule.vaccines).filter(Vaccine.vaccine_id == vaccine_id).count() > 0:
        flash('Cannot delete vaccine with associated schedules. Remove them first.', 'error')
        return redirect(url_for('admin.manage_vaccines'))

    db.session.delete(vaccine)
    db.session.commit()
    flash('Vaccine deleted successfully!', 'success')
    return redirect(url_for('admin.manage_vaccines'))


# ── Schedules ─────────────────────────────────────────────────────────────────

@admin_bp.route('/schedules', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_VACCINE_ADMIN])
def manage_schedules():
    if request.method == 'POST':
        schedule = Schedule(
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            dose_number=int(request.form.get('dose_number')),
            centre_id=int(request.form.get('centre_id'))
        )
        db.session.add(schedule)
        db.session.commit()

        for vaccine_id in request.form.getlist('vaccines'):
            vaccine = Vaccine.query.get(vaccine_id)
            schedule.vaccines.append(vaccine)

        db.session.commit()
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('admin.manage_schedules'))

    schedules = Schedule.query.all()
    centres   = VaccineCentre.query.all()
    vaccines  = Vaccine.query.all()
    return render_template('admin/manage_schedules.html',
                           schedules=schedules, centres=centres, vaccines=vaccines)


@admin_bp.route('/schedules/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_VACCINE_ADMIN])
def edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    centres  = VaccineCentre.query.all()
    vaccines = Vaccine.query.all()

    if request.method == 'POST':
        schedule.date        = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        schedule.centre_id   = int(request.form.get('centre_id'))
        schedule.dose_number = int(request.form.get('dose_number'))

        schedule.vaccines.clear()
        for vaccine_id in request.form.getlist('vaccines'):
            vaccine = Vaccine.query.get(vaccine_id)
            schedule.vaccines.append(vaccine)

        db.session.commit()
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('admin.manage_schedules'))

    return render_template('edit_schedule.html', schedule=schedule, centres=centres, vaccines=vaccines)


@admin_bp.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_VACCINE_ADMIN])
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)

    if Appointment.query.filter_by(schedule_id=schedule_id).count() > 0:
        flash("Cannot delete schedule with existing appointments. Please cancel associated appointments first.", "error")
        return redirect(url_for('admin.manage_schedules'))

    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('admin.manage_schedules'))


# ── Centres ───────────────────────────────────────────────────────────────────

@admin_bp.route('/centres', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def manage_centres():
    if request.method == 'POST':
        centre = VaccineCentre(
            name=request.form.get('name'),
            address=request.form.get('address'),
            district=request.form.get('district'),
            pincode=request.form.get('pincode')
        )
        db.session.add(centre)
        db.session.commit()
        flash('Vaccination centre added successfully!', 'success')
        return redirect(url_for('admin.manage_centres'))

    centres = VaccineCentre.query.all()
    return render_template('admin/manage_centres.html', centres=centres)


@admin_bp.route('/centres/edit/<int:centre_id>', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def edit_centre(centre_id):
    centre = VaccineCentre.query.get_or_404(centre_id)

    if request.method == 'POST':
        centre.name     = request.form.get('name')
        centre.address  = request.form.get('address')
        centre.district = request.form.get('district')
        centre.pincode  = request.form.get('pincode')
        db.session.commit()
        flash('Vaccination center updated successfully!', 'success')
        return redirect(url_for('admin.manage_centres'))

    return render_template('edit_centre.html', centre=centre)


@admin_bp.route('/centres/delete/<int:centre_id>', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN])
def delete_centre(centre_id):
    centre = VaccineCentre.query.get_or_404(centre_id)

    if Schedule.query.filter_by(centre_id=centre_id).count() > 0:
        flash('Cannot delete center with associated schedules. Remove them first.', 'error')
        return redirect(url_for('admin.manage_centres'))

    db.session.delete(centre)
    db.session.commit()
    flash('Vaccination center deleted successfully!', 'success')
    return redirect(url_for('admin.manage_centres'))


# ── Inventory ─────────────────────────────────────────────────────────────────

@admin_bp.route('/inventory', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def manage_inventory():
    if request.method == 'POST':
        try:
            vaccine_id      = request.form.get('vaccine_id')
            expiration_date = datetime.strptime(request.form.get('expiration_date'), '%Y-%m-%d')
            quantity        = int(request.form.get('quantity'))

            inventory = Inventory(expiration_date=expiration_date, quantity=quantity)
            vaccine   = Vaccine.query.get(vaccine_id)
            if vaccine:
                inventory.vaccines.append(vaccine)

            db.session.add(inventory)
            db.session.commit()
            flash('Inventory added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating inventory: {str(e)}', 'error')

        return redirect(url_for('admin.manage_inventory'))

    inventories = Inventory.query.options(db.joinedload(Inventory.vaccines)).all()
    vaccines    = Vaccine.query.all()
    return render_template(
        'admin/manage_inventory.html',
        inventories=inventories,
        vaccines=vaccines,
        current_date=date.today()
    )


@admin_bp.route('/inventory/edit/<int:inventory_id>', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def edit_inventory(inventory_id):
    inventory = Inventory.query.options(db.joinedload(Inventory.vaccines)).get_or_404(inventory_id)
    vaccines  = Vaccine.query.all()

    if request.method == 'POST':
        try:
            inventory.expiration_date = datetime.strptime(request.form.get('expiration_date'), '%Y-%m-%d')
            inventory.quantity        = int(request.form.get('quantity'))

            new_vaccine = Vaccine.query.get(request.form.get('vaccine_id'))
            if new_vaccine:
                inventory.vaccines = [new_vaccine]

            db.session.commit()
            flash('Inventory updated successfully!', 'success')
            return redirect(url_for('admin.manage_inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating inventory: {str(e)}', 'error')

    return render_template('admin/edit_inventory.html', inventory=inventory, vaccines=vaccines)


@admin_bp.route('/inventory/delete/<int:inventory_id>', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN])
def delete_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)
    try:
        db.session.delete(inventory)
        db.session.commit()
        flash('Inventory deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting inventory: {str(e)}', 'error')
    return redirect(url_for('admin.manage_inventory'))


# ── Appointments Overview ─────────────────────────────────────────────────────

@admin_bp.route('/appointments')
@login_required
@role_required([ROLE_ADMIN])
def admin_appointments():
    appointments = (
        db.session.query(Appointment, Profile, User, Vaccine, Schedule, VaccineCentre)
        .join(Profile,      Appointment.profile_id  == Profile.profile_id)
        .join(User,         Profile.user_id          == User.user_id)
        .join(Vaccine,      Appointment.vaccine_id   == Vaccine.vaccine_id)
        .join(Schedule,     Appointment.schedule_id  == Schedule.schedule_id)
        .join(VaccineCentre, Schedule.centre_id      == VaccineCentre.centre_id)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )

    grouped_appointments = {}
    for appt, profile, user, vaccine, schedule, centre in appointments:
        grouped_appointments.setdefault(user.email, {})
        profile_key = f"{profile.fname} {profile.lname}"
        grouped_appointments[user.email].setdefault(profile_key, [])
        grouped_appointments[user.email][profile_key].append({
            'appointment_id': appt.appointment_id,
            'date':           appt.appointment_date,
            'time':           appt.time_slot,
            'vaccine':        vaccine.name,
            'dose_number':    schedule.dose_number,
            'centre':         centre.name,
            'district':       centre.district,
            'profile_id':     profile.profile_id,
            'age':            profile.age,
            'gender':         profile.gender,
            'status':         appt.status,
        })

    return render_template('admin/appointments_overview.html', appointments=grouped_appointments)


@admin_bp.route('/appointment/<int:id>/complete', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN])
def admin_complete_appointment(id):
    appointment = Appointment.query.get_or_404(id)

    if appointment.status == 'Completed':
        flash('Lịch hẹn này đã được đánh dấu hoàn thành rồi.', 'info')
        return redirect(url_for('admin.admin_appointments'))

    if appointment.status == 'Cancelled':
        flash('Không thể hoàn thành lịch hẹn đã bị hủy.', 'error')
        return redirect(url_for('admin.admin_appointments'))

    appointment.status = 'Completed'
    
    db.session.commit()
    flash('Đã xác nhận hoàn thành tiêm chủng thành công!', 'success')
    return redirect(url_for('admin.admin_appointments'))


@admin_bp.route('/appointment/<int:id>/confirm', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN])
def admin_confirm_appointment(id):
    appointment = Appointment.query.get_or_404(id)

    if appointment.status != 'Pending':
        flash('Chỉ có thể xác nhận lịch hẹn đang ở trạng thái chờ xử lý.', 'error')
        return redirect(url_for('admin.admin_appointments'))

    appointment.status = 'Confirmed'
    db.session.commit()
    flash('Đã xác nhận lịch hẹn thành công! Người dân có thể đến tiêm chủng.', 'success')
    return redirect(url_for('admin.admin_appointments'))
