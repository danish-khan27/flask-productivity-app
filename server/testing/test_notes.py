import pytest
from server.config import create_app, db
from server.models import User, Note

@pytest.fixture
def client():
    app = create_app("test")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_create_note_requires_login(client):
    # attempt without login
    resp = client.post("/notes", json={"title": "test", "content": "hello"})
    assert resp.status_code == 401

def test_create_and_list_notes(client):
    # signup + login
    client.post("/signup", json={"username": "alice", "password": "pw"})

    # create a note
    resp = client.post("/notes", json={"title": "note1", "content": "content123"})
    assert resp.status_code == 201

    # list notes
    resp = client.get("/notes")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "note1"
