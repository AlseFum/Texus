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
from protocol.types import entry

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


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
        # 使用 entry 的 to_dict 方法
        return value.to_dict()
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    else:
        return value


def deserialize_value(value):
    """递归反序列化值，将字典转换回 entry 对象"""
    if isinstance(value, dict):
        # 检查是否是 entry 对象的序列化形式
        if "mime" in value and "value" in value and "skip" in value:
            try:
                return entry.from_dict(value)
            except:
                # 如果转换失败，返回原始字典
                pass
        
        # 递归处理嵌套字典
        return {k: deserialize_value(v) for k, v in value.items()}
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
    
    def start_auto_backup(self, tables_dict: Dict[str, Any]):
        """启动自动备份"""
        if self._running:
            print("自动备份已在运行")
            return
        
        self._running = True
        self._stop_event.clear()
        self._backup_thread = threading.Thread(
            target=self._backup_loop,
            args=(tables_dict,),
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
    
    def _backup_loop(self, tables_dict: Dict[str, Any]):
        """备份循环"""
        while not self._stop_event.is_set():
            try:
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
            for table_name, table in tables_dict.items():
                if hasattr(table, 'get_all_data'):
                    table_data = table.get_all_data()
                    # 序列化表数据
                    serialized_data = {
                        "name": table_data.get("name"),
                        "data": serialize_value(table_data.get("data", {})),
                        "sync_required": table_data.get("sync_required", False)
                    }
                    backup_data["tables"][table_name] = serialized_data
                else:
                    # 如果没有 get_all_data 方法，使用 inner 属性
                    backup_data["tables"][table_name] = {
                        "name": table_name,
                        "data": serialize_value(getattr(table, 'inner', {})),
                        "sync_required": False
                    }
            
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
            
            print(f"备份已创建: {backup_path}")
            
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
                print(f"已删除旧备份: {file_path}")
                
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
