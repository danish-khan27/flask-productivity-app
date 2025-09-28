from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields
from datetime import datetime

from server.config import db, bcrypt

# -------------------
# Models
# -------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, default="")
    bio = db.Column(db.String, default="")

    notes = relationship("Note", backref="user", lazy=True, cascade="all, delete-orphan")

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes are write-only.")

    @password_hash.setter
    def password_hash(self, raw_password: str):
        self._password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def authenticate(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self._password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.username} id={self.id}>"

class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @validates("title")
    def validate_title(self, key, value):
        if not value or not value.strip():
            raise ValueError("Title is required.")
        return value.strip()

    @validates("content")
    def validate_content(self, key, value):
        if not value or not value.strip():
            raise ValueError("Content is required.")
        if len(value.strip()) < 3:
            raise ValueError("Content must be at least 3 characters.")
        return value.strip()

    def __repr__(self):
        return f"<Note {self.id} user_id={self.user_id}>"

# -------------------
# Schemas
# -------------------

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    image_url = fields.Str()
    bio = fields.Str()

class NoteSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    content = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    user = fields.Nested(UserSchema)
