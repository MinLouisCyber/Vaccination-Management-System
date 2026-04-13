from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))

        if request.method == 'POST':
            email    = request.form.get('email').strip()
            password = request.form.get('password').strip()

            print(f"Login attempt for email: {email}")

            user = User.query.filter_by(email=email).first()
            if user:
                print(f"User found with id: {user.user_id}")
                if check_password_hash(user.password, password):
                    login_user(user)
                    flash('Login successful!', 'success')
                    return redirect(url_for('main.dashboard'))
                else:
                    print("Password check failed")
            else:
                print("User not found")

            flash('Invalid email or password', 'error')
    except Exception as e:
        print(f"Login error: {str(e)}")
        flash('An error occurred during login', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.home'))
