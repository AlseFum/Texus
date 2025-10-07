# Gen - 文本生成器模块

基于 BNF 风格语法的随机文本生成器，支持嵌套和复杂的模板语法。

## 文件结构

```
Gen/
├── __init__.py      # 主入口，包含 Gen Port 类
├── generator.py     # Generator 类 - 生成器核心
├── parser.py        # Parser 类 - BNF 风格解析器
├── file.py          # GenFile 类 - 文件类型定义
└── README.md        # 本文件
```

## 工作流程

访问 `/xxx.gen` 时：

1. 从 **pub 表**读取 `xxx` 的文本内容和时间戳
2. 检查 **gen 表**缓存：
   - 比较时间戳和模板内容
   - 如果缓存有效，使用缓存的 Generator
   - 如果缓存失效或不存在，重新解析模板
3. 使用 **Parser** 解析模板生成 **Generator** 对象
4. 更新 **gen 表**缓存（保存 Generator 对象引用）
5. 调用 `generator.gen()` 生成随机文本
6. 返回生成的文本

### 特点

- ✅ **智能缓存**: 根据时间戳判断是否需要重新解析
- ✅ **高性能**: 相同模板只解析一次，后续访问使用缓存
- ✅ **自动更新**: pub 表内容更新时自动重新解析
- ✅ **内存高效**: Generator 对象保存在内存中，无需序列化

### 数据存储

- **pub 表**: 存储模板文本 + `lastSavedTime`（最后编辑时间）
- **gen 表**: 缓存解析结果
  - `template`: 模板文本
  - `sourceTimestamp`: pub 表的时间戳
  - `generator`: Generator 对象（Python 对象引用）
  - `parsedTime`: 解析时间

## 语法说明

### 基本语法

- `[a|b|c]` - **Roulette**：随机选择其中一个选项
- `{a|b|c}` - **Roulette**：随机选择其中一个选项（备用写法）
- 普通文本 - 直接输出
- `\[` `\]` `\{` `\}` `\|` `\\` - 转义特殊字符

### 示例

```
你好[世界|朋友|同志]
→ "你好世界" 或 "你好朋友" 或 "你好同志"

{早上|中午|晚上}好啊
→ "早上好啊" 或 "中午好啊" 或 "晚上好啊"

[很|非常|特别][开心|高兴|愉快]
→ "很开心" 或 "非常高兴" 等 9 种组合

今天天气[真|很|超级]{好|不错|棒}呢
→ 嵌套随机生成，支持复杂组合

我[喜欢|爱]\[编程\]
→ "我喜欢[编程]" 或 "我爱[编程]"（转义特殊字符）
```

## 核心类

### Generator

生成器核心类，支持两种生成模式：
- **PlainList**: 顺序拼接所有元素
- **Roulette**: 随机选择其中一个元素

### Parser

BNF 风格解析器，将文本模板解析为 Generator 对象树。

### Gen

Port 访问接口，提供：
- `access(pack)` - 主访问方法（唯一的方法）
  - 从 pub 表读取模板
  - 解析并生成随机文本
  - 返回结果

## 使用示例

### 1. 在 pub 表中保存模板

```python
from Database import pub_set
from datetime import datetime

pub_set("greeting", {
    "text": "你好[世界|朋友|同志]！今天[很|超级]开心见到你。",
    "lastSavedTime": datetime.now()
})
```

### 2. 访问 .gen 生成随机文本

```
GET /greeting.gen

可能的输出：
- "你好世界！今天很开心见到你。"
- "你好朋友！今天超级开心见到你。"
- "你好同志！今天很开心见到你。"
...（每次访问随机生成）
```

### 3. 直接使用 Parser 和 Generator

```python
from Port.Gen import Parser, Generator

# 使用解析器
parser = Parser("你好[世界|朋友]")
generator = parser.parse()
result = generator.gen()  # "你好世界" 或 "你好朋友"

# 直接使用 Generator
gen = Generator("Roulette", ["选项1", "选项2", "选项3"])
result = gen.gen()  # 随机返回一个选项
```

