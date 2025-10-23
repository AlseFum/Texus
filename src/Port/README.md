# Port 模块

Port 模块是系统的核心处理层，负责管理所有内容的提取与分发过程。它提供了多种 Port 类型来处理不同类型的数据和请求。

## 文件结构

```
Port/
├── __init__.py           # 主入口文件，提供分发和路由功能
├── Text.py              # 文本处理 Port
├── Meta.py              # Meta 脚本处理 Port
├── Exec.py              # 脚本执行 Port
├── Gen/                 # 生成器 Port
│   ├── __init__.py      # Gen 模块入口
│   ├── parser.py        # 语法解析器
│   ├── generator.py     # 内容生成器
│   ├── file.py          # 文件处理
│   ├── Syntax.md        # 语法文档
│   ├── AST.md           # AST 文档
│   └── README.md        # Gen 模块文档
└── README.md            # 本文档
```

## 核心概念

### Port 系统

Port 是处理特定类型请求的处理器，每个 Port 都实现了 `access(pack)` 方法来处理请求。

### 分发机制

系统通过 `dispatch(which)` 函数根据 MIME 类型或请求类型选择合适的 Port：

```python
from Port import dispatch

# 根据类型获取对应的 Port
port = dispatch("text")    # 返回 Text Port
port = dispatch("meta")    # 返回 Meta Port
port = dispatch("gen")     # 返回 Gen Port
port = dispatch("raw")     # 返回 Raw Port
```

## Port 类型详解

### 1. Text Port (`Text.py`)

处理文本数据的标准 Port，提供文本的读取、写入和 API 访问功能。

#### 主要方法

- `get_data(entry_key)` - 从数据库获取文本数据
- `getByWeb(pack)` - Web 方式获取文本
- `getByApi(pack)` - API 方式获取文本
- `set(pack)` - 设置文本内容
- `access(pack)` - 主访问方法

#### 使用示例

```python
from Port import Text
from protocol.types import Access

# 创建访问包
pack = Access(
    who="user",
    by="web", 
    path="/my-text",
    query={"op": "get"},
    cookies={},
    mime="text",
    entry="my-text"
)

# 处理请求
result = Text.access(pack)
```

### 2. Meta Port (`Meta.py`)

处理 Meta 脚本的 Port，支持脚本执行和动态内容生成。

#### 主要功能

- **脚本执行** - 执行存储在数据库中的脚本
- **数据传递** - 将源数据作为 `input_data` 传递给脚本
- **安全执行** - 提供安全的脚本执行环境
- **结果提取** - 提取脚本的 print 输出

#### 使用示例

```python
# 访问 /source.script 会：
# 1. 获取 source 的内容作为 input_data
# 2. 执行 script 中的脚本
# 3. 返回脚本的输出

# script 内容示例：
"""
print(f"Processing: {input_data}")
print("Script completed")
"""
```

#### 可用变量

脚本执行环境中提供以下变量：

- `input_data` - 源数据内容
- `request` - 完整的请求对象
- `db` - 数据库 API
- `re` - 正则表达式模块

### 3. Exec Port (`Exec.py`)

提供安全的脚本执行环境，专门用于执行用户脚本。

#### 主要功能

- **安全执行** - 限制可用的内置函数
- **数据库 API** - 提供 `db` 对象进行数据库操作
- **操作记录** - 记录所有数据库操作
- **错误处理** - 捕获和处理执行错误

#### DatabaseAPI 功能

```python
# 在脚本中使用 db API
db.get("key")                    # 获取数据
db.set("key", "value")           # 设置数据
db.list_keys("pattern*")         # 列出匹配的键
db.exists("key")                 # 检查键是否存在
db.delete("key")                 # 删除数据
db.copy("from", "to")            # 复制数据
```

### 4. Gen Port (`Gen/`)

生成器 Port，用于根据模板生成动态内容。

#### 主要组件

- **Parser** - 解析生成器语法
- **Generator** - 执行生成逻辑
- **GenFile** - 管理生成器文件
- **缓存系统** - 缓存解析结果以提高性能

#### 特性

- **语法解析** - 支持复杂的生成器语法
- **缓存机制** - 智能缓存解析结果
- **错误处理** - 详细的错误信息
- **性能优化** - 避免重复解析

### 5. Raw Port

简单的原始数据处理 Port，直接返回数据库中的原始内容。

## 分发逻辑

### 标准分发

```python
def dispatch(which):
    if which == "meta":
        return Meta
    elif which in ["raw"]:
        return Raw
    elif which in ["gen"]:
        return Gen
    return Text  # 默认使用 Text Port
```

### Meta 脚本分发

当访问带有后缀的路径时（如 `/source.script`），系统会：

1. 检查是否存在对应的脚本 entry
2. 如果存在，使用 Meta.accessScript 处理
3. 如果不存在，返回错误信息

## 请求处理流程

### 1. 请求接收

```python
# 服务器接收请求
pack = request2access(request)
```

### 2. 分发处理

```python
# 根据 MIME 类型分发
mime = first_avail(pack.mime, getmime(pack.entry), "text")
Dispatcher = Port.dispatch(mime)
```

### 3. 执行处理

```python
# 执行 Port 的 access 方法
output = Dispatcher.access(pack)
```

### 4. 返回结果

```python
# 返回处理结果
return output.value if output.skip else wrap(output)
```

## 扩展 Port

### 创建自定义 Port

```python
from protocol.types import FinalVis

class MyCustomPort:
    @staticmethod
    def access(pack) -> FinalVis:
        # 自定义处理逻辑
        result = "Custom processing result"
        return FinalVis.of("text", result)

# 注册到分发系统
def dispatch(which):
    if which == "custom":
        return MyCustomPort
    # ... 其他分发逻辑
```

### Port 接口规范

所有 Port 都应该实现以下接口：

```python
class Port:
    @staticmethod
    def access(pack) -> FinalVis:
        """
        处理请求的主要方法
        
        Args:
            pack: Access 对象，包含请求信息
            
        Returns:
            FinalVis: 处理结果
        """
        pass
```

## 错误处理

### 常见错误类型

1. **数据不存在** - 返回 "(empty)" 或错误信息
2. **脚本执行错误** - 返回详细的错误信息
3. **解析错误** - 返回语法错误信息
4. **权限错误** - 返回访问被拒绝信息

### 错误响应格式

```python
# 成功响应
FinalVis.of("text", "Success result")

# 错误响应
FinalVis.of("text", "Error: Detailed error message")
```

## 性能优化

### 1. 缓存机制

- **Gen Port** - 缓存解析结果
- **Meta Port** - 缓存脚本内容
- **Text Port** - 缓存数据转换结果

### 2. 懒加载

- 只在需要时加载和解析内容
- 避免不必要的数据库查询

### 3. 批量处理

- 支持批量数据操作
- 减少数据库访问次数

## 安全考虑

### 1. 脚本执行安全

- 限制可用的内置函数
- 提供安全的数据库 API
- 记录所有操作历史

### 2. 输入验证

- 验证输入数据格式
- 防止恶意输入
- 限制资源使用

### 3. 权限控制

- 区分不同类型的访问者
- 限制敏感操作
- 记录访问日志

## 调试和监控

### 1. 日志记录

```python
# 在 Port 中添加日志
import logging
logger = logging.getLogger(__name__)

def access(pack):
    logger.info(f"Processing request: {pack.entry}")
    # ... 处理逻辑
```

### 2. 性能监控

- 记录处理时间
- 监控资源使用
- 分析性能瓶颈

### 3. 错误追踪

- 详细的错误堆栈
- 错误发生上下文
- 自动错误报告

## 最佳实践

### 1. Port 设计

- 保持单一职责
- 提供清晰的接口
- 处理所有异常情况

### 2. 性能优化

- 使用缓存机制
- 避免重复计算
- 优化数据库查询

### 3. 安全实践

- 验证所有输入
- 限制脚本权限
- 记录敏感操作

### 4. 错误处理

- 提供有意义的错误信息
- 优雅地处理异常
- 记录错误详情