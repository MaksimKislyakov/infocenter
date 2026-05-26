import os

os.environ.setdefault("TESTING", "1")

from app.db.session import Base, engine
import app.models

Base.metadata.create_all(bind=engine)

from app.main import create_default_units, create_default_admin
create_default_units()
create_default_admin()
