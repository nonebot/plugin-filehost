from enum import Enum
from pathlib import Path
from typing import Optional, Union

from nonebot.config import BaseConfig
from pydantic import AnyHttpUrl, PositiveInt
from pydantic.fields import Field


class LinkKind(str, Enum):
    hard = "hard"
    symbolic = "symbolic"


class Config(BaseConfig):
    HOST_OVERRIDE: Optional[AnyHttpUrl] = Field(None, env="filehost_host_override")

    LINK_FILE: Union[PositiveInt, bool] = Field(True, env="filehost_link_file")
    LINK_TYPE: LinkKind = Field(LinkKind.hard, env="filehost_link_type")

    TMP_DIR: Optional[Path] = Field(env="filehost_tmp_dir")
