from Common.base import FinalVis, entry
from Common import execute_script
from Database import Table
from .Text import Text

# 脚本模板
ENHANCED_SCRIPT_TEMPLATE = """# 输入数据
input_data = '''{input_data}'''

# 用户脚本
{metaHandler}
"""

# 调试信息模板
DEBUG_INFO_TEMPLATE = """Script executed successfully but produced no output.

Script content:
{metaHandler}

Available variables after execution:
- input_data: {input_data_repr}
- request: {request_repr}

Try adding a print statement to your script."""

TEXT_MANUAL = """Text Port - 文本处理端口

Text Port 用于处理文本数据的读取和写入操作。

主要功能：
- 读取文本内容：GET /path/to/file
- 写入文本内容：POST /path/to/file?op=set&content=文本内容
- API 访问：支持通过 API 获取结构化数据（包含时间戳等信息）

使用示例：
1. 读取文本：
   GET /myfile.text
   或
   GET /myfile

2. 写入文本：
   POST /myfile?op=set&content=Hello World

3. API 获取（返回 JSON）：
   GET /api/myfile
   返回：{"text": "...", "lastSavedTime": "..."}

支持的 MIME 类型：
- text: 默认文本类型
"""
PY_MANUAL = """Py Port (Exec) - 脚本执行端口

Py Port 用于执行 Python 脚本，专门用于操作数据库。

主要功能：
- 执行用户脚本：通过 query 参数或 entry 内容提供脚本
- 安全执行环境：限制可用函数，只能操作数据库
- 操作记录：记录所有数据库操作
- API 支持：支持 API 和 Web 两种访问方式

数据库 API (db)：
- db.get("key")           # 获取数据
- db.set("key", "value")   # 设置数据
- db.list_keys("pattern*") # 列出匹配的键
- db.exists("key")         # 检查键是否存在
- db.delete("key")         # 删除数据
- db.copy("from", "to")    # 复制数据

使用示例：
1. 通过 entry 执行脚本：
   创建 entry "myscript.py"，内容为：
   ```
   db.set("test", "value")
   print(db.get("test"))
   ```
   然后访问：GET /myscript.py

2. 通过 query 参数执行：
   GET /exec?script=print("Hello")

注意：
- 脚本只能操作数据库，不能执行危险操作
- 脚本输出通过 print() 函数返回
"""
GEN_MANUAL = """Gen Port - 生成器端口

Gen Port 用于根据模板生成随机内容。

主要功能：
- 模板解析：解析生成器语法
- 内容生成：根据模板生成随机文本
- 缓存机制：智能缓存解析结果，提高性能
- 错误处理：详细的错误信息

语法特性：
- 支持随机选择：使用 | 分隔选项
- 支持嵌套和递归
- 支持注释和变量

使用示例：
1. 创建生成器模板：
   创建 entry "mystory.gen"，内容为：
   ```
   [故事开始]
   [今天是一个|美好|糟糕]的一天
   [我遇到了|朋友|敌人]
   ```

2. 访问生成内容：
   GET /mystory.gen
   每次访问都会生成不同的随机组合

缓存机制：
- 自动缓存解析结果
- 当源文件更新时自动重新解析
- 提高重复生成性能
"""
META_MANUAL = """Meta Port - Meta 脚本端口

Meta Port 用于执行 Meta 脚本，实现数据转换和处理。

主要功能：
- 脚本执行：执行存储在数据库中的脚本
- 数据传递：将源数据作为 input_data 传递给脚本
- 安全执行：提供安全的脚本执行环境
- 结果提取：提取脚本的 print 输出

使用方式：
访问格式：/source.meta
- source: 源数据 entry 名称
- meta: Meta 脚本 entry 名称

执行流程：
1. 获取 source 的内容作为 input_data
2. 获取 meta 脚本内容
3. 执行脚本（input_data 作为变量传入）
4. 返回脚本的 print 输出

可用变量：
- input_data: 源数据内容（字符串）
- request: 完整的请求对象
- source: 源数据 entry 对象

使用示例：
1. 创建源数据 "data.text"：
   Hello World

2. 创建 Meta 脚本 "uppercase.meta"：
   ```
   result = input_data.upper()
   print(result)
   ```

3. 访问：GET /data.uppercase
   返回：HELLO WORLD

注意：
- 脚本必须使用 print() 输出结果
- input_data 包含源数据的文本内容
"""
TIMER_MANUAL = """Timer Port - 定时任务端口

Timer Port 用于管理和执行定时任务。

主要功能：
- 定时任务管理：管理 .timer 文件中的脚本列表
- 随机执行：TimerManager 每秒扫描并随机选择一个 timer 执行
- 脚本执行：执行 timer 中定义的脚本列表
- 统计记录：记录执行次数和最后触发时间

Timer 文件格式：
1. 脚本列表（每行一个脚本 entry 名称）
2. 内联脚本（以 # 开头）
3. 注释（以 // 开头）

示例 timer 文件内容：
```
myscript1.py
myscript2.py
# inline script: db.set("test", "value")
// This is a comment
```

执行机制：
- TimerManager 每秒扫描一次 TIMER 表
- 随机选择一个 .timer entry
- 从 entry 中随机选择一个脚本执行
- 记录执行统计信息

使用示例：
1. 创建 timer 文件 "mytimer.timer"：
   ```
   script1.py
   script2.py
   ```

2. TimerManager 会自动扫描并执行：
   - 每秒随机选择一个 timer
   - 随机执行其中的脚本

3. 查看执行统计：
   访问 TIMER 表获取执行次数等信息

注意事项：
- TimerManager 在服务启动时自动启动
- 所有 .timer entry 都会被扫描
- 脚本执行失败不影响其他 timer
"""
Manual={
    "text":TEXT_MANUAL,
    "py":PY_MANUAL,
    "gen":GEN_MANUAL,
    "meta":META_MANUAL,
    "timer":TIMER_MANUAL,
}
class Meta:
    @staticmethod
    def access(pack) -> FinalVis:
        """Meta Port 主访问方法"""
        return Meta.accessScript(pack)
    
    @staticmethod
    def accessScript(pack) -> FinalVis:
        if(getattr(pack, "suffix", None) in Manual):
            return FinalVis.of("raw", Manual[pack.suffix])
        
        main_table = Table.of("main")
        
        #abracadabra.xxx, xxx is the meta
        script_falsemeta = main_table.get(getattr(pack, "suffix", None))
        
        # 获取脚本内容
        metaHandler = ""
        if isinstance(script_falsemeta, entry):
            metaHandler = script_falsemeta.value.get("text", "")
        else:
            metaHandler = str(script_falsemeta or "")
        
        # 获取源数据（pack.entry就是源数据）
        source_data = main_table.get(pack.entry)
        input_data = ""
        if isinstance(source_data, entry):
            input_data = source_data.value.get("text", "")
        else:
            input_data = str(source_data or "")
        
        # 使用原始脚本内容，添加输入数据作为变量
        enhanced_script = ENHANCED_SCRIPT_TEMPLATE.format(
            input_data=input_data,
            metaHandler=metaHandler
        )
        
        # 使用 Common.execute_script 执行脚本
        # 添加额外的全局变量：request 和 source
        extra_globals = {
            'request': pack,
            'source': source_data,
        }
        
        success, output, operations = execute_script(enhanced_script, extra_globals)
        
        if success:
            # 只提取print输出的结果
            if output:
                return FinalVis.of("text", payload={"text": output})
            else:
                # 显示更详细的执行信息
                input_data_repr = repr(input_data[:100] + '...' if len(input_data) > 100 else input_data)
                debug_info = DEBUG_INFO_TEMPLATE.format(
                    metaHandler=metaHandler,
                    input_data_repr=input_data_repr,
                    request_repr=repr(pack)
                )
                return FinalVis.of("text", payload={"text": debug_info})
        else:
            error_msg = f"Script execution error: {output}"
            return FinalVis.of("text", payload={"text": error_msg})

# 插件注册函数
def registry():
    return {
        "mime": "meta",
        "port": Meta
    }