# Server 模块

Server 模块是系统的总入口，所有的访问请求都从这里经过并分发到相应的处理模块。基于 FastAPI 构建，提供 HTTP 服务器功能。

## 文件结构

```
server/
├── __init__.py           # 空文件
├── main.py              # 主服务器文件，FastAPI 应用入口
├── translate.py         # 请求转换和解析模块
├── assets_support.py    # 静态资源支持模块
└── README.MD            # 本文档
```

## 核心组件

### 1. 主服务器 (`main.py`)

基于 FastAPI 的 HTTP 服务器，提供以下功能：

#### 应用配置

```python
app = FastAPI(title="Note Server", version="0.1.0")
```

#### 启动和关闭事件

- **启动事件**：初始化备份系统
- **关闭事件**：停止备份系统

#### CORS 配置

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 路由定义

- **健康检查**：`GET /health`
- **静态资源**：`GET /assets/{path:path}`
- **API 接口**：`GET/POST /api/{path:path}`
- **通用访问**：`GET/POST /{path:path}`

### 2. 请求转换 (`translate.py`)

负责将 HTTP 请求转换为系统内部的 Access 对象。

#### 主要功能

- **访问类型检测** - 判断是 API、Web 还是其他类型请求
- **访问者类型检测** - 识别 user、script、agent 等访问者
- **请求解析** - 解析路径、查询参数、cookies 等
- **参数插值** - 支持从请求体中进行参数插值

#### 核心函数

##### `detect_by(request)`

通过请求头判断访问类型：

```python
def detect_by(request: Request):
    # 检查 query 参数
    from_param = request.query_params.get("from", "").lower()
    
    # 检查 User-Agent 等请求头
    user_agent = request.headers.get("user-agent", "").lower()
    content_type = request.headers.get("content-type", "").lower()
    accept = request.headers.get("accept", "").lower()
    
    # 返回 Access.API 或 Access.Web
```

##### `detect_who(request)`

识别访问者类型：

```python
def detect_who(request: Request):
    # 检查 role 参数
    role_param = request.query_params.get("role", "").lower()
    
    # 根据 User-Agent 等判断
    # 返回 "user", "script", "agent" 等
```

##### `request2access(request, ...)`

将 HTTP 请求转换为 Access 对象：

```python
def request2access(
    request: Request,
    path: str | None = None,
    mime: str | None = None,
    entry: str | None = None,
    who: str | None = None,
    by: str | None = None,
) -> Access:
    # 解析路径信息
    # 确定 entry 和 mime
    # 合并查询参数
    # 返回 Access 对象
```

##### `replaceByBody(pack, body_or_request)`

处理请求体中的参数插值：

```python
async def replaceByBody(pack, body_or_request):
    # 解析请求体
    # 替换查询参数中的 $ 变量
    # 替换 cookies 中的 $ 变量
    # 返回处理后的 pack
```

### 3. 静态资源支持 (`assets_support.py`)

管理前端构建后的静态资源文件。

#### 主要功能

- **目录扫描** - 自动扫描 Express 模块中的 assets 目录
- **资源服务** - 提供静态资源文件服务
- **MIME 类型检测** - 根据文件扩展名确定 MIME 类型

#### 核心函数

##### `scan_assets_directories()`

扫描并初始化 assets 目录：

```python
def scan_assets_directories():
    # 扫描 Express/*/dist/assets 目录
    # 存储到全局变量 ASSETS_DIRS
    # 打印扫描结果
```

##### `serve(path)`

提供静态资源文件服务：

```python
def serve(path: str):
    # 在扫描到的目录中查找文件
    # 确定 MIME 类型
    # 返回 FileResponse
```

## 请求处理流程

### 1. 请求接收

```python
# 服务器接收 HTTP 请求
@app.get("/{path:path}")
async def visit_get(request: Request):
    return await visit(request2access(request))
```

### 2. 请求转换

```python
# 将 HTTP 请求转换为 Access 对象
pack = request2access(request)
```

### 3. 内部处理

```python
# 调用内部处理函数
return await visit(pack)
```

### 4. 分发处理

```python
# 在 visit_internal 中进行分发
def visit_internal(pack):
    mime = first_avail(pack.mime, getmime(pack.entry), "text")
    Dispatcher = Port.dispatch(mime)
    
    # Meta 脚本处理逻辑
    if Dispatcher == Port.Text and pack.mime and pack.mime != "text":
        # 检查并执行 Meta 脚本
    
    # 执行 Port 处理
    output = Dispatcher.access(pack)
    return output.value if output.skip else wrap(output)
```

## 路由详解

### 1. 健康检查

```http
GET /health
```

返回服务器状态信息：

```json
{
  "status": "ok"
}
```

### 2. 静态资源

```http
GET /assets/{path:path}
```

提供前端构建后的静态资源文件，如 CSS、JS、图片等。

### 3. API 接口

```http
GET /api/{path:path}
POST /api/{path:path}
```

API 接口，自动识别为 API 请求类型。

### 4. 通用访问

```http
GET /{path:path}
POST /{path:path}
```

通用访问接口，支持所有类型的请求。

## 请求类型检测

### API 请求特征

- `from=api` 查询参数
- `application/json` 内容类型
- 命令行工具 User-Agent（curl, wget 等）
- 编程语言 HTTP 客户端
- 移动端 API 请求

### Web 请求特征

- `from=web` 查询参数
- 浏览器 User-Agent
- `text/html` Accept 头
- 完整的浏览器标识

### 访问者类型

- **user** - 真实用户浏览器
- **script** - 脚本和命令行工具
- **agent** - 程序化访问和开发工具

## 参数插值

支持在查询参数和 cookies 中使用 `$` 前缀进行参数插值：

```python
# 查询参数
pack.query = {"name": "$username"}

# 请求体
body = {"username": "john"}

# 插值后
pack.query = {"name": "john"}
```

## 错误处理

### 1. 路由错误

- 404 错误由 FastAPI 自动处理
- 返回标准的 JSON 错误响应

### 2. 处理错误

- Port 处理错误返回错误信息
- 脚本执行错误返回详细错误堆栈

### 3. 资源错误

- 静态资源不存在返回 404
- 文件读取错误返回 500

## 配置选项

### 1. CORS 配置

```python
allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### 2. 备份系统配置

```python
init_backup_system(
    backup_dir="src/Database/.backup",
    max_backups=10,
    backup_interval=60,
    format="toml"
)
```

## 部署和运行

### 1. 开发模式

```bash
# 使用 uvicorn 运行
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 生产模式

```bash
# 使用 gunicorn 运行
gunicorn src.server.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 3. Docker 部署

```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "src.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 性能优化

### 1. 静态资源缓存

- 设置适当的缓存头
- 使用 CDN 加速静态资源

### 2. 请求处理优化

- 异步处理请求
- 连接池管理
- 请求压缩

### 3. 内存管理

- 定期清理缓存
- 监控内存使用
- 优化数据结构

## 安全考虑

### 1. 输入验证

- 验证所有输入参数
- 防止路径遍历攻击
- 限制请求大小

### 2. 访问控制

- 区分不同类型的访问者
- 限制敏感操作
- 记录访问日志

### 3. 错误信息

- 避免泄露敏感信息
- 统一错误响应格式
- 记录详细错误日志

## 监控和日志

### 1. 访问日志

```python
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    return response
```

### 2. 性能监控

- 请求处理时间
- 内存使用情况
- 错误率统计

### 3. 健康检查

- 数据库连接状态
- 备份系统状态
- 资源使用情况

## 扩展

### 1. 添加新的路由

```python
@app.get("/custom/{path:path}")
async def custom_handler(request: Request):
    # 自定义处理逻辑
    pass
```

### 2. 添加中间件

```python
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # 自定义中间件逻辑
    response = await call_next(request)
    return response
```

### 3. 添加新的请求类型检测

```python
def detect_custom_type(request: Request):
    # 自定义检测逻辑
    return "custom"
```

## 故障排除

### 1. 常见问题

- **端口被占用** - 检查端口使用情况
- **静态资源 404** - 检查 assets 目录扫描
- **CORS 错误** - 检查 CORS 配置
- **备份失败** - 检查备份目录权限

### 2. 调试技巧

- 启用详细日志
- 使用调试模式运行
- 检查请求头信息
- 验证路径解析

### 3. 性能问题

- 监控请求处理时间
- 检查内存使用
- 分析慢查询
- 优化静态资源加载