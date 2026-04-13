from datetime import datetime

from flask import Blueprint, jsonify
from flask_login import login_required

from extensions import db
from models import Schedule, Vaccine, Appointment, VaccineCentre, Inventory, available_at, stored_at

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/schedule/<int:schedule_id>/vaccines')
@login_required
def get_schedule_vaccines(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    return jsonify([{'id': v.vaccine_id, 'name': v.name} for v in schedule.vaccines])


@api_bp.route('/vaccine/<int:vaccine_id>/schedules')
@login_required
def get_vaccine_schedules(vaccine_id):
    current_date = datetime.now().date()
    vaccine      = Vaccine.query.get_or_404(vaccine_id)
    schedules    = (
        Schedule.query
        .filter(Schedule.date >= current_date, Schedule.vaccines.contains(vaccine))
        .order_by(Schedule.date)
        .all()
    )
    return jsonify([{
        'id':          s.schedule_id,
        'date':        s.date.strftime('%Y-%m-%d'),
        'centre_name': s.centre.name
    } for s in schedules])


@api_bp.route('/schedules/<date>')
@login_required
def get_schedules(date):
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        schedules   = Schedule.query.filter_by(date=target_date).all()
        return jsonify([{
            'id':              s.schedule_id,
            'centre':          s.centre.name,
            'vaccines':        [{'id': v.vaccine_id, 'name': v.name} for v in s.vaccines],
            'dose_number':     s.dose_number,
            'available_slots': 10 - Appointment.query.filter_by(schedule_id=s.schedule_id).count()
        } for s in schedules])
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/vaccine-availability/<int:centre_id>')
@login_required
def get_vaccine_availability(centre_id):
    VaccineCentre.query.get_or_404(centre_id)
    available_vaccines = (
        db.session.query(Vaccine)
        .join(stored_at)
        .join(Inventory)
        .filter(Inventory.quantity > 0)
        .join(available_at)
        .filter(available_at.c.centre_id == centre_id)
        .all()
    )
    return jsonify([{
        'id':      v.vaccine_id,
        'name':    v.name,
        'min_age': v.min_age,
        'max_age': v.max_age
    } for v in available_vaccines])
