# 🦖 Pterodactyl 文件管理器（点个小星星呗）

一个轻量级的 Pterodactyl 面板文件管理 Web 界面。

**配置保存在浏览器本地 (localStorage)，服务器不保存任何用户数据。**

## 停机自启功能已被移除
可以移步到：https://github.com/fascmer/ptero-monitor

## 功能

- 📂 文件列表浏览
- 📁 文件夹导航
- ✏️ 在线编辑文件
- ⬇️ 下载文件
- ⬆️ 上传文件
- 🗑️ 删除文件/文件夹
- 📝 重命名文件/文件夹
- 📁 新建文件/文件夹

## 快速开始

<img width="1167" height="631" alt="image" src="https://github.com/user-attachments/assets/62fc8e97-5bab-40d7-8ccc-90476a70f15d" />


### Docker 运行

```bash
docker run -d -p 8000:8000 ghcr.io/YOUR_USERNAME/pterodactyl-manager:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  pterodactyl-manager:
    image: ghcr.io/YOUR_USERNAME/pterodactyl-manager:latest
    ports:
      - "8000:8000"
    restart: unless-stopped
```

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python3 server.py

# 或指定端口
PORT=3000 python3 server.py
```

## 配置

在 Web 界面中配置:

| 参数 | 说明 | 示例 |
|------|------|------|
| API 地址 | Pterodactyl API 基础地址 | `https://panel.example.com/api/client/servers` |
| Server ID | 服务器 ID | `abc12345` |
| API Key | API 密钥 | `ptlc_xxxxxxxxxxxx` |

配置保存在浏览器的 localStorage 中，刷新页面后仍会保留。

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | `8000` | 监听端口 |

## 许可证

MIT License

## 免责声明
本项目仅用于学习、研究和交流目的，不用于任何商业用途。项目中所涉及的代码、数据、文档及其他相关内容，均不代表作者或相关方的正式立场或建议。
使用者基于本项目所进行的任何操作、修改、部署或应用，均需自行承担全部责任与风险。作者不对因使用本项目内容而引发的任何直接或间接损失、损害或法律责任承担任何责任。
如涉及第三方知识产权或其他合法权益，请权利人及时联系作者，我们将尽快处理。
