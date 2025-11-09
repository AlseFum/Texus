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

# MIME 类型到 entry 类的映射
_ENTRY_CLASS_REGISTRY = {}

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


def register_entry_class(mime: str, entry_class: type):
    """注册 MIME 类型对应的 entry 类
    
    Args:
        mime: MIME 类型
        entry_class: entry 类或其子类
    """
    _ENTRY_CLASS_REGISTRY[mime] = entry_class


def get_entry_class(mime: str) -> type:
    """获取 MIME 类型对应的 entry 类
    
    Args:
        mime: MIME 类型
    
    Returns:
        entry 类或其子类，默认返回 entry
    """
    return _ENTRY_CLASS_REGISTRY.get(mime, entry)


class CustomJSONEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，处理特殊对象"""
    
    def default(self, obj):
        # 处理 entry 对象
        if isinstance(obj, entry):
            return obj.to_dict()
        
        # 处理 datetime 对象
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # 其他对象使用默认处理
        return super().default(obj)


def serialize_value(value):
    """递归序列化值，将 entry 对象转换为字典"""
    if isinstance(value, entry):
        # 使用 entry 的 to_dict 方法（可能被子类覆写）
        return value.to_dict()
    elif isinstance(value, datetime):
        # datetime 转为 ISO 字符串
        return value.isoformat()
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in list(value.items())}
    elif isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    else:
        return value


def deserialize_value(value):
    """递归反序列化值，将字典转换回 entry 对象"""
    if isinstance(value, dict):
        # 检查是否是 entry 对象（通过必需字段判断）
        if "mime" in value and "value" in value:
            mime_type = value.get("mime")
            entry_class = get_entry_class(mime_type)
            return entry_class.from_dict(value)
        # 递归处理嵌套字典
        return {k: deserialize_value(v) for k, v in list(value.items())}
    elif isinstance(value, list):
        return [deserialize_value(item) for item in value]
    elif isinstance(value, str) and 'T' in value and len(value) > 18:
        # 简单检测 ISO datetime 格式并尝试解析
        return datetime.fromisoformat(value) if value.count('-') >= 2 and ':' in value else value
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
            format: 备份格式，支持 "json"、"toml" 和 "line"
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
        if self.format not in ["json", "toml", "line"]:
            raise ValueError("格式必须是 'json'、'toml' 或 'line'")
        
        if self.format == "toml" and not TOML_AVAILABLE:
            print("警告: TOML 不可用，使用 JSON 格式")
            self.format = "json"
        
        # 日志开关（默认安静，设置环境变量 TEXUS_BACKUP_VERBOSE=1 开启详细日志）
        self.verbose = str(os.getenv("TEXUS_BACKUP_VERBOSE", "0")).lower() in ("1", "true", "yes", "on")
    
    def _log(self, message: str):
        """受控日志：仅在 verbose 启用时输出"""
        if self.verbose:
            print(message)
    
    def start_auto_backup(self, tables_dict_or_func):
        """启动自动备份"""
        if self._running:
            self._log("自动备份已在运行")
            return
        
        self._running = True
        self._stop_event.clear()
        self._backup_thread = threading.Thread(
            target=self._backup_loop,
            args=(tables_dict_or_func,),
            daemon=True
        )
        self._backup_thread.start()
        self._log(f"自动备份已启动，间隔 {self.backup_interval} 秒")
    
    def stop_auto_backup(self):
        """停止自动备份"""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        if self._backup_thread:
            self._backup_thread.join(timeout=5)
        self._log("自动备份已停止")
    
    def _backup_loop(self, tables_dict_or_func):
        """备份循环"""
        while not self._stop_event.is_set():
            # 获取最新的tables字典
            tables_dict = tables_dict_or_func() if callable(tables_dict_or_func) else tables_dict_or_func
            
            # 检查是否有表需要备份
            if not hasattr(tables_dict, 'get_tables_need_sync') or tables_dict.get_tables_need_sync():
                self.create_backup(tables_dict)
            
            # 等待下次备份
            self._stop_event.wait(self.backup_interval)
    
    def create_backup(self, tables_dict: Dict[str, Any]) -> str:
        """
        创建备份
        
        Args:
            tables_dict: 表字典，通常是 Database.tables
            
        Returns:
            备份文件路径
        """
        # 如果是 line 格式，调用专门的方法
        if self.format == "line":
            return self.create_backup_line_format(tables_dict)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.{self.format}"
        backup_path = self.backup_dir / filename
        
        try:
            # 收集所有表的数据 - 直接使用字典，不添加元数据
            backup_data = {}
            
            # 遍历所有表
            self._log(f"\n开始备份，共 {len(tables_dict)} 个表:")
            for table_name, table in tables_dict.items():
                if hasattr(table, 'get_all_data'):
                    table_data = table.get_all_data()
                    raw_data = table_data.get("data", {})
                    entry_count = len(raw_data) if isinstance(raw_data, dict) else 0
                    self._log(f"  表 {table_name}: {entry_count} 条记录")
                    
                    # 直接序列化表数据，不添加额外包装
                    backup_data[table_name] = serialize_value(raw_data)
                else:
                    # 如果没有 get_all_data 方法，使用 inner 属性
                    inner_data = getattr(table, 'inner', {})
                    entry_count = len(inner_data) if isinstance(inner_data, dict) else 0
                    self._log(f"  表 {table_name}: {entry_count} 条记录")
                    
                    # 直接序列化
                    backup_data[table_name] = serialize_value(inner_data)
            self._log(f"备份数据收集完成，开始保存...")
            
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
            
            self._log(f"+ {backup_path}")
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            # 标记所有表已备份
            self._mark_tables_synced(tables_dict)
            
            return str(backup_path)
        except Exception as e:
            print(f"创建备份失败: {e}")
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def _cleanup_old_backups(self):
        """清理旧备份文件"""
        # 根据格式确定文件扩展名
        if self.format == "line":
            extension = "txt"
        else:
            extension = self.format
        
        backup_files = list(self.backup_dir.glob(f"backup_*.{extension}"))
        
        if len(backup_files) <= self.max_backups:
            return
        
        # 按修改时间排序，删除多余的
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for file_path in backup_files[self.max_backups:]:
            file_path.unlink()
            self._log(f"- {file_path}")
    
    def _mark_tables_synced(self, tables_dict: Dict[str, Any]):
        """标记所有表已备份"""
        for table in tables_dict.values():
            if hasattr(table, 'mark_synced'):
                table.mark_synced()
    
    def load_latest_backup(self, tables_dict: Dict[str, Any]) -> bool:
        """
        加载最新备份
        
        Args:
            tables_dict: 表字典
            
        Returns:
            是否成功加载
        """
        # 如果是 line 格式，调用专门的方法
        if self.format == "line":
            return self.load_backup_line_format(tables_dict)
        
        # 查找最新备份文件
        backup_files = list(self.backup_dir.glob(f"backup_*.{self.format}"))
        if not backup_files:
            self._log("没有找到备份文件")
            return False
        
        # 按修改时间排序，获取最新的
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        self._log(f"加载最新备份: {latest_backup}")
        
        # 加载备份数据
        with open(latest_backup, 'r', encoding='utf-8') as f:
            backup_data = json.load(f) if self.format == "json" else toml.load(f)
        
        # 恢复表数据
        restored_tables = 0
        
        # 兼容旧格式（有 "tables" 键）和新格式（直接是表数据）
        if "tables" in backup_data and isinstance(backup_data.get("tables"), dict):
            # 旧格式兼容
            tables_data = backup_data["tables"]
            for table_name, table_data in tables_data.items():
                if table_name in tables_dict:
                    table = tables_dict[table_name]
                    if hasattr(table, 'inner'):
                        table.inner = deserialize_value(table_data.get("data", {}))
                    restored_tables += 1
        else:
            # 新格式：直接是表名到数据的映射
            for table_name, table_data in backup_data.items():
                if table_name in tables_dict:
                    table = tables_dict[table_name]
                    if hasattr(table, 'inner'):
                        table.inner = deserialize_value(table_data)
                    restored_tables += 1
        
        print(f"成功恢复 {restored_tables} 个表的数据")
        return True
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份文件"""
        # 根据格式确定文件扩展名
        if self.format == "line":
            extension = "txt"
        else:
            extension = self.format
        
        backup_files = list(self.backup_dir.glob(f"backup_*.{extension}"))
        backups = []
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
    
    def create_backup_line_format(self, tables_dict: Dict[str, Any]) -> str:
        """
        创建 line 格式的备份
        
        格式：
        Table tablename timestamp:
        - 20251108181432 mime keyname valueline
        - ...
        
        (necessary empty line)
        
        Table tablename2 timestamp:
        - ...
        
        Args:
            tables_dict: 表字典，通常是 Database.tables
            
        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.txt"
        backup_path = self.backup_dir / filename
        
        try:
            lines = []
            self._log(f"\n开始创建 line 格式备份，共 {len(tables_dict)} 个表:")
            
            # 遍历所有表
            for table_name, table in tables_dict.items():
                if hasattr(table, 'get_all_data'):
                    table_data = table.get_all_data()
                    raw_data = table_data.get("data", {})
                elif hasattr(table, 'inner'):
                    raw_data = table.inner
                else:
                    continue
                
                entry_count = len(raw_data) if isinstance(raw_data, dict) else 0
                self._log(f"  表 {table_name}: {entry_count} 条记录")
                
                if not raw_data:
                    continue
                
                # 添加表头
                table_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                lines.append(f"Table {table_name} {table_timestamp}:")
                
                # 添加每条记录
                for keyname, value in raw_data.items():
                    # 记录的时间戳（如果 value 是 entry 对象，可能有 lastModifiedTime）
                    if isinstance(value, entry):
                        if hasattr(value, 'lastModifiedTime') and value.lastModifiedTime:
                            if isinstance(value.lastModifiedTime, datetime):
                                record_timestamp = value.lastModifiedTime.strftime("%Y%m%d%H%M%S")
                            else:
                                # 如果是字符串，尝试解析
                                try:
                                    dt = datetime.fromisoformat(value.lastModifiedTime)
                                    record_timestamp = dt.strftime("%Y%m%d%H%M%S")
                                except:
                                    record_timestamp = table_timestamp
                        else:
                            record_timestamp = table_timestamp
                        
                        mime = value.mime
                        valueline = value.to_line()
                    else:
                        # 如果不是 entry 对象，直接序列化
                        record_timestamp = table_timestamp
                        mime = "raw"
                        import json
                        valueline = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
                    
                    # 转义 keyname 中的空格
                    keyname_escaped = keyname.replace(" ", "\\ ")
                    lines.append(f"- {record_timestamp} {mime} {keyname_escaped} {valueline}")
                
                # 添加空行分隔表
                lines.append("")
            
            # 写入文件
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            self._log(f"+ {backup_path}")
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            # 标记所有表已备份
            self._mark_tables_synced(tables_dict)
            
            return str(backup_path)
        except Exception as e:
            print(f"创建 line 格式备份失败: {e}")
            import traceback
            traceback.print_exc()
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def load_backup_line_format(self, tables_dict: Dict[str, Any], backup_path: str = None) -> bool:
        """
        从 line 格式备份恢复数据
        
        Args:
            tables_dict: 表字典
            backup_path: 备份文件路径，如果为 None 则加载最新的
            
        Returns:
            是否成功加载
        """
        try:
            # 如果没有指定路径，找最新的 txt 备份
            if backup_path is None:
                backup_files = list(self.backup_dir.glob("backup_*.txt"))
                if not backup_files:
                    self._log("没有找到 line 格式备份文件")
                    return False
                backup_path = max(backup_files, key=lambda x: x.stat().st_mtime)
            else:
                backup_path = Path(backup_path)
            
            self._log(f"加载 line 格式备份: {backup_path}")
            
            # 读取文件
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            current_table = None
            restored_count = 0
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    # 空行，表分隔
                    current_table = None
                    continue
                
                if line.startswith("Table "):
                    # 表头: Table tablename timestamp:
                    parts = line.split()
                    if len(parts) >= 3:
                        table_name = parts[1]
                        # timestamp = parts[2].rstrip(':')
                        
                        if table_name in tables_dict:
                            current_table = tables_dict[table_name]
                            self._log(f"  恢复表: {table_name}")
                        else:
                            self._log(f"  警告: 表 {table_name} 不存在，跳过")
                            current_table = None
                    continue
                
                if line.startswith("- ") and current_table is not None:
                    # 数据行: - 20251108181432 mime keyname valueline
                    parts = line[2:].split(' ', 3)  # 跳过 "- "，然后分割成 4 部分
                    
                    if len(parts) >= 4:
                        record_timestamp = parts[0]
                        mime = parts[1]
                        keyname = parts[2].replace("\\ ", " ")  # 反转义
                        valueline = parts[3]
                        
                        # 恢复 value
                        entry_class = get_entry_class(mime)
                        value_data = entry_class.from_line(valueline)
                        
                        # 创建 entry 对象
                        entry_obj = entry_class(mime=mime, value=value_data)
                        
                        # 设置 lastModifiedTime
                        try:
                            dt = datetime.strptime(record_timestamp, "%Y%m%d%H%M%S")
                            entry_obj.lastModifiedTime = dt
                        except:
                            pass
                        
                        # 存入表
                        if hasattr(current_table, 'inner'):
                            current_table.inner[keyname] = entry_obj
                            restored_count += 1
            
            self._log(f"成功恢复 {restored_count} 条记录")
            return True
            
        except Exception as e:
            print(f"加载 line 格式备份失败: {e}")
            import traceback
            traceback.print_exc()
            return False