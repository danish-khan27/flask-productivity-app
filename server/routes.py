from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, desc

from server.config import db
from server.models import User, Note, UserSchema, NoteSchema

# ----------------
# Helpers
# ----------------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)

def require_login():
    if not session.get("user_id"):
        return {"error": "Unauthorized"}, 401
    return None

def require_owner(note: Note):
    if note.user_id != session.get("user_id"):
        return {"error": "Forbidden"}, 403
    return None

# ----------------
# Auth resources
# ----------------
class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"errors": ["Username and password are required."]}, 422

        try:
            user = User(username=username)
            user.password_hash = password  # hashes via setter
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return UserSchema().dump(user), 201
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username must be unique."]}, 422

class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session["user_id"] = user.id
            return UserSchema().dump(user), 200
        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401
        session.pop("user_id", None)
        return "", 204

class CheckSession(Resource):
    def get(self):
        user = current_user()
        if not user:
            return {"error": "Unauthorized"}, 401
        return UserSchema().dump(user), 200

# ----------------
# Notes resources
# ----------------
class NotesIndex(Resource):
    def get(self):
        unauthorized = require_login()
        if unauthorized:
            return unauthorized

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = max(1, min(per_page, 50))

        stmt = select(Note).where(Note.user_id == session["user_id"]).order_by(desc(Note.id))
        paginated = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

        return {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "total_pages": paginated.pages,
            "items": [NoteSchema().dump(n) for n in paginated.items],
        }, 200

    def post(self):
        unauthorized = require_login()
        if unauthorized:
            return unauthorized

        data = request.get_json() or {}
        note = Note(
            title=data.get("title"),
            content=data.get("content"),
            user_id=session["user_id"],
        )
        db.session.add(note)
        db.session.commit()
        return NoteSchema().dump(note), 201

# ----------------
# Single place to bind resources
# ----------------
def register_routes(api):
    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")
    api.add_resource(CheckSession, "/check_session")
    api.add_resource(NotesIndex, "/notes")
