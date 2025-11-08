"""
数据库备份管理器
- 每10分钟自动备份
- 保留10个备份文件
- 启动时加载最新备份
- 支持 JSON 和 TOML 格式
"""

import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 导入 entry 类型用于序列化检查
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Common.base import entry

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


class CustomJSONEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，处理特殊对象"""
    
    def default(self, obj):
        # 处理 TimerEntry 对象，转换为文本格式
        if isinstance(obj, entry):
            if hasattr(obj, 'mime') and obj.mime == "timer":
                try:
                    from Port.Timer import TimerEntry
                    text_content = ""
                    saved_time = datetime.now()
                    
                    if isinstance(obj, TimerEntry):
                        # 使用 to_text() 转换为文本格式
                        text_content = obj.to_text() if hasattr(obj, 'to_text') else ""
                        saved_time = obj.lastModifiedTime if hasattr(obj, 'lastModifiedTime') else datetime.now()
                    else:
                        # 如果不是 TimerEntry，尝试从 value property 获取文本
                        try:
                            val = obj.value
                            if isinstance(val, dict):
                                text_content = val.get("text", "")
                                saved_time = val.get("lastSavedTime", datetime.now())
                            elif isinstance(val, str):
                                text_content = val
                        except:
                            pass
                        if not text_content:
                            text_content = ""
                            saved_time = obj.lastModifiedTime if hasattr(obj, 'lastModifiedTime') else datetime.now()
                    
                    # 创建文本格式的 entry
                    text_entry = entry(
                        mime="text",
                        value={
                            "text": text_content,
                            "lastSavedTime": saved_time
                        }
                    )
                    result = text_entry.to_dict()
                    result["__type__"] = "entry"
                    # 标记原始 mime 为 timer，用于恢复时识别
                    result["_original_mime"] = "timer"
                    return result
                except (ImportError, AttributeError) as e:
                    print(f"Warning: 无法序列化 TimerEntry: {e}")
                    # 如果无法导入或没有 to_text 方法，回退到普通序列化
                    pass
            
            # 普通 entry 对象的处理
            result = obj.to_dict()
            result["__type__"] = "entry"
            return result
        
        # 处理 datetime 对象
        if isinstance(obj, datetime):
            return {
                "__type__": "datetime",
                "value": obj.isoformat()
            }
        
        # 其他对象使用默认处理
        return super().default(obj)


def serialize_value(value):
    """递归序列化值，将 entry 对象转换为字典"""
    if isinstance(value, entry):
        # 检查是否是 TimerEntry（mime == "timer"），如果是则转换为文本格式
        if hasattr(value, 'mime') and value.mime == "timer":
            # 尝试导入 TimerEntry 并进行转换
            try:
                from Port.Timer import TimerEntry
                # 无论是 TimerEntry 还是普通 entry，只要 mime="timer"，都尝试转换
                text_content = ""
                saved_time = datetime.now()
                
                # 检查是否是 TimerEntry 实例
                if isinstance(value, TimerEntry):
                    # 使用 to_text() 转换为文本格式
                    text_content = value.to_text() if hasattr(value, 'to_text') else ""
                    saved_time = value.lastModifiedTime if hasattr(value, 'lastModifiedTime') else datetime.now()
                else:
                    # 如果不是 TimerEntry，尝试从 value property 获取文本（不是 _value）
                    try:
                        # 使用 value property 而不是 _value
                        val = value.value
                        if isinstance(val, dict):
                            text_content = val.get("text", "")
                            saved_time = val.get("lastSavedTime", datetime.now())
                        elif isinstance(val, str):
                            text_content = val
                    except:
                        pass
                    
                    # 如果 value 中没有 text，尝试从 Text 表中获取（因为 Timer 是 ShadowPort）
                    if not text_content:
                        try:
                            # 尝试导入 Text 来获取实际存储的文本内容
                            # 注意：这里需要知道 entry_key，但在序列化时可能没有
                            # 所以这个逻辑需要在备份流程中处理
                            pass
                        except:
                            pass
                    
                    # 如果还是没有内容，至少保存格式
                    if not text_content:
                        text_content = ""
                        saved_time = value.lastModifiedTime if hasattr(value, 'lastModifiedTime') else datetime.now()
                
                # 创建文本格式的 entry
                text_entry = entry(
                    mime="text",
                    value={
                        "text": text_content,
                        "lastSavedTime": saved_time
                    }
                )
                result = text_entry.to_dict()
                result["__type__"] = "entry"
                # 标记原始 mime 为 timer，用于恢复时识别
                result["_original_mime"] = "timer"
                return result
            except (ImportError, AttributeError) as e:
                print(f"Warning: 无法序列化 TimerEntry: {e}")
                # 如果无法导入或没有 to_text 方法，回退到普通序列化
                pass
        
        # 普通 entry 对象的序列化
        # 使用 entry 的 to_dict 方法，并添加类型标记
        result = value.to_dict()
        result["__type__"] = "entry"  # 添加类型标记便于反序列化
        return result
    elif isinstance(value, datetime):
        return {
            "__type__": "datetime",
            "value": value.isoformat()
        }
    elif isinstance(value, dict):
        # 使用 list() 创建副本，避免在迭代时字典大小变化的问题
        return {k: serialize_value(v) for k, v in list(value.items())}
    elif isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    else:
        return value


def deserialize_value(value):
    """递归反序列化值，将字典转换回 entry 对象"""
    if isinstance(value, dict):
        # 检查类型标记
        if value.get("__type__") == "entry":
            try:
                # 检查是否是 timer entry（通过 _original_mime 标记）
                if value.get("_original_mime") == "timer":
                    # 尝试导入 TimerEntry
                    try:
                        from Port.Timer import TimerEntry
                        # 从文本内容恢复 TimerEntry
                        entry_data = {k: v for k, v in value.items() if k not in ["__type__", "_original_mime"]}
                        restored_entry = entry.from_dict(entry_data)
                        # 如果恢复的 entry 是 text 类型，且有 text 内容，转换为 TimerEntry
                        if hasattr(restored_entry, 'value') and isinstance(restored_entry.value, dict):
                            text_content = restored_entry.value.get("text", "")
                            saved_time = restored_entry.value.get("lastSavedTime")
                            if text_content:
                                # 使用 text 内容创建 TimerEntry
                                return TimerEntry(text=text_content, lastModifiedTime=saved_time)
                    except (ImportError, AttributeError) as e:
                        print(f"Warning: 无法恢复 TimerEntry: {e}")
                        # 回退到普通 entry
                
                # 移除类型标记后转换为 entry 对象
                entry_data = {k: v for k, v in value.items() if k not in ["__type__", "_original_mime"]}
                return entry.from_dict(entry_data)
            except Exception as e:
                print(f"Warning: Failed to deserialize entry object: {e}")
                return entry_data
        elif value.get("__type__") == "datetime":
            try:
                from datetime import datetime
                return datetime.fromisoformat(value["value"])
            except Exception as e:
                print(f"Warning: Failed to deserialize datetime: {e}")
                return value["value"]
        # 向后兼容：检查是否是旧格式的 entry 对象
        elif "mime" in value and "value" in value and "skip" in value and "__type__" not in value:
            try:
                return entry.from_dict(value)
            except Exception as e:
                print(f"Warning: Failed to deserialize legacy entry object: {e}")
                # 递归处理嵌套字典
                # 使用 list() 创建副本，避免在迭代时字典大小变化的问题
                return {k: deserialize_value(v) for k, v in list(value.items())}
        else:
            # 递归处理嵌套字典
            # 使用 list() 创建副本，避免在迭代时字典大小变化的问题
            return {k: deserialize_value(v) for k, v in list(value.items())}
    elif isinstance(value, list):
        return [deserialize_value(item) for item in value]
    else:
        return value


class BackupManager:
    """数据库备份管理器"""
    
    def __init__(self, backup_dir: str = ".backup", max_backups: int = 10, 
                 backup_interval: int = 600, format: str = "json"):
        """
        初始化备份管理器
        
        Args:
            backup_dir: 备份目录
            max_backups: 最大备份文件数量
            backup_interval: 备份间隔（秒），默认600秒（10分钟）
            format: 备份格式，支持 "json" 和 "toml"
        """
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_interval = backup_interval
        self.format = format.lower()
        
        # 确保备份目录存在
        self.backup_dir.mkdir(exist_ok=True)
        
        # 备份线程控制
        self._backup_thread = None
        self._stop_event = threading.Event()
        self._running = False
        
        # 验证格式
        if self.format not in ["json", "toml"]:
            raise ValueError("格式必须是 'json' 或 'toml'")
        
        if self.format == "toml" and not TOML_AVAILABLE:
            print("警告: TOML 不可用，使用 JSON 格式")
            self.format = "json"
    
    def start_auto_backup(self, tables_dict_or_func):
        """启动自动备份"""
        if self._running:
            print("自动备份已在运行")
            return
        
        self._running = True
        self._stop_event.clear()
        self._backup_thread = threading.Thread(
            target=self._backup_loop,
            args=(tables_dict_or_func,),
            daemon=True
        )
        self._backup_thread.start()
        print(f"自动备份已启动，间隔 {self.backup_interval} 秒")
    
    def stop_auto_backup(self):
        """停止自动备份"""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        if self._backup_thread:
            self._backup_thread.join(timeout=5)
        print("自动备份已停止")
    
    def _backup_loop(self, tables_dict_or_func):
        """备份循环"""
        while not self._stop_event.is_set():
            try:
                # 获取最新的tables字典
                if callable(tables_dict_or_func):
                    tables_dict = tables_dict_or_func()
                else:
                    tables_dict = tables_dict_or_func
                
                # 检查是否有表需要备份
                if hasattr(tables_dict, 'get_tables_need_sync'):
                    tables_need_sync = tables_dict.get_tables_need_sync()
                    if tables_need_sync:
                        self.create_backup(tables_dict)
                else:
                    # 如果没有 get_tables_need_sync 方法，直接备份
                    self.create_backup(tables_dict)
                
                # 等待下次备份
                self._stop_event.wait(self.backup_interval)
            except Exception as e:
                print(f"备份过程中出错: {e}")
                self._stop_event.wait(60)  # 出错后等待1分钟再试
    
    def create_backup(self, tables_dict: Dict[str, Any]) -> str:
        """
        创建备份
        
        Args:
            tables_dict: 表字典，通常是 Database.tables
            
        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.{self.format}"
        backup_path = self.backup_dir / filename
        
        try:
            # 收集所有表的数据
            backup_data = {
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "format_version": "1.0",
                "tables": {}
            }
            
            # 遍历所有表
            print(f"\n开始备份，共 {len(tables_dict)} 个表:")
            for table_name, table in tables_dict.items():
                if hasattr(table, 'get_all_data'):
                    table_data = table.get_all_data()
                    raw_data = table_data.get("data", {})
                    # 打印表信息
                    if isinstance(raw_data, dict):
                        entry_count = len(raw_data)
                        print(f"  表 {table_name}: {entry_count} 条记录", end="")
                        # 如果是 PUB 表，显示一些条目键
                        if table_name == "PUB" and entry_count > 0:
                            keys = list(raw_data.keys())[:5]  # 只显示前5个
                            print(f" (示例键: {', '.join(keys)}{'...' if entry_count > 5 else ''})")
                            # 检查是否有 timer entry，并打印其内容
                            timer_count = 0
                            timer_entries = []
                            # 使用 list() 创建副本，避免在迭代时字典大小变化的问题
                            for key, value in list(raw_data.items()):
                                is_timer = False
                                timer_content = None
                                
                                # 检查是否是 timer entry
                                if isinstance(value, dict):
                                    if value.get("mime") == "timer":
                                        is_timer = True
                                        # 尝试从字典中获取文本内容
                                        value_dict = value.get("value", {})
                                        if isinstance(value_dict, dict):
                                            timer_content = value_dict.get("text", "")
                                elif hasattr(value, 'mime') and value.mime == "timer":
                                    is_timer = True
                                    # 尝试获取文本内容
                                    try:
                                        if hasattr(value, 'to_text'):
                                            timer_content = value.to_text()
                                        elif hasattr(value, 'value'):
                                            val = value.value
                                            if isinstance(val, dict):
                                                timer_content = val.get("text", "")
                                    except Exception as e:
                                        timer_content = f"[无法获取内容: {e}]"
                                
                                if is_timer:
                                    timer_count += 1
                                    timer_entries.append((key, timer_content))
                            
                            if timer_count > 0:
                                print(f"    - 包含 {timer_count} 个 timer entry:")
                                for timer_key, timer_content in timer_entries:
                                    if timer_content:
                                        # 打印 timer 内容，每行前面加缩进
                                        content_lines = timer_content.split('\n')
                                        for line in content_lines[:10]:  # 最多显示前10行
                                            print(f"      [{timer_key}] {line}")
                                        if len(content_lines) > 10:
                                            print(f"      [{timer_key}] ... (还有 {len(content_lines) - 10} 行)")
                                    else:
                                        print(f"      [{timer_key}] (无内容)")
                        else:
                            print()
                    else:
                        print(f"  表 {table_name}: 数据格式 {type(raw_data).__name__}")
                    
                    # 序列化表数据（在序列化前先处理 timer entry）
                    # 对于 PUB 表，确保 timer entry 被正确转换
                    if table_name == "PUB" and isinstance(raw_data, dict):
                        processed_data = {}
                        # 使用 list() 创建副本，避免在迭代时字典大小变化的问题
                        for key, entry_value in list(raw_data.items()):
                            # 在序列化前，如果是 timer entry，尝试从 Text 获取实际内容
                            if isinstance(entry_value, entry) and hasattr(entry_value, 'mime') and entry_value.mime == "timer":
                                # 如果 value 是 None，尝试从 Text 表中获取实际内容
                                if entry_value.value is None or (hasattr(entry_value, '_value') and entry_value._value is None):
                                    try:
                                        from Port.Text import Text
                                        text_data = Text.get_data(key)
                                        if text_data and hasattr(text_data, 'value'):
                                            text_value = text_data.value
                                            if isinstance(text_value, dict):
                                                text_content = text_value.get("text", "")
                                                saved_time = text_value.get("lastSavedTime", datetime.now())
                                                # 创建包含文本内容的 entry 用于序列化
                                                text_entry = entry(
                                                    mime="text",
                                                    value={
                                                        "text": text_content,
                                                        "lastSavedTime": saved_time
                                                    }
                                                )
                                                result = text_entry.to_dict()
                                                result["__type__"] = "entry"
                                                result["_original_mime"] = "timer"
                                                processed_data[key] = result
                                                continue
                                    except Exception as e:
                                        print(f"Warning: 无法从 Text 获取 timer entry {key} 的内容: {e}")
                                
                                # 如果无法从 Text 获取，使用 serialize_value 处理
                                processed_data[key] = serialize_value(entry_value)
                            else:
                                processed_data[key] = serialize_value(entry_value)
                        raw_data = processed_data
                    
                    # 序列化表数据
                    serialized_data = {
                        "name": table_data.get("name"),
                        "data": serialize_value(raw_data),
                        "sync_required": table_data.get("sync_required", False)
                    }
                    backup_data["tables"][table_name] = serialized_data
                else:
                    # 如果没有 get_all_data 方法，使用 inner 属性
                    inner_data = getattr(table, 'inner', {})
                    if isinstance(inner_data, dict):
                        entry_count = len(inner_data)
                        print(f"  表 {table_name}: {entry_count} 条记录")
                    else:
                        print(f"  表 {table_name}: 数据格式 {type(inner_data).__name__}")
                    
                    backup_data["tables"][table_name] = {
                        "name": table_name,
                        "data": serialize_value(inner_data),
                        "sync_required": False
                    }
            print(f"备份数据收集完成，开始保存...")
            
            # 保存备份文件
            if self.format == "json":
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
            elif self.format == "toml":
                # TOML 需要先序列化为兼容格式
                with open(backup_path, 'w', encoding='utf-8') as f:
                    # 使用 toml 库，它会自动处理多行字符串
                    # 长文本会自动使用 """ 多行语法
                    toml.dump(backup_data, f)
            
            print(f"+ {backup_path}")
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            # 标记所有表已备份
            self._mark_tables_synced(tables_dict)
            
            return str(backup_path)
            
        except Exception as e:
            print(f"创建备份失败: {e}")
            # 删除可能的不完整文件
            if backup_path.exists():
                backup_path.unlink()
            raise
    
    def _cleanup_old_backups(self):
        """清理旧备份文件"""
        try:
            # 获取所有备份文件
            backup_files = list(self.backup_dir.glob(f"backup_*.{self.format}"))
            
            if len(backup_files) <= self.max_backups:
                return
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 删除多余的备份文件
            files_to_delete = backup_files[self.max_backups:]
            for file_path in files_to_delete:
                file_path.unlink()
                print(f"- {file_path}")
                
        except Exception as e:
            print(f"清理旧备份时出错: {e}")
    
    def _mark_tables_synced(self, tables_dict: Dict[str, Any]):
        """标记所有表已备份"""
        try:
            for table in tables_dict.values():
                if hasattr(table, 'mark_synced'):
                    table.mark_synced()
        except Exception as e:
            print(f"标记表已备份时出错: {e}")
    
    def load_latest_backup(self, tables_dict: Dict[str, Any]) -> bool:
        """
        加载最新备份
        
        Args:
            tables_dict: 表字典
            
        Returns:
            是否成功加载
        """
        try:
            # 查找最新备份文件
            backup_files = list(self.backup_dir.glob(f"backup_*.{self.format}"))
            if not backup_files:
                print("没有找到备份文件")
                return False
            
            # 按修改时间排序，获取最新的
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            print(f"加载最新备份: {latest_backup}")
            
            # 加载备份数据
            if self.format == "json":
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
            elif self.format == "toml":
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    backup_data = toml.load(f)
            
            # 恢复表数据
            restored_tables = 0
            for table_name, table_data in backup_data.get("tables", {}).items():
                if table_name in tables_dict:
                    table = tables_dict[table_name]
                    
                    # 恢复表数据，使用反序列化
                    if hasattr(table, 'inner'):
                        serialized_data = table_data.get("data", {})
                        table.inner = deserialize_value(serialized_data)
                    
                    # 恢复其他属性
                    if hasattr(table, 'lastModifiedTime'):
                        table.lastModifiedTime = table_data.get("lastModifiedTime")
                    
                    restored_tables += 1
            
            print(f"成功恢复 {restored_tables} 个表的数据")
            return True
            
        except Exception as e:
            print(f"加载备份失败: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份文件"""
        backups = []
        try:
            backup_files = list(self.backup_dir.glob(f"backup_*.{self.format}"))
            for file_path in backup_files:
                stat = file_path.stat()
                backups.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            # 按修改时间排序
            backups.sort(key=lambda x: x["modified"], reverse=True)
            
        except Exception as e:
            print(f"列出备份文件时出错: {e}")
        
        return backups
    
    def get_backup_info(self) -> Dict[str, Any]:
        """获取备份系统信息"""
        backups = self.list_backups()
        return {
            "backup_dir": str(self.backup_dir),
            "format": self.format,
            "max_backups": self.max_backups,
            "backup_interval": self.backup_interval,
            "running": self._running,
            "total_backups": len(backups),
            "latest_backup": backups[0] if backups else None
        }
