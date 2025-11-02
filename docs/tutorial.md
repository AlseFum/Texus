# 教程

本教程将引导您学习 Texus 的各项功能。

## 教程 1: 文本处理

### 创建和读取文本

```bash
# 创建文本文件
curl -X POST "http://localhost:7123/mynote?op=set&content=这是我的第一条笔记"

# 读取文本文件
curl http://localhost:7123/mynote

# 通过 API 获取（包含元数据）
curl http://localhost:7123/api/mynote
```

### 响应格式

**Web 访问** (`GET /mynote`):
```
这是我的第一条笔记
```

**API 访问** (`GET /api/mynote`):
```json
{
  "text": "这是我的第一条笔记",
  "lastSavedTime": "2024-01-01T12:00:00"
}
```

## 教程 2: 脚本执行

### 创建数据库操作脚本

创建文件 `demo.py`:

```python
# 设置数据
db.set("name", "Texus")
db.set("version", "1.0.0")

# 获取数据
name = db.get("name")
version = db.get("version")

# 输出结果
print(f"{name} version {version}")
print(f"所有键: {db.list_keys('*')}")
```

### 执行脚本

```bash
curl http://localhost:7123/demo.py
```

### 可用的数据库 API

- `db.get(key)` - 获取数据
- `db.set(key, value)` - 设置数据
- `db.delete(key)` - 删除数据
- `db.exists(key)` - 检查键是否存在
- `db.list_keys(pattern)` - 列出匹配的键
- `db.copy(from_key, to_key)` - 复制数据

## 教程 3: 内容生成器

### 创建生成器模板

创建文件 `story.gen`:

```
[故事开始]
[今天是一个|美好|糟糕|奇怪]的一天。
[我遇到了|朋友|敌人|陌生人]。
[我们一起|聊天|战斗|冒险]。
[故事结束]
```

### 生成内容

```bash
# 每次访问都会生成不同的随机组合
curl http://localhost:7123/story.gen
```

**可能的输出**:
```
故事开始
今天是一个美好的一天。
我遇到了朋友。
我们一起聊天。
故事结束
```

## 教程 4: Meta 脚本

### 数据转换示例

1. **创建源数据** `data.text`:
   ```
   Hello World
   ```

2. **创建转换脚本** `uppercase.meta`:
   ```python
   result = input_data.upper()
   print(result)
   ```

3. **执行转换**:
   ```bash
   curl http://localhost:7123/data.uppercase
   ```

**输出**: `HELLO WORLD`

### 数据统计示例

1. **源数据** `words.text`:
   ```
   apple banana apple orange
   ```

2. **统计脚本** `count.meta`:
   ```python
   words = input_data.split()
   word_count = {}
   for word in words:
       word_count[word] = word_count.get(word, 0) + 1
   
   for word, count in word_count.items():
       print(f"{word}: {count}")
   ```

3. **执行**:
   ```bash
   curl http://localhost:7123/words.count
   ```

## 教程 5: 定时任务

### 创建定时任务

创建文件 `mytimer.timer`:

```
script1.py
script2.py
# inline: db.set("last_run", "2024-01-01")
// This is a comment
```

### Timer 文件格式

- **脚本列表**: 每行一个脚本以`- `开头 entry 名称（如 `script.py`）
- **行内脚本** 每行一个脚本以`+ `开头 (如`print('nihao')`)
- **内联脚本**: 以 `#` 开头的单行 Python 代码
- **注释**: 以 `//` 开头的注释行

### 执行机制

- TimerManager 每秒扫描一次 TIMER 表
- 随机选择一个 `.timer` entry
- 从 entry 中随机选择一个脚本执行
- 记录执行统计信息

### 查看帮助

```bash
curl http://localhost:7123/help.timer
```

## 下一步

- 参考 [API 文档](api.md) 了解完整的 API 接口
- 查看 [贡献指南](../README.md#贡献指南) 了解如何参与开发

