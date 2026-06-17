import unittest

import nonebot
from nonebot.compat import type_validate_python


try:
    nonebot.get_driver()
except ValueError:
    nonebot.init(driver="~fastapi")


class RequestScopeInfoTest(unittest.TestCase):
    def test_websocket_scope_accepts_raw_headers(self):
        from nonebot_plugin_filehost.models import RequestScopeInfo

        scope = {
            "type": "websocket",
            "asgi": {"version": "3.0", "spec_version": "2.4"},
            "http_version": "1.1",
            "scheme": "ws",
            "server": ("192.168.10.72", 8080),
            "client": ("192.168.0.5", 35322),
            "root_path": "",
            "path": "/onebot/v11/ws",
            "raw_path": b"/onebot/v11/ws",
            "query_string": b"",
            "headers": [
                (b"x-self-id", b"2043440173"),
                (b"authorization", b"Bearer 1145141919810123456"),
                (b"x-client-role", b"Universal"),
                (b"user-agent", b"OneBot/11"),
                (b"connection", b"Upgrade"),
                (b"upgrade", b"websocket"),
                (b"host", b"192.168.10.72:8080"),
            ],
            "subprotocols": [],
            "state": {},
            "extensions": {"websocket.http.response": {}},
            "app": object(),
        }

        request = type_validate_python(RequestScopeInfo, scope)

        self.assertEqual(request.type, "websocket")
        self.assertEqual(request.scheme, "ws")
        self.assertEqual(request.headers["host"], "192.168.10.72:8080")
