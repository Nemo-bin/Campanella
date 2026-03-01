from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    db.session.add(User(name="Ben"))
    db.session.commit()