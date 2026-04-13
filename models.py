from extensions import db

# ─── Association Tables ────────────────────────────────────────────────────────

stored_at = db.Table('StoredAt',
    db.Column('inventory_id', db.Integer, db.ForeignKey('Inventory.inventory_id'), primary_key=True),
    db.Column('vaccine_id',   db.Integer, db.ForeignKey('Vaccines.vaccine_id'),   primary_key=True)
)

includes = db.Table('Includes',
    db.Column('vaccine_id',  db.Integer, db.ForeignKey('Vaccines.vaccine_id'),  primary_key=True),
    db.Column('schedule_id', db.Integer, db.ForeignKey('Schedules.schedule_id'), primary_key=True)
)

available_at = db.Table('AvailableAt',
    db.Column('vaccine_id', db.Integer, db.ForeignKey('Vaccines.vaccine_id'),        primary_key=True),
    db.Column('centre_id',  db.Integer, db.ForeignKey('VaccineCentres.centre_id'),   primary_key=True)
)

# ─── Models ───────────────────────────────────────────────────────────────────

from flask_login import UserMixin

# Role constants (used across the app)
ROLE_USER          = 'user'
ROLE_ADMIN         = 'admin'
ROLE_VACCINE_ADMIN = 'vaccine_admin'

ADMIN_EMAILS         = ['admin@example.com']
VACCINE_ADMIN_EMAILS = ['vaccine_admin@example.com']


class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    user_id  = db.Column('user_id', db.Integer, primary_key=True, autoincrement=True)
    email    = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profiles = db.relationship('Profile', backref='user', lazy=True)

    def get_id(self):
        return str(self.user_id)

    @property
    def role(self):
        if self.email in ADMIN_EMAILS:
            return ROLE_ADMIN
        elif self.email in VACCINE_ADMIN_EMAILS:
            return ROLE_VACCINE_ADMIN
        return ROLE_USER


class Profile(db.Model):
    __tablename__ = 'Profiles'
    profile_id   = db.Column('profile_id', db.Integer, primary_key=True, autoincrement=True)
    gender       = db.Column(db.String(10))
    fname        = db.Column(db.String(50))
    mname        = db.Column(db.String(50))
    lname        = db.Column(db.String(50))
    age          = db.Column(db.Integer)
    user_id      = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    appointments = db.relationship('Appointment', backref='profile', lazy=True)


class Vaccine(db.Model):
    __tablename__ = 'Vaccines'
    vaccine_id  = db.Column('vaccine_id', db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text)
    min_age     = db.Column(db.Integer)
    max_age     = db.Column(db.Integer)
    name        = db.Column(db.String(100))


class Inventory(db.Model):
    __tablename__ = 'Inventory'
    inventory_id    = db.Column('inventory_id', db.Integer, primary_key=True, autoincrement=True)
    expiration_date = db.Column(db.Date)
    quantity        = db.Column(db.Integer)
    vaccines        = db.relationship('Vaccine', secondary='StoredAt')


class VaccineCentre(db.Model):
    __tablename__ = 'VaccineCentres'
    centre_id = db.Column('centre_id', db.Integer, primary_key=True, autoincrement=True)
    name      = db.Column(db.String(100))
    address   = db.Column(db.Text)
    district  = db.Column(db.String(50))
    pincode   = db.Column(db.String(10))


class Schedule(db.Model):
    __tablename__ = 'Schedules'
    schedule_id = db.Column('schedule_id', db.Integer, primary_key=True, autoincrement=True)
    date        = db.Column(db.Date)
    dose_number = db.Column(db.Integer)
    centre_id   = db.Column(db.Integer, db.ForeignKey('VaccineCentres.centre_id'))
    centre      = db.relationship('VaccineCentre')
    vaccines    = db.relationship('Vaccine', secondary='Includes')


class Appointment(db.Model):
    __tablename__ = 'Appointments'
    appointment_id   = db.Column('appointment_id', db.Integer, primary_key=True, autoincrement=True)
    appointment_date = db.Column(db.Date)
    time_slot        = db.Column(db.Time)
    vaccine_id       = db.Column(db.Integer, db.ForeignKey('Vaccines.vaccine_id'))
    profile_id       = db.Column(db.Integer, db.ForeignKey('Profiles.profile_id'))
    schedule_id      = db.Column(db.Integer, db.ForeignKey('Schedules.schedule_id'))
    status           = db.Column(db.String(20), default='Pending')
    vaccine          = db.relationship('Vaccine')
    schedule         = db.relationship('Schedule')
