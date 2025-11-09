from Database import Table
from Common.base import FinalVis, entry
from Common.util import first_valid
from datetime import datetime
import threading
import time
import random

class TimerEntry(entry, mime="timer"):
    """Timer 专用的 entry 类型，存储脚本列表、内联脚本和注释"""
    
    def __init__(self, scripts=None, inline_scripts=None, comments=None, count=None, items=None, lastModifiedTime=None, text=None):
        if text is not None:
            # 从纯文本解析所有数据
            parsed = TimerEntry._parse_scripts_from_text(text)
            items = parsed.get("items", [])
            count = parsed.get("count", None)
        else:
            # 如果提供了 scripts、inline_scripts、comments，转换为 items 格式
            if items is None:
                items = []
                if comments:
                    for comment in comments:
                        items.append({"type": "comment", "content": comment})
                if scripts:
                    for script in scripts:
                        items.append({"type": "script", "content": script})
                if inline_scripts:
                    for inline_script in inline_scripts:
                        items.append({"type": "inline_script", "content": inline_script})
        
        items = items or []
        
        self._items = items  # 保持原始顺序的项列表，每个项包含 type 和 content
        self._count = count
        self.lastModifiedTime = lastModifiedTime or datetime.now()
        super().__init__(mime="timer", value=None)
    
    @staticmethod
    def _parse_scripts_from_text(text: str) -> dict:
        """从纯文本解析 timer 数据，保持原始位置顺序
        
        支持的格式：
        count = number
        
        #comments
        
        #comments
        
        - scripts 1
        
        - scripts2
        
        - scripts3
        
        + inlinescripts1
        
        + inlinescripts2
        """
        if not text or not isinstance(text, str):
            return {"items": [], "count": None}
        
        items = []
        count = None
        
        for line in text.split('\n'):
            original_line = line
            line = line.strip()
            
            # 空行保留
            if not line:
                items.append({"type": "blank", "content": ""})
                continue
            
            # 解析 count = number
            if line.startswith('count = '):
                try:
                    count = int(line.replace('count = ', '').strip())
                    items.append({"type": "count", "content": count})
                except:
                    pass
                continue
            
            # 解析注释
            if line.startswith('#'):
                comment = line[1:].strip()  # 去掉 # 符号
                items.append({"type": "comment", "content": comment})
                continue
            
            # 解析脚本路径 (- 开头)
            if line.startswith('- '):
                script = line[2:].strip()  # 去掉 - 符号
                if script:
                    items.append({"type": "script", "content": script})
                continue
            
            # 解析内联脚本 (+ 开头)
            if line.startswith('+ '):
                inline_script = line[2:].strip()  # 去掉 + 符号
                if inline_script:
                    items.append({"type": "inline_script", "content": inline_script})
                continue
        
        return {
            "items": items,
            "count": count
        }
    
    @property
    def value(self):
        """覆写 value getter，返回 Timer 的数据结构"""
        return {
            "scripts": self.scripts,
            "inline_scripts": self.inline_scripts,
            "comments": self.comments,
            "count": self._count,
            "items": self._items,
            "text": self.to_text(),
            "lastModifiedTime": self.lastModifiedTime
        }
    
    @value.setter
    def value(self, val):
        """设置 value"""
        if val and isinstance(val, dict):
            if "items" in val:
                self._items = val.get("items", [])
            else:
                # 如果没有 items，从 scripts、inline_scripts、comments 重建
                items = []
                if val.get("comments"):
                    for comment in val.get("comments", []):
                        items.append({"type": "comment", "content": comment})
                if val.get("scripts"):
                    for script in val.get("scripts", []):
                        items.append({"type": "script", "content": script})
                if val.get("inline_scripts"):
                    for inline_script in val.get("inline_scripts", []):
                        items.append({"type": "inline_script", "content": inline_script})
                self._items = items
            self._count = val.get("count", None)
            if "lastModifiedTime" in val:
                self.lastModifiedTime = val["lastModifiedTime"]
        elif val and isinstance(val, str):
            # 如果是字符串，尝试解析
            parsed = TimerEntry._parse_scripts_from_text(val)
            self._items = parsed.get("items", [])
            self._count = parsed.get("count", None)
            self.lastModifiedTime = datetime.now()
    
    @property
    def scripts(self):
        """获取脚本列表（脚本路径）"""
        return [item["content"] for item in self._items if item.get("type") == "script"]
    
    @scripts.setter
    def scripts(self, scripts_list):
        """设置脚本列表（会替换所有脚本项）"""
        # 移除所有现有的脚本项
        self._items = [item for item in self._items if item.get("type") != "script"]
        # 添加新的脚本项（在最后）
        for script in (scripts_list or []):
            self._items.append({"type": "script", "content": script})
        self.lastModifiedTime = datetime.now()
    
    @property
    def inline_scripts(self):
        """获取内联脚本列表"""
        return [item["content"] for item in self._items if item.get("type") == "inline_script"]
    
    @inline_scripts.setter
    def inline_scripts(self, inline_scripts_list):
        """设置内联脚本列表（会替换所有内联脚本项）"""
        # 移除所有现有的内联脚本项
        self._items = [item for item in self._items if item.get("type") != "inline_script"]
        # 添加新的内联脚本项（在最后）
        for inline_script in (inline_scripts_list or []):
            self._items.append({"type": "inline_script", "content": inline_script})
        self.lastModifiedTime = datetime.now()
    
    @property
    def comments(self):
        """获取注释列表"""
        return [item["content"] for item in self._items if item.get("type") == "comment"]
    
    @comments.setter
    def comments(self, comments_list):
        """设置注释列表（会替换所有注释项）"""
        # 移除所有现有的注释项
        self._items = [item for item in self._items if item.get("type") != "comment"]
        # 添加新的注释项（在最后）
        for comment in (comments_list or []):
            self._items.append({"type": "comment", "content": comment})
        self.lastModifiedTime = datetime.now()
    
    @property
    def count(self):
        """获取执行次数"""
        return self._count
    
    @count.setter
    def count(self, count_value):
        """设置执行次数"""
        self._count = count_value
        # 更新或添加 count 项
        count_items = [item for item in self._items if item.get("type") == "count"]
        if count_items:
            count_items[0]["content"] = count_value
        else:
            # 如果没有 count 项，添加到开头
            self._items.insert(0, {"type": "count", "content": count_value})
        self.lastModifiedTime = datetime.now()
    
    def to_text(self) -> str:
        """将 timer 数据转换为纯文本格式，保持原始位置顺序
        
        格式：
        count = number
        
        #comments
        
        #comments
        
        - scripts 1
        
        - scripts2
        
        - scripts3
        
        + inlinescripts1
        
        + inlinescripts2
        """
        lines = []
        
        # 按照 items 的顺序输出，保持原始位置
        for item in self._items:
            item_type = item.get("type")
            content = item.get("content")
            
            if item_type == "blank":
                lines.append("")
            elif item_type == "count":
                lines.append(f"count = {content}")
            elif item_type == "comment":
                lines.append(f"#{content}")
            elif item_type == "script":
                lines.append(f"- {content}")
            elif item_type == "inline_script":
                lines.append(f"+ {content}")
        
        return '\n'.join(lines).strip()

class TimerManager:
    """定时任务管理器，负责管理所有定时任务的调度和执行"""
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
        self._state_lock = threading.Lock()
    
    def start(self):
        """启动定时任务调度器"""
        with self._state_lock:
            if self.running:
                return
            
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
    
    def stop(self):
        """停止定时任务调度器"""
        with self._state_lock:
            self.running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _scheduler_loop(self):
        """调度器主循环 - 每秒执行一次"""
        while True:
            with self._state_lock:
                if not self.running:
                    break
                should_run = self.running
            
            if not should_run:
                break
            
            self._scan_and_execute()
            time.sleep(1)  # 每秒扫描一次
    
    def _scan_and_execute(self):
        """扫描TIMER表并随机选择一个条目执行"""
        # 从TIMER表获取所有条目
        # Timer.update 会确保所有 timer entry 都在 TIMER 表中有记录
        timer_table = Table.of("TIMER")
        main_table = Table.of("main")
        
        # 获取所有.timer entry的名称（从TIMER表）
        timer_entries = []
        for entry_name, entry_data in timer_table.inner.items():
            # 跳过非entry文件的数据
            if entry_name.startswith('_'):
                continue
            
            # 检查是否是.timer entry（通过主表中的mime类型判断）
            data = main_table.get(entry_name)
            if data and isinstance(data, entry) and data.mime == "timer":
                timer_entries.append(entry_name)
        
        # 测试功能：每秒打印扫描到的可用的Timer，使用vmAPI打印到TimerHistory.text
        from Database import vmAPI
        db_api = vmAPI()
        
        # # 生成扫描结果文本
        # scan_result = ""
        # scan_result += f"可用Timer数量: {len(timer_entries)}\n"
        # if (len(timer_entries) > 0):
        #     for entry_name in timer_entries:
        #         scan_result += f"  - {entry_name}\n"
        
        # 使用vmAPI保存到TimerHistory.text
        # try:
        #     # 读取现有内容
        #     history_entry = db_api.get("TimerHistory.text")
        #     existing_content = ""
        #     if history_entry and isinstance(history_entry.value, dict):
        #         existing_content = history_entry.value.get("text", "")
            
        #     # 追加新的扫描结果
        #     new_content = existing_content + "\n" + scan_result if existing_content else scan_result
        #     db_api.set("timerhistory", new_content, mime="text")
            
        #     print(scan_result.strip())
        # except Exception as e:
        #     print(f"保存Timer扫描结果失败: {e}")
        
        # 如果没有可用的 timer entry，直接返回
        if not timer_entries:
            return
        
        # 随机选择一个.timer entry执行
        selected_entry = random.choice(timer_entries)
        self._execute_timer_entry(selected_entry)
    
    def _execute_timer_entry(self, entry_name):
        """执行单个.timer entry"""
        # 从主表获取.timer entry的内容
        main_table = Table.of("main")
        timer_data = main_table.get(entry_name)
        
        if timer_data is None:
            return
        
        # 获取脚本列表和内联脚本列表
        scripts = []
        inline_scripts = []
        
        if isinstance(timer_data, TimerEntry):
            scripts = timer_data.scripts
            inline_scripts = timer_data.inline_scripts
        elif isinstance(timer_data, entry):
            scripts = timer_data.value.get("scripts", [])
            inline_scripts = timer_data.value.get("inline_scripts", [])
        
        # 如果没有任何脚本，直接返回
        if not scripts and not inline_scripts:
            return
        
        # 执行每个脚本路径
        for script_path in scripts:
            self._execute_script(script_path)
        
        # 执行每个内联脚本
        for inline_script in inline_scripts:
            self._execute_inline_script(inline_script, entry_name)
        
        # 更新TIMER表中的触发次数
        timer_table = Table.of("TIMER")
        timer_record = timer_table.get(entry_name)
        if timer_record is None:
            timer_record = {"count": 0, "last_triggered": None}
        
        if isinstance(timer_record, dict):
            timer_record["count"] = timer_record.get("count", 0) + 1
            timer_record["last_triggered"] = datetime.now().isoformat()
            timer_table.set(entry_name, timer_record)
    
    def _execute_script(self, script_path):
        """执行单个脚本路径"""
        from Common import execute_script
        
        # 获取脚本内容
        main_table = Table.of("main")
        script_data = main_table.get(script_path)
        if script_data is None:
            print(f"警告: 脚本 {script_path} 不存在")
            return
        
        # 提取脚本内容
        script_content = ""
        if isinstance(script_data, entry):
            script_content = script_data.value.get("text", "")
        else:
            script_content = str(script_data or "")
        
        if not script_content.strip():
            return
        
        # 执行脚本
        success, output, operations = execute_script(script_content)
        
        if not success:
            print(f"脚本 {script_path} 执行失败: {output}")
        elif output:
            print(f"脚本 {script_path} 输出:\n{output}")
    
    def _execute_inline_script(self, script_content, entry_name):
        """执行内联脚本"""
        from Common import execute_script
        
        if not script_content or not script_content.strip():
            return
        
        # 直接执行内联脚本内容
        success, output, operations = execute_script(script_content)
        
        if not success:
            print(f"内联脚本 (from {entry_name}) 执行失败: {output}")
        elif output:
            print(f"内联脚本 (from {entry_name}) 输出:\n{output}")

# 模块级单例实例
timer_manager = TimerManager()


from Common.base import FinalVis
from .Text import Text, ShadowPort

class Timer(ShadowPort):
    """定时任务 Port - 用于访问和管理.timer文件
    
    Timer 继承自 Text，覆写了 get_data 方法以支持 TimerEntry
    使用PUB表存储.timer entry内容
    使用TIMER表记录执行统计信息
    """
    @staticmethod
    def access(pack) -> FinalVis:
        """访问 .timer 时在页面顶部弹出提示（通知栏），说明 + / - 的用法"""
        op = first_valid(getattr(pack, "query", {}).get("op", None), "get")
        if op == "set":
            # 复用 Text 的保存逻辑（会触发 ShadowPort.update，从而更新 TIMER 表）
            return Text.set(pack)
        
        # API 下保持与 Text 一致，返回结构化数据
        is_api = getattr(pack, "by", "") == "api"
        if is_api:
            return Text.getByApi(pack)
        
        # Web 渲染：注入通知栏，提示 + / - 用法
        text_file = Text.get_data(getattr(pack, "entry", "") or getattr(pack, "path", ""))
        text_content = text_file.value.get("text", "")
        
        help_msg = (
            "Timer 用法提示：\\n"
            "- 以 `- <脚本路径>` 添加脚本（每行一个）\\n"
            "- 以 `+ <内联脚本>` 添加即时执行的脚本\\n"
            "- 以 `# 注释` 添加说明\\n"
            "- 可选 `count = <数字>` 指定次数\\n"
            "示例：\\n"
            "count = 5\\n"
            "# 下面是脚本路径\\n"
            "- script1.py\\n"
            "- script2.py\\n"
            "# 下面是内联脚本\\n"
            "+ db.set(\\\"key\\\", \\\"value\\\")"
        )
        
        return FinalVis.of(
            "text",
            payload={
                "text": text_content,
                "infoMessage": help_msg,
                "infoType": "info",
                "infoDismissible": True,
                "infoDuration": 0
            }
        )
    
    @staticmethod
    def get_data(entry_key) -> TimerEntry:
        """从数据库获取.timer文件数据，返回TimerEntry对象
        每次获取时会与主表中的内容时间戳对比，如果不同则重新生成并保存
        """
        main_table = Table.of("main")
        pub_data = main_table.get(entry_key)
        if pub_data is None:
            return TimerEntry(scripts=[], lastModifiedTime=None)
        
        # 获取源数据的时间戳和文本内容
        source_timestamp = None
        source_text = None
        
        if isinstance(pub_data, entry):
            source_timestamp = pub_data.lastModifiedTime
            # 提取文本内容
            if isinstance(pub_data.value, str):
                source_text = pub_data.value
            elif isinstance(pub_data.value, dict):
                source_text = pub_data.value.get("text", "")
        elif isinstance(pub_data, str):
            source_timestamp = datetime.now()
            source_text = pub_data
        else:
            source_timestamp = datetime.now()
            source_text = str(pub_data)
        
        # 如果是 TimerEntry，需要对比时间戳
        if isinstance(pub_data, TimerEntry):
            # 对比时间戳，如果相同则直接返回
            if pub_data.lastModifiedTime == source_timestamp:
                return pub_data
            # 时间戳不同，需要重新生成
        
        # 从源文本解析生成 TimerEntry
        timer_entry = TimerEntry(text=source_text or "", lastModifiedTime=source_timestamp)
        
        # 保存到主表
        main_table.set(entry_key, timer_entry)
        
        return timer_entry
    
    @staticmethod
    def update(pack):
        """当 text 内容变动时更新 timer 的 table"""
        entry_key = pack.entry if hasattr(pack, 'entry') else None
        if not entry_key:
            return
        # 从 text 表中读取最新的文本内容
        from .Text import Text
        text_data = Text.get_data(entry_key)
        text_content = text_data.value.get("text", "")
        text_timestamp = text_data.value.get("lastSavedTime")
        
        # 检查主表中的数据
        main_table = Table.of("main")
        data = main_table.get(entry_key)
        
        # 判断是否是 timer entry
        is_timer = data and getattr(pack, "suffix", None) == "timer"
        # 如果已经是 timer entry，更新它
        if is_timer:
            # 从文本内容创建 TimerEntry
            timer_entry = TimerEntry(text=text_content, lastModifiedTime=text_timestamp)
            
            # 更新主表中的 timer entry
            main_table.set(entry_key, timer_entry)
            
            # 确保 TIMER 表中有记录，如果不存在则创建，如果存在则更新
            timer_table = Table.of("TIMER")
            timer_record = timer_table.get(entry_key)
            if timer_record is None:
                # 如果 TIMER 表中没有记录，创建一个新的
                timer_record = {"count": 0, "last_triggered": None}
            elif not isinstance(timer_record, dict):
                timer_record = {"count": 0, "last_triggered": None}
            
            # 更新时间戳信息（保留 count 和 last_triggered）
            timer_record["last_updated"] = datetime.now().isoformat() if text_timestamp else None
            timer_table.set(entry_key, timer_record)

# 注册到 ShadowPort
ShadowPort.set(Timer)

# 插件注册函数
def registry():
    return {
        "mime": "timer",
        "port": Timer
    }