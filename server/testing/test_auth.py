import pytest
from server.config import create_app, db
from server.models import User

@pytest.fixture
def client():
    app = create_app("test")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_signup_and_login(client):
    # signup
    resp = client.post("/signup", json={"username": "bob", "password": "pw"})
    assert resp.status_code == 201

    # check session
    resp = client.get("/check_session")
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "bob"
