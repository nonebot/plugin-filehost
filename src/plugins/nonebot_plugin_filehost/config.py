from typing import Optional

from nonebot.config import BaseConfig
from pydantic.fields import Field


class Config(BaseConfig):
    # Your Config Here
    FALLBACK_HOST: Optional[str] = Field(alias="filehost_fallback_host")

    class Config:
        extra = "ignore"
