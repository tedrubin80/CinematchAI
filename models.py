# models.py - Database models for Cinematch (neutered demo subset)

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)

    two_factor_secret = db.Column(db.String(32))
    two_factor_enabled = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_account_locked(self):
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False

    def lock_account(self, duration_minutes=30):
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        db.session.commit()

    def unlock_account(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None
        db.session.commit()


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))


class APIKey(db.Model):
    __tablename__ = 'api_keys'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service = db.Column(db.String(50), nullable=False)
    encrypted_key = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))


class ContentKeyword(db.Model):
    __tablename__ = 'content_keywords'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = db.Column(db.String(50), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))


class MovieDocument(db.Model):
    __tablename__ = 'movie_documents'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = db.Column(db.String(50))
    source_id = db.Column(db.String(500))
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    doc_metadata = db.Column(JSONB)
    embedding = db.Column(Vector(1536))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatLog(db.Model):
    __tablename__ = 'chat_logs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = db.Column(db.String(64), db.ForeignKey('sessions.id'))
    user_input = db.Column(db.Text)
    bot_response = db.Column(db.Text)
    llm_used = db.Column(db.String(50))
    content_rating = db.Column(db.String(20))
    response_time_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
