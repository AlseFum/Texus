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
    format="json"              # 备份格式
)
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

## 内置表

系统使用以下表：

- **main** - 主表，存储所有 entry（路径→entry 映射）
- **HID** - 私有数据存储
- **GEN** - Gen Port 的缓存表（ShadowTable）
- **TIMER** - Timer Port 的统计表（ShadowTable）

## 备份格式

备份系统支持多种格式：

- **JSON** - 人类可读的 JSON 格式
- **TOML** - 更紧凑的 TOML 格式

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

## 注意事项

1. **数据持久性** - 数据存储在内存中，重启后会丢失，需要依赖备份系统
2. **备份频率** - 建议根据数据重要性设置合适的备份间隔
3. **内存使用** - 大量数据会占用较多内存，注意监控
4. **并发安全** - 当前实现不是线程安全的，多线程环境需要额外考虑

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
