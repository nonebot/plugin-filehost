# nonebot-plugin-filehost

> **NoneBot2 的 HTTP 静态文件托管插件，为跨机文件传输提供了优雅的解决方案**

---

## 优势

- 跨机器, 跨网络支持, 只要反向WebSocket可以正常连接, 它就可以使用

- 使用临时文件作为中转, 内存占用低
  - 临时文件会尝试采用硬链接方式创建, 快速且可靠
  - 临时文件在程序退出时会自动删除, 不会永久占用空间
  
- 自动检测访问来源生成资源URL, 无需手动配置

## 开始使用

### 安装插件

- 如果使用了`nb-cli`

```shell
nb plugin install nonebot-plugin-filehost
```

- 或者手动安装:

  - 使用你的包管理器(如`pip`)安装`nonebot-plugin-filehost`:

    ```shell
    pip install nonebot-plugin-filehost
    ```

  - 修改`pyproject.toml`文件(推荐)

    ```diff
    [nonebot.plugins]
    - plugins = []
    + plugins = ["nonebot_plugin_filehost"]
    plugin_dirs = ["src/plugins"]
    ```

  - 修改`bot.py`文件, 添加一行:
  
    ```diff
    driver = nonebot.get_driver()
    driver.register_adapter("cqhttp", CQHTTPBot)

    nonebot.load_from_toml("pyproject.toml")
    + nonebot.load_plugin('nonebot_plugin_filehost')
    ```

### 使用插件

- 请前往[示例插件](./src/plugins/testing/__init__.py)进行查看

## 开源许可

本项目采用[MIT许可](./LICENSE)
