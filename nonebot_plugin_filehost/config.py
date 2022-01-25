from typing import Optional, Union
from enum import Enum

from nonebot.config import BaseConfig
from pydantic.fields import Field
from pydantic import PositiveInt, AnyHttpUrl


class LinkType(str, Enum):
    hard = "hard"
    soft = "soft"


class Config(BaseConfig):
    FALLBACK_HOST: Optional[AnyHttpUrl] = Field(env="filehost_fallback_host")
    LINK_FILE: Union[PositiveInt, bool] = Field(True, env="filehost_link_file")
    LINK_TYPE: LinkType = Field(LinkType.hard, env="filehost_link_type")

    class Config:
        extra = "ignore"
