from flask import Flask, render_template
from os import environ

from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Init extensions ──────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)

    # ── User loader ──────────────────────────────────────────────────────────
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Register blueprints ──────────────────────────────────────────────────
    from routes.auth         import auth_bp
    from routes.main         import main_bp
    from routes.appointments import appointments_bp
    from routes.admin        import admin_bp
    from routes.chat         import chat_bp
    from routes.api          import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp)

    # ── Error handlers ───────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(environ.get('PORT', 10000)))
