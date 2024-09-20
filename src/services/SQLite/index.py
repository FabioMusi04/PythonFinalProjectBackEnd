from sqlalchemy import create_engine

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

from src.api.users.model import Base
Base.metadata.create_all(bind=engine)