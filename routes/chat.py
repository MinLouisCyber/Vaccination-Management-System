import json
import os
import requests

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from models import Profile, Appointment, Vaccine, Schedule, VaccineCentre, ROLE_USER

chat_bp = Blueprint('chat', __name__)

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL   = 'llama-3.3-70b-versatile'

SYSTEM_PROMPT = """You are a helpful assistant for the Vinavacci vaccination management system. You can help users by providing information about:

1. Their profiles and profile management
2. Their current and upcoming appointments
3. Available vaccines and vaccination centers
4. General scheduling information
5. Basic system navigation guidance
6. Any general assistance about vaccines based on your pre trained knowledge

You can view but not modify:
- User profiles
- Appointment details
- Vaccine information
- Schedule information
- Center information

When responding:
- Provide clear, accurate information from the database
- Give step-by-step guidance for using system features
- Direct users to appropriate pages for actions
- Format dates as YYYY-MM-DD and times in 24-hour format
- Maintain a helpful and health-focused tone
- Well structured message with proper spaces and New lines

You cannot:
- Directly modify any database records
- Access admin functions
- View sensitive system information
- Make changes to appointments or profiles"""


@chat_bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat_interface():
    if current_user.role != ROLE_USER:
        flash('This feature is only available for regular users.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            user_message = request.json.get('message', '')

            profiles     = Profile.query.filter_by(user_id=current_user.user_id).all()
            profile_info = [{'name': f"{p.fname} {p.lname}", 'age': p.age, 'gender': p.gender, 'id': p.profile_id}
                            for p in profiles]

            appointments = (
                Appointment.query
                .join(Profile)
                .filter(Profile.user_id == current_user.user_id)
                .join(Vaccine)
                .join(Schedule)
                .join(VaccineCentre)
                .all()
            )
            appt_info = [{
                'date':    a.appointment_date.strftime('%Y-%m-%d'),
                'time':    a.time_slot.strftime('%H:%M'),
                'vaccine': a.vaccine.name,
                'centre':  a.schedule.centre.name,
                'address': a.schedule.centre.address,
                'id':      a.appointment_id,
            } for a in appointments]

            vaccines     = Vaccine.query.all()
            vaccine_info = [{'name': v.name, 'description': v.description,
                             'min_age': v.min_age, 'max_age': v.max_age} for v in vaccines]

            centres     = VaccineCentre.query.all()
            centre_info = [{'name': c.name, 'address': c.address,
                            'district': c.district, 'pincode': c.pincode} for c in centres]

            context = f"""Current user: {current_user.email}

User Profiles:
{json.dumps(profile_info, indent=2)}

User Appointments:
{json.dumps(appt_info, indent=2)}

Available Vaccines:
{json.dumps(vaccine_info, indent=2)}

Vaccination Centers:
{json.dumps(centre_info, indent=2)}"""

            response = requests.post(
                GROQ_API_URL,
                headers={
                    'Authorization': f'Bearer {GROQ_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': GROQ_MODEL,
                    'messages': [
                        {'role': 'system', 'content': SYSTEM_PROMPT},
                        {'role': 'user', 'content': f"Context:\n{context}\n\nUser message: {user_message}"}
                    ],
                    'temperature': 1,
                    'max_tokens':  1024,
                    'stream':      False
                }
            )

            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                return jsonify({'response': ai_response})
            else:
                return jsonify({'error': 'Failed to get response from AI'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # GET
    try:
        profiles = Profile.query.filter_by(user_id=current_user.user_id).all()
        return render_template('chat.html', profiles=profiles)
    except Exception as e:
        flash('An error occurred while loading the chat interface.', 'error')
        return redirect(url_for('main.dashboard'))
