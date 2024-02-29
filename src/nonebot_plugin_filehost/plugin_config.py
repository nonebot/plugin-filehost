from enum import Enum
from pathlib import Path
from typing import Optional, Union

from nonebot import get_plugin_config
from pydantic import AnyHttpUrl, BaseModel, PositiveInt


class LinkKind(str, Enum):
    hard = "hard"
    symbolic = "symbolic"


class FileHostConfig(BaseModel):
    filehost_host_override: Optional[AnyHttpUrl] = None

    filehost_link_file: Union[PositiveInt, bool] = True
    filehost_link_type: LinkKind = LinkKind.hard

    filehost_tmp_dir: Optional[Path] = None


config = get_plugin_config(FileHostConfig)
