import shutil
import sys
from contextvars import ContextVar
from io import BufferedReader, BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union
from urllib.parse import ParseResult, urljoin
from uuid import uuid4

import anyio.to_thread
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from nonebot import get_driver, logger
from nonebot.drivers import ASGIMixin
from nonebot.plugin import PluginMetadata
from starlette.types import ASGIApp, Receive, Scope, Send

from .models import RequestScopeInfo
from .plugin_config import FileHostConfig, LinkKind, config

__plugin_meta__ = PluginMetadata(
    name="文件托管支持",
    description="提供跨机文件传输支持，通过 HTTP 服务托管文件",
    usage="见文档 (https://github.com/nonebot/plugin-filehost#readme)",
    type="library",
    homepage="https://github.com/nonebot/plugin-filehost",
    config=FileHostConfig,
    supported_adapters=None,
)

driver = get_driver()


temporary_dir = TemporaryDirectory(prefix="filehost-", dir=config.filehost_tmp_dir)


class HostContextVarMiddleware:
    current_scope: ContextVar[Scope] = ContextVar("current_scope")
    current_request: ContextVar[RequestScopeInfo] = ContextVar("current_request")

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if config.filehost_host_override is None and scope["type"] in {
            "http",
            "websocket",
        }:
            type(self).current_scope.set(scope)
            try:
                request_info = RequestScopeInfo.parse_obj(scope)
                logger.opt(colors=True).trace(f"Request info: <e>{request_info}</e>")
            except Exception:
                logger.exception(f"Scope {scope=} deserialize failed:")
            else:
                type(self).current_request.set(request_info)
        await self.app(scope, receive, send)


if isinstance(driver, ASGIMixin) and isinstance((app := driver.server_app), FastAPI):
    app.add_middleware(HostContextVarMiddleware)
    app.mount(
        path="/filehost",
        app=StaticFiles(directory=temporary_dir.name),
        name="filehost",
    )
else:
    logger.warning("FileHost plugin only works with fastapi driver.")


@driver.on_shutdown
def cleanup():
    logger.debug(f"Cleaning up temporary directory {temporary_dir.name}...")
    temporary_dir.cleanup()


FileHostSupportedTypes = Union[BytesIO, BufferedReader, Path, bytes, str]


class FileHost:
    def __init__(
        self,
        source: FileHostSupportedTypes,
        suffix: str = "",
        filename: Optional[str] = None,
    ) -> None:
        self.source = source
        self.id = uuid4()
        self.filename = filename or f"{self.id}{suffix}"
        self.file_dir = Path(temporary_dir.name) / self.filename

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.id=} {self.filename=}>"

    def to_url_sync(self):
        """
        使用同步 I/O 获取文件托管的 URL。

        NOTE: 这个方法可能会阻塞事件循环，请不要在异步上下文中调用。
        """
        if isinstance(self.source, bytes):
            file_size = self._bytes_handler(self.source)
        elif isinstance(self.source, BytesIO):
            file_size = self._bytes_io_handler(self.source)
        elif isinstance(self.source, Path):
            file_size = self._path_handler(self.source)
        elif isinstance(self.source, BufferedReader):
            file_size = self._buffered_reader_handler(self.source)
        elif isinstance(self.source, str):
            file_size = self._path_handler(Path(self.source))
        else:
            raise ValueError(f"Unsupported source type: {type(self.source)}")

        logger.trace(f"File host {self.id=} created, {file_size=}")
        return self._generate_url()

    async def to_url(self):
        """
        获取文件托管的 URL。
        """
        if isinstance(self.source, bytes):
            file_size = await self._async_bytes_handler(self.source)
        elif isinstance(self.source, BytesIO):
            file_size = await self._async_bytes_io_handler(self.source)
        elif isinstance(self.source, Path):
            file_size = await self._async_path_handler(self.source)
        elif isinstance(self.source, BufferedReader):
            file_size = await self._async_buffered_reader_handler(self.source)
        elif isinstance(self.source, str):
            file_size = await self._async_path_handler(Path(self.source))
        else:
            raise ValueError(f"Unsupported source type: {type(self.source)}")

        logger.trace(f"File host {self.id=} created, {file_size=}")
        return self._generate_url()

    def _generate_url(self):
        if config.filehost_host_override is not None:
            base_url = urljoin(
                str(config.filehost_host_override), f"./filehost/{self.filename}"
            )
        elif request := HostContextVarMiddleware.current_request.get(None):
            base_url = ParseResult(
                scheme=(
                    {
                        "ws": "http",
                        "wss": "https",
                        "http": "http",
                        "https": "https",
                    }.get(request.scheme, "http")
                ),
                netloc=request.headers["host"],
                path=f"/filehost/{self.filename}",
                params="",
                query="",
                fragment="",
            ).geturl()
        else:
            raise ValueError(
                "No override host specified, and current request has no host header found."
            )
        return base_url

    def _bytes_handler(self, source: bytes):
        return self.file_dir.write_bytes(source)

    async def _async_bytes_handler(self, source: bytes):
        async with await anyio.open_file(self.file_dir, "wb") as f:
            return await f.write(source)

    def _bytes_io_handler(self, source: BytesIO):
        return self._bytes_handler(source.getvalue())

    async def _async_bytes_io_handler(self, source: BytesIO):
        return await self._async_bytes_handler(source.getvalue())

    def _path_handler(self, source: Path):
        file_size = source.stat().st_size

        if config.filehost_link_file is False or (
            isinstance(config.filehost_link_file, int)
            and file_size >= config.filehost_link_file
        ):
            shutil.copyfile(source, self.file_dir)
        else:
            try:
                if config.filehost_link_type is LinkKind.hard:
                    # NOTE: https://bugs.python.org/issue39950
                    if sys.version_info >= (3, 10):
                        source.hardlink_to(self.file_dir)
                    else:
                        source.link_to(self.file_dir)
                elif config.filehost_link_type is LinkKind.symbolic:
                    source.symlink_to(self.file_dir)
            except OSError as e:
                logger.opt(colors=True).warning(
                    f"FileHost failed to create "
                    f"<y>{config.filehost_link_type.value}</y> <r>{e}</r>, "
                    "fallback to copy file."
                )
                shutil.copyfile(source, self.file_dir)
        return file_size

    async def _async_path_handler(self, source: Path):
        return await anyio.to_thread.run_sync(self._path_handler, source)

    def _buffered_reader_handler(self, source: BufferedReader):
        return self._path_handler(Path(source.name))

    async def _async_buffered_reader_handler(self, source: BufferedReader):
        return await self._async_path_handler(Path(source.name))


__all__ = ["FileHost"]
