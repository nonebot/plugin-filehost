# nonebot-plugin-filehost

> **NoneBot2 的 HTTP 静态文件托管插件，为跨机文件传输提供了优雅的解决方案**

[![PyPI](https://img.shields.io/pypi/v/nonebot-plugin-filehost?style=for-the-badge)](https://pypi.org/project/nonebot-plugin-filehost/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nonebot-plugin-filehost?style=for-the-badge)

[![GitHub issues](https://img.shields.io/github/issues/mnixry/nonebot-plugin-filehost)](https://github.com/mnixry/nonebot-plugin-filehost/issues)
[![GitHub stars](https://img.shields.io/github/stars/mnixry/nonebot-plugin-filehost)](https://github.com/mnixry/nonebot-plugin-filehost/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mnixry/nonebot-plugin-filehost)](https://github.com/mnixry/nonebot-plugin-filehost/network)
[![GitHub license](https://img.shields.io/github/license/mnixry/nonebot-plugin-filehost)](https://github.com/mnixry/nonebot-plugin-filehost/blob/main/LICENSE)
![Lines of code](https://img.shields.io/tokei/lines/github/mnixry/nonebot-plugin-filehost)

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

### 进行配置

本插件支持以下配置项

- `FILEHOST_FALLBACK_HOST`
  - 当请求不包含`Host`头或者上下文变量序列化失败时使用的主机地址
  - 默认为`None`, 示例值为`http://localhost:8080`
  
- `FILEHOST_LINK_FILE`
  - 使用文件系统链接代替文件复制, 可以提升临时文件创建速度
  - 默认为`True`,同时支持`bool`和`int`类型
    - 当为`bool`时, 无条件启用链接
    - 当为`int`时, 当文件字节数大于或等于该数时启用链接, 低于时使用复制

- `FILEHOST_LINK_TYPE`
  - 指定使用的链接类型, 有`hard`和`soft`两个可选值
    - `hard`: 建立硬链接
    - `soft`: 链接软链接 (符号链接)
  - 默认为`hard`

## 开源许可

本项目采用[MIT许可](./LICENSE)
