# import nonebot
from contextvars import ContextVar
from typing import Mapping, Optional, Sequence, Tuple

from nonebot import get_driver
from nonebot.drivers.fastapi import Driver as FastAPIDriver
from nonebot.log import logger
from pydantic import BaseModel, Extra, IPvAnyAddress
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send
from typing_extensions import Literal

from .config import Config

driver = get_driver()

if not isinstance(driver, FastAPIDriver):
    raise ValueError("Now filehost only support fastapi driver")

config = Config.parse_obj(driver.config.dict())


# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass


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

    class Config:
        extra = Extra.allow

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


class HostContextVarMiddleware:
    current_scope: ContextVar[Scope] = ContextVar("current_scope")
    current_request: ContextVar[RequestScopeInfo] = ContextVar("current_request")

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        type(self).current_scope.set(scope)
        if scope["type"] in {"http", "websocket"}:
            try:
                request_info = RequestScopeInfo.parse_obj(scope)
                logger.opt(colors=True).debug(f"Request info: <e>{request_info}</e>")
            except Exception:
                logger.exception(f"Scope {scope=} deserialize failed:")
            else:
                type(self).current_request.set(request_info)
        await self.app(scope, receive, send)


driver.server_app.add_middleware(HostContextVarMiddleware)
