from protocol.types import entry
from .backup import BackupManager
from .table import Table

tables={}
backup_manager = None
def pub_get(entry):
    """获取公共条目"""
    pub_table = Table.of("PUB")
    return pub_table.get(entry, None)

def pub_set(entry, value):
    """设置公共条目"""
    pub_table = Table.of("PUB")
    return pub_table.set(entry, value)

def hid_set(entry, value):
    """设置私有条目"""
    hid_table = Table.of("HID")
    return hid_table.set(entry, value)

def hid_get(entry):
    """获取私有条目"""
    hid_table = Table.of("HID")
    return hid_table.get(entry, None)
def claim(path,mime):
    """声明MIME类型"""
    mime_table = Table.of("MIME")
    if mime_table.get(path) is None:
        mime_table.set(path, mime)
        return True
    else:
        return False

def getmime(path):
    """获取MIME类型"""
    mime_table = Table.of("MIME")
    return mime_table.get(path, None)

from datetime import datetime

# 初始化一些基础数据
Table.of("PUB").set("a", entry(mime="text", value={
    "text": "text text", 
    "lastSavedTime": datetime.now()
}))

# 加载 Gen 测试用例
from .test_cases import load_test_cases
load_test_cases(Table.of("PUB"))

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
    backup_manager.load_latest_backup(tables)
    
    # 启动自动备份
    backup_manager.start_auto_backup(tables)
    
    print(f"备份系统已初始化: {backup_dir}, 格式: {format}, 间隔: {backup_interval}秒")
    return backup_manager

def stop_backup_system():
    """停止备份系统"""
    global backup_manager
    if backup_manager:
        backup_manager.stop_auto_backup()
        backup_manager = None
        print("备份系统已停止")

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