# serializers for https://api.sejm.gov.pl/eli/
from enum import Enum

from pydantic import BaseModel, Field


class PublisherCode(str, Enum):
    DU = "DU"
    MP = "MP"


class ActInfo(BaseModel):
    address: str  # WDU20170002196
    publisher: str
    year: int
    pos: int
    volume: int
    title: str
    display_address: str = Field(alias="displayAddress")
    promulgation: str | None = Field(default=None)
    announcement_date: str | None = Field(alias="announcementDate", default=None)
    text_pdf: bool = Field(alias="textPDF")
    text_html: bool = Field(alias="textHTML")
    change_date: str = Field(alias="changeDate")
    eli: str = Field(alias="ELI")
    type: str
    status: str


class ActsInYear(BaseModel):
    items: list[ActInfo] = []
