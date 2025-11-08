from Common.base import entry
from .backup import BackupManager
from .table import Table
from datetime import datetime
import re

tables = {}
backup_manager = None

# 日志
from Common.logger import get_logger
logger = get_logger("database")

def getmime(entry_key):
    """从主表获取 entry 的 MIME 类型"""
    main_table = Table.of("main")
    data = main_table.get(entry_key)
    if isinstance(data, entry):
        return data.mime
    return None

class vmAPI:
    """为用户脚本提供的数据库操作API - 直接操作主表"""
    
    def __init__(self):
        self.operations = []  # 记录操作历史
        self.main = Table.of("main")
    
    def get(self, key: str) -> entry:
        """获取entry对象"""
        result = self.main.get(key)
        self.operations.append(f"GET {key}")
        if isinstance(result, entry):
            return result
        elif isinstance(result, dict):
            return entry(mime="text", value=result)
        else:
            return entry(mime="text", value={"text": str(result or ""), "lastSavedTime": None})
    
    def set(self, key: str, content: str, mime: str = "text") -> bool:
        """设置entry内容"""
        try:
            file_data = {
                "text": str(content),
                "lastSavedTime": datetime.now()
            }
            new_entry = entry(mime=mime, value=file_data)
            self.main.set(key, new_entry)
            self.operations.append(f"SET {key}")
            return True
        except Exception as e:
            self.operations.append(f"SET {key} FAILED: {e}")
            return False
    
    def list_keys(self, pattern: str = None) -> list:
        """列出所有键，可选择模式匹配"""
        all_keys = list(self.main.inner.keys())
        
        if pattern:
            # 简单的通配符匹配
            pattern = pattern.replace('*', '.*').replace('?', '.')
            regex = re.compile(pattern)
            filtered_keys = [key for key in all_keys if regex.match(key)]
            self.operations.append(f"LIST {pattern} -> {len(filtered_keys)} keys")
            return filtered_keys
        else:
            self.operations.append(f"LIST ALL -> {len(all_keys)} keys")
            return all_keys
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        result = self.main.get(key) is not None
        self.operations.append(f"EXISTS {key} -> {result}")
        return result
    
    def delete(self, key: str) -> bool:
        """删除entry"""
        try:
            if key in self.main.inner:
                del self.main.inner[key]
                self.main.sync()
                self.operations.append(f"DELETE {key}")
                return True
            else:
                self.operations.append(f"DELETE {key} NOT_FOUND")
                return False
        except Exception as e:
            self.operations.append(f"DELETE {key} FAILED: {e}")
            return False
    
    def copy(self, from_key: str, to_key: str) -> bool:
        """复制entry"""
        try:
            source = self.get(from_key)
            if source and source.value.get("text"):
                result = self.set(to_key, source.value.get("text", ""), source.mime)
                if result:
                    self.operations.append(f"COPY {from_key} -> {to_key}")
                return result
            else:
                self.operations.append(f"COPY {from_key} -> {to_key} FAILED: source not found")
                return False
        except Exception as e:
            self.operations.append(f"COPY {from_key} -> {to_key} FAILED: {e}")
            return False

# 初始化主表和一些基础数据
main_table = Table.of("main")
main_table.set("a", entry(mime="text", value={
    "text": "text text", 
    "lastSavedTime": datetime.now()
}))

# 加载 Gen 测试用例
from .test_cases import load_test_cases
# load_test_cases(main_table)

def init_backup_system(backup_dir: str = ".backup", max_backups: int = 10, 
                      backup_interval: int = 600, format: str = "json"):
    """初始化备份系统"""
    global backup_manager
    backup_manager = BackupManager(
        backup_dir=backup_dir,
        max_backups=max_backups,
        backup_interval=backup_interval,
        format=format
    )
    
    # 启动时加载最新备份
    logger.info("加载最新备份...")
    backup_manager.load_latest_backup(tables)
    
    # 启动自动备份
    logger.info(f"启动自动备份: 目录={backup_dir}, 格式={format}, 间隔={backup_interval}秒")
    backup_manager.start_auto_backup(tables)
    
    logger.info(f"备份系统初始化完成")
    return backup_manager

def stop_backup_system():
    """停止备份系统"""
    global backup_manager
    if backup_manager:
        backup_manager.stop_auto_backup()
        backup_manager = None
        logger.info("备份系统已停止")

def get_backup_manager():
    """获取备份管理器"""
    return backup_manager

def create_manual_backup():
    """手动创建备份"""
    global backup_manager
    if backup_manager:
        return backup_manager.create_backup(tables)
    else:
        print("备份系统未初始化")
        return None

def get_backup_info():
    """获取备份信息"""
    global backup_manager
    if backup_manager:
        return backup_manager.get_backup_info()
    else:
        return {"error": "备份系统未初始化"}