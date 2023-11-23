from enum import Enum
from typing import Optional, Union

from nonebot.config import BaseConfig
from pydantic import AnyHttpUrl, PositiveInt
from pydantic.fields import Field


class LinkKind(str, Enum):
    hard = "hard"
    soft = "soft"


class Config(BaseConfig):
    FALLBACK_HOST: Optional[AnyHttpUrl] = Field(env="filehost_fallback_host")
    LINK_FILE: Union[PositiveInt, bool] = Field(True, env="filehost_link_file")
    LINK_TYPE: LinkKind = Field(LinkKind.hard, env="filehost_link_type")

    class Config:
        extra = "ignore"
