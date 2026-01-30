from app.db.session import engine
from app.db import models


def create_tables():
    models.Base.metadata.create_all(bind=engine)
