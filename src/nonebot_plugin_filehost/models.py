from typing import Mapping, Optional, Sequence, Tuple

from nonebot.compat import PYDANTIC_V2
from pydantic import BaseModel, IPvAnyAddress
from starlette.datastructures import Headers
from typing_extensions import Literal


class RequestHeaders(Headers):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, Sequence) and all(
            map(lambda e: isinstance(e, Sequence), value)
        ):
            return cls(raw=value)  # type:ignore
        elif isinstance(value, Mapping):
            if all(map(lambda k: isinstance(k, str), value.keys())) and all(
                map(lambda v: isinstance(v, str), value.values())
            ):
                return cls(headers=value)
            else:
                return cls(scope=value)  # type:ignore
        raise ValueError("Invalid request headers.")


class RequestScopeInfo(BaseModel):
    """
    This is scope model for uvicorn

    Reference: https://www.uvicorn.org/#http-scope
    """

    if PYDANTIC_V2:
        from pydantic import ConfigDict

        model_config = ConfigDict(extra="allow")

    else:

        class Config:
            extra = "allow"

    asgi: Mapping[str, str]

    type: Literal["http", "websocket"]
    server: Tuple[IPvAnyAddress, int]
    client: Tuple[IPvAnyAddress, int]

    scheme: str
    method: Optional[str] = None
    http_version: Optional[str] = None
    root_path: str
    path: str
    headers: RequestHeaders
