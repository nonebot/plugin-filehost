import atexit
import shutil
from contextvars import ContextVar
from io import BufferedReader, BytesIO
from pathlib import Path
from secrets import token_urlsafe
from tempfile import TemporaryDirectory
from typing import Union
from urllib.parse import ParseResult, urljoin

from fastapi.staticfiles import StaticFiles
from nonebot import get_driver
from nonebot.drivers.fastapi import Driver as FastAPIDriver
from nonebot.log import logger
from nonebot.plugin.export import export
from pydantic.main import BaseModel, Extra
from starlette.types import ASGIApp, Receive, Scope, Send

from .config import Config, LinkType
from .models import RequestScopeInfo

driver = get_driver()


if not isinstance(driver, FastAPIDriver):
    raise ValueError("FileHost supports FastAPI driver only")

hosting_config = Config.parse_obj(driver.config.dict())
export_namespace = export()

temporary_dir = TemporaryDirectory(prefix="filehost-")


@export_namespace
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
                logger.opt(colors=True).trace(f"Request info: <e>{request_info}</e>")
            except Exception:
                logger.exception(f"Scope {scope=} deserialize failed:")
            else:
                type(self).current_request.set(request_info)
        await self.app(scope, receive, send)


driver.server_app.add_middleware(HostContextVarMiddleware)
driver.server_app.mount(
    path="/filehost",
    app=StaticFiles(directory=temporary_dir.name),
    name="filehost",
)


def cleanup():
    logger.debug(f"Exit singal received, Start cleaning up {temporary_dir}")
    temporary_dir.cleanup()


atexit.register(cleanup)


@export_namespace
class FileHost(BaseModel):
    @staticmethod
    def new(source: Union[BytesIO, BufferedReader, Path, bytes, str]):
        file_id = token_urlsafe()
        tmpfile_path = Path(temporary_dir.name) / file_id

        if isinstance(source, BytesIO):
            content = source.getvalue()
            tmpfile_path.write_bytes(content)
        elif isinstance(source, bytes):
            tmpfile_path.write_bytes(source)
        else:
            file_path = (
                source
                if isinstance(source, Path)
                else Path(
                    source.name if isinstance(source, BufferedReader) else str(source)
                )
            ).absolute()
            if not file_path.is_file():
                raise ValueError(f"Input source={source!r} is not a valid file!")
            if not hosting_config.LINK_FILE:
                shutil.copyfile(file_path, tmpfile_path)
            else:
                link_limit = (
                    0 if hosting_config.LINK_FILE is True else hosting_config.LINK_FILE
                )
                if file_path.stat().st_size >= link_limit:
                    try:
                        if hosting_config.LINK_TYPE is LinkType.hard:
                            file_path.link_to(tmpfile_path)
                        else:
                            file_path.symlink_to(tmpfile_path)
                    except OSError as e:
                        logger.opt(colors=True).warning(
                            f"FileHost failed to create "
                            f"<y>{hosting_config.LINK_TYPE.value}</y> link: "
                            f"<r><b>errno={e.errno}</b> {e.strerror}</r>, "
                            "fallback to copy file."
                        )
                        shutil.copyfile(file_path, tmpfile_path)
                else:
                    shutil.copyfile(file_path, tmpfile_path)

        return FileHost(id=file_id, path=tmpfile_path)

    id: str
    path: Path

    class Config:
        allow_mutation = False
        extra = Extra.forbid

    def to_url(self) -> str:
        request = HostContextVarMiddleware.current_request.get(None)
        if (request is None) or ("host" not in request.headers):
            if hosting_config.FALLBACK_HOST is None:
                raise ValueError(
                    "No fallback host specified, "
                    "and current request has no host header."
                )
            base_url = urljoin(hosting_config.FALLBACK_HOST, f"/filehost/{self.id}")
        else:
            base_url = ParseResult(
                scheme={
                    "ws": "http",
                    "wss": "https",
                    "http": "http",
                    "https": "https",
                }.get(request.scheme, "http"),
                netloc=request.headers["host"],
                path=f"/filehost/{self.id}",
                params="",
                query="",
                fragment="",
            ).geturl()
        return base_url


__all__ = ["FileHost", "HostContextVarMiddleware"]
