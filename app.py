import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from sqlalchemy import text

from auth import auth_bp
from main import main_bp
from admin_routes import admin_bp
from student_routes import student_bp
from company_routes import company_bp

ADMIN_EMAIL = "admin@college.com"
ADMIN_PASSWORD = "admin123"

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_schema_updates()
        seed_admin()

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)

    return app


def ensure_schema_updates():
    # Add applications.resume_filename if missing (SQLite-safe)
    cols = db.session.execute(text("PRAGMA table_info(applications);")).fetchall()
    col_names = {c[1] for c in cols}  # second field is column name

    if "resume_filename" not in col_names:
        db.session.execute(text("ALTER TABLE applications ADD COLUMN resume_filename TEXT;"))
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def seed_admin():
    existing = User.query.filter_by(email=ADMIN_EMAIL).first()
    if existing:
        return
    admin = User(email=ADMIN_EMAIL, role="admin", is_active=True, is_blacklisted=False)
    admin.set_password(ADMIN_PASSWORD)
    db.session.add(admin)
    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)