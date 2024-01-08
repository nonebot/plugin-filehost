# nonebot-plugin-filehost

> **NoneBot2 的 HTTP 静态文件托管插件，为跨机文件传输提供解决方案**

[![PyPI](https://img.shields.io/pypi/v/nonebot-plugin-filehost?style=for-the-badge)](https://pypi.org/project/nonebot-plugin-filehost/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nonebot-plugin-filehost?style=for-the-badge)

[![GitHub issues](https://img.shields.io/github/issues/nonebot/plugin-filehost)](https://github.com/nonebot/plugin-filehost/issues)
[![GitHub stars](https://img.shields.io/github/stars/nonebot/plugin-filehost)](https://github.com/nonebot/plugin-filehost/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/nonebot/plugin-filehost)](https://github.com/nonebot/plugin-filehost/network)
[![GitHub license](https://img.shields.io/github/license/nonebot/plugin-filehost)](https://github.com/nonebot/plugin-filehost/blob/main/LICENSE)

---

## 优势

- 跨机器, 跨网络支持, 只要反向 WebSocket 可以正常连接, 它就可以使用
- 使用临时文件作为中转, 内存占用低
  - 临时文件会尝试采用硬链接方式创建, 快速且可靠
  - 临时文件在程序退出时会自动删除, 不会永久占用空间
- 自动检测访问来源生成资源 URL, 无需手动配置

## 开始使用

### 安装插件

请使用 NoneBot CLI 进行安装:

```shell
nb plugin install nonebot-plugin-filehost
```

### 进行配置

本插件支持以下配置项

- `FILEHOST_HOST_OVERRIDE`：用于覆盖自动检测的访问来源, 例如 `http://example.com:8080/`， 在反向 WebSocket 连接 Host 和公网 Host 不一致时使用
- `FILEHOST_LINK_FILE`：使用文件系统链接代替文件复制, 可以提升临时文件创建速度

  - 默认为`True`,同时支持`bool`和`int`类型
    - 当为`bool`时, 无条件启用链接
    - 当为`int`时, 当文件**字节数**大于或等于该数时启用链接, 低于时使用复制

- `FILEHOST_LINK_TYPE`

  - 指定使用的链接类型, 有`hard`和`soft`两个可选值
    - `hard`: 建立硬链接
    - `symbolic`: 建立软链接
  - 默认为`hard`

- `FILEHOST_TMP_DIR`：临时文件存放目录, 默认为操作系统的临时目录

### 在代码中使用

托管已有文件：

```python
from pathlib import Path
from nonebot_plugin_filehost import FileHost

url = await FileHost(Path("/path/to/your/file")).to_url()
```

托管 `bytes` 或者 `BytesIO`：

```python
from nonebot_plugin_filehost import FileHost

url = await FileHost(some_bytes).to_url()
```

使用同步代码：

```python
url = FileHost().to_url_sync()
```

### TODO

- [ ] 支持自定义文件服务访问路径
- [ ] 支持对 URL 进行读取，进行中转

## 开源许可

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

本项目使用 MIT 开源许可证进行许可, 详细信息请参阅 [LICENSE](./LICENSE) 文件。
