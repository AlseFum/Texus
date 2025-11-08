# Database 模块

Database 模块提供了轻量级的键值存储系统，支持多表管理、自动备份和恢复功能。

## 文件结构

```
Database/
├── __init__.py      # 主入口文件，提供便捷的API接口
├── table.py         # Table 类定义，核心存储实现
├── backup.py        # 备份系统实现
├── test_cases.py    # 测试用例和数据
└── .backup/         # 备份文件存储目录
```

## 核心组件

### 1. Table 类 (`table.py`)

Table 是核心的存储单元，提供键值对存储功能。

#### 主要方法：

- `Table.of(name)` - 获取或创建指定名称的表
- `get(key, otherwise=None)` - 获取值
- `set(key, value)` - 设置值
- `sync()` - 标记表需要备份
- `is_sync_required()` - 检查是否需要备份
- `mark_synced()` - 标记已备份完成

#### 使用示例：

```python
from Database import Table

# 创建或获取表
table = Table.of("MY_TABLE")

# 存储数据
table.set("key1", "value1")
table.set("key2", {"data": "complex"})

# 读取数据
value = table.get("key1")
value = table["key2"]  # 支持字典式访问
```

### 2. 直接使用 Table (`__init__.py`)

所有数据存储直接通过 Table.of() 访问，无需额外封装：

```python
from Database import Table

# 主表 - 存储所有 entry
main_table = Table.of("main")

# 存储数据
main_table.set("my_data", "some value")

# 读取数据
data = main_table.get("my_data")

# 私有数据表
hid_table = Table.of("HID")
hid_table.set("secret", "private value")
secret = hid_table.get("secret")
```

#### MIME 类型管理

```python
from Database import getmime

# MIME 类型直接从 entry 对象读取
mime_type = getmime("myfile")  # 从主表查询 entry 的 mime 属性
```

### 3. 备份系统 (`backup.py`)

自动备份系统支持定期备份和手动备份。

#### 初始化备份系统

```python
from Database import init_backup_system

# 初始化备份系统
backup_manager = init_backup_system(
    backup_dir=".backup",      # 备份目录
    max_backups=10,            # 最大备份数量
    backup_interval=600,       # 备份间隔（秒）
    format="json"              # 备份格式: "json", "toml" 或 "line"
)

# 使用 line 格式
backup_manager = init_backup_system(format="line")

# 使用 JSON 格式（默认）
backup_manager = init_backup_system(format="json")
```

#### 手动备份

```python
from Database import create_manual_backup

# 创建手动备份
backup_info = create_manual_backup()
```

#### 停止备份系统

```python
from Database import stop_backup_system

# 停止备份系统
stop_backup_system()
```

## 数据模型

### Entry 对象

Database 使用 `entry` 对象来存储结构化数据：

```python
from Common.base import entry
from Database import Table
from datetime import datetime

# 获取主表
main_table = Table.of("main")

# 创建 entry 对象
my_entry = entry(
    mime="text",
    value={
        "text": "Hello World",
        "lastSavedTime": datetime.now()
    }
)

# 存储 entry
main_table.set("my_entry", my_entry)

# 读取 entry
retrieved_entry = main_table.get("my_entry")
print(retrieved_entry.value["text"])  # "Hello World"
```

#### Entry 序列化方法

`entry` 类提供了多种序列化方法：

```python
from Common.base import entry

my_entry = entry(
    mime="text",
    value={"text": "Hello", "count": 42}
)

# 转换为字典（用于 JSON/TOML 备份）
entry_dict = my_entry.to_dict()

# 从字典恢复
restored = entry.from_dict(entry_dict)

# 转换为单行文本（用于 line 格式备份）
line = my_entry.to_line()
# 输出: '{"text":"Hello","count":42}'

# 从单行文本恢复 value
value = entry.from_line(line)

# 转换为可渲染对象（用于视图层）
renderee = my_entry.to_renderee()
```

## 内置表

系统使用以下表：

- **main** - 主表，存储所有 entry（路径→entry 映射）
- **HID** - 私有数据存储
- **GEN** - Gen Port 的缓存表（ShadowTable）
- **TIMER** - Timer Port 的统计表（ShadowTable）

## 备份格式

备份系统支持多种格式：

- **JSON** - 人类可读的 JSON 格式，结构简洁
- **TOML** - 更紧凑的 TOML 格式
- **line** - 文本行格式，易于查看和比对，以 `.txt` 扩展名保存

### JSON 格式示例

简洁的 JSON 格式，直接存储表数据，无多余元数据：

```json
{
  "main": {
    "document.md": {
      "mime": "text",
      "value": {
        "text": "# My Document\n\nContent...",
        "lastSavedTime": "2025-11-08T18:26:14.524079"
      },
      "lastModifiedTime": "2025-11-08T18:26:14.524079"
    }
  },
  "timers": {
    "timer1": {
      "mime": "timer",
      "value": {
        "interval": 3600,
        "active": true
      }
    }
  }
}
```

### Line 格式示例

文本行格式，每个表独立显示，易于阅读和版本控制：

```
Table main 20251108182614:
- 20251108182614 text document.md {"text":"# My Document\n\nContent...","lastSavedTime":"2025-11-08T18:26:14.524079"}
- 20251108182650 text readme {"text":"README content...","lastSavedTime":"2025-11-08T18:26:50.123456"}

Table timers 20251108182614:
- 20251108182614 timer timer1 {"interval":3600,"active":true}
- 20251108182700 timer timer2 {"interval":7200,"active":false}

```

格式说明：
- `Table tablename timestamp:` - 表头，包含表名和时间戳
- `- timestamp mime keyname valueline` - 数据行，包含记录时间戳、MIME类型、键名和JSON格式的value
- 表与表之间用空行分隔

## 使用场景

### 1. 简单键值存储

```python
from Database import Table

# 获取主表
main_table = Table.of("main")

# 存储用户配置
main_table.set("user_config", {
    "theme": "dark",
    "language": "zh-CN"
})

# 读取配置
config = main_table.get("user_config")
```

### 2. 文件内容管理

```python
from Database import Table
from Common.base import entry
from datetime import datetime

# 获取主表
main_table = Table.of("main")

# 存储文件内容
file_content = entry(
    mime="text",
    value={
        "text": "# My Document\n\nThis is content...",
        "lastSavedTime": datetime.now()
    }
)
main_table.set("document.md", file_content)

# 读取文件内容
doc = main_table.get("document.md")
print(doc.value["text"])
```

### 3. 脚本存储

```python
from Database import Table

# 获取主表
main_table = Table.of("main")

# 存储 Python 脚本
script_content = """
print("Hello from script!")
return "Script executed"
"""
main_table.set("my_script", script_content)

# 读取脚本
script = main_table.get("my_script")
```

## 性能特性

- **内存存储** - 所有数据存储在内存中，访问速度快
- **自动备份** - 支持定期自动备份，防止数据丢失
- **增量同步** - 只备份有变化的表，提高效率
- **多表隔离** - 不同表之间数据完全隔离
- **多格式支持** - 支持 JSON、TOML 和 line 三种备份格式
- **简洁存储** - JSON/TOML 格式无多余元数据，文件更小
- **易于比对** - line 格式便于 Git 版本控制和差异对比

## 注意事项

1. **数据持久性** - 数据存储在内存中，重启后会丢失，需要依赖备份系统
2. **备份频率** - 建议根据数据重要性设置合适的备份间隔
3. **内存使用** - 大量数据会占用较多内存，注意监控
4. **并发安全** - 当前实现不是线程安全的，多线程环境需要额外考虑
5. **备份格式选择**：
   - **JSON** - 适合通用场景，结构化好，易于解析
   - **line** - 适合版本控制，易于查看差异，便于手动编辑
   - **TOML** - 适合配置文件风格的存储

## 备份格式对比

| 特性 | JSON | TOML | line |
|------|------|------|------|
| 文件扩展名 | `.json` | `.toml` | `.txt` |
| 人类可读性 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 机器解析 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 版本控制友好 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 文件大小 | 中等 | 小 | 中等 |
| 差异对比 | 一般 | 一般 | 优秀 |
| 手动编辑 | 一般 | 一般 | 容易 |
| 时间戳记录 | 有 | 有 | 每行独立 |

### 使用建议

**选择 JSON 格式**：
- 通用场景，最广泛支持
- 需要其他工具解析备份数据
- 兼容性要求高

**选择 line 格式**：
- 使用 Git 进行版本控制
- 需要频繁查看数据变化
- 希望手动编辑备份文件
- 需要独立的时间戳记录

**选择 TOML 格式**：
- 偏好配置文件风格
- 需要更紧凑的文件大小

## 扩展

可以通过继承 `Table` 类来扩展功能：

```python
from Database import Table

class MyCustomTable(Table):
    def __init__(self, name):
        super().__init__(name)
        # 添加自定义功能
    
    def custom_method(self):
        # 自定义方法
        pass
```

### 自定义 entry 子类

可以继承 `entry` 类并覆写序列化方法：

```python
from Common.base import entry

class TimerEntry(entry, mime="timer"):
    """Timer 专用的 entry 类"""
    
    def to_line(self) -> str:
        """自定义单行序列化格式"""
        # 自定义逻辑
        return super().to_line()
    
    @classmethod
    def from_line(cls, line: str):
        """自定义反序列化逻辑"""
        # 自定义逻辑
        return super().from_line(line)
```
