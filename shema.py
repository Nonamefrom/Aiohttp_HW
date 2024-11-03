import datetime

from pydantic import BaseModel, field_validator


class BaseAdvertisement(BaseModel):
    heading: str | None = None
    description: str | None = None
    owner: str | None = None
    @field_validator("heading", "description", "owner", mode="before")
    @classmethod
    def check_field(cls, value: str):
        if value is not None and len(value) < 1:
            raise ValueError("Field can not be empty!")
        return value


class CreateAdvertisement(BaseAdvertisement):
    heading: str
    description: str
    owner: str


class DeleteAdvertisement(BaseAdvertisement):
    id: int
    heading: str
    description: str
    owner: str
    make_time: datetime.datetime
