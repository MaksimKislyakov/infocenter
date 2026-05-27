import os

os.environ.setdefault("TESTING", "1")

from app.db.session import Base, engine
import app.models

Base.metadata.create_all(bind=engine)

from app.main import create_default_units, create_default_admin, create_default_user
create_default_units()
create_default_admin()
create_default_user()

# Create a regular test user if not exists
from app.db.session import SessionLocal
from app.models.user_model import User
from app.services.auth_service import get_password_hash
from app.core.enums import Role

db = SessionLocal()
try:
	user = db.query(User).filter(User.login == "testuser").first()
	if not user:
		user = User(
			login="testuser",
			full_name="Test User",
			role=Role.USER,
			email="testuser@example.com",
			password_hash=get_password_hash("password"),
			is_active=True,
		)
		db.add(user)
		db.commit()
		print("Test user created")
	else:
		print("Test user already exists")
finally:
	db.close()
