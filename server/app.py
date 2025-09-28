#!/usr/bin/env python3
import os
from server.config import create_app, db

env = os.getenv("FLASK_ENV", "dev")
app = create_app(env)

if __name__ == "__main__":
    # Ensure DB tables exist when running locally
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)
