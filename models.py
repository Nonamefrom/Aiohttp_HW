import atexit
import datetime
import os

from sqlalchemy import DateTime, Integer, String, create_engine, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker

POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
POSTGRES_DB = os.getenv("POSTGRES_DB", "netology")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

PG_DSN = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(PG_DSN)


def on_exit():
    print("exit")
    engine.dispose()


atexit.register(on_exit)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    heading: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    make_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    @property
    def dict(self):
        return {
            "id": self.id,
            "heading": self.heading,
            "description": self.description,
            "owner": self.owner,
            "make_time": self.make_time.isoformat(),
        }

# Создание всех таблиц
Base.metadata.create_all(bind=engine)
