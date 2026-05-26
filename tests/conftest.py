import os

# Ensure tests use testing mode
os.environ.setdefault("TESTING", "1")

# Create in-memory tables and default data for tests
from app.db.session import Base, engine
import app.models  # registers models with Base

Base.metadata.create_all(bind=engine)

# Create default units and admin user used by tests
from app.main import create_default_units, create_default_admin
create_default_units()
create_default_admin()
