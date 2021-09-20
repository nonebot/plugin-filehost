from io import BytesIO
from pathlib import Path

from nonebot.adapters.cqhttp import Bot, MessageEvent, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command
from nonebot_plugin_filehost import FileHost, HostContextVarMiddleware

scope_browse = on_command(
    "current_scope", aliases={"当前Scope", "Scope"}, permission=SUPERUSER
)

request_browse = on_command(
    "current_request", aliases={"当前Request", "Request"}, permission=SUPERUSER
)

request_resource = on_command(
    "request_resource", aliases={"资源测试"}, permission=SUPERUSER
)


@scope_browse.handle()
async def _(bot: Bot, event: MessageEvent):
    await scope_browse.send(
        str(HostContextVarMiddleware.current_scope.get()),
    )


@request_browse.handle()
async def _(bot: Bot, event: MessageEvent):
    await request_browse.send(
        str(HostContextVarMiddleware.current_request.get()),
    )


@request_resource.handle()
async def _(bot: Bot, event: MessageEvent):
    res_path = Path(__file__).parent / "res.jpg"
    await request_resource.send(
        f"Start test file {res_path=} sending, content:"
        + MessageSegment.image(res_path, cache=False)
    )
    file_by_bytes = FileHost.new(res_path.read_bytes())
    await request_resource.send(
        "Send by filehost bytes type:"
        + MessageSegment.image(file_by_bytes.to_url(), cache=False)
    )
    file_by_bytes_io = FileHost.new(BytesIO(res_path.read_bytes()))
    await request_resource.send(
        "Send by filehost bytes io type:"
        + MessageSegment.image(file_by_bytes_io.to_url(), cache=False)
    )
    with open(res_path, "rb") as f:
        file_by_file_like = FileHost.new(f)
    await request_resource.send(
        "Send by filehost filelike type:"
        + MessageSegment.image(file_by_file_like.to_url(), cache=False)
    )
    file_by_path_obj = FileHost.new(res_path)
    await request_resource.send(
        "Send by filehost path object type:"
        + MessageSegment.image(file_by_path_obj.to_url(), cache=False)
    )
    file_by_str_path = FileHost.new(str(res_path))
    await request_resource.send(
        "Send by filehost str path type:"
        + MessageSegment.image(file_by_str_path.to_url(), cache=False)
    )
    await request_resource.send("Congratulations! All checks have passed!")
