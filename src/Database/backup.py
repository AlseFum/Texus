"""
数据库备份系统

功能：
- 自动备份：每分钟保存一次数据库状态
- 备份管理：保留最新 10 个备份文件
- 数据恢复：从备份文件恢复数据库
"""

from datetime import datetime
import json
import asyncio
from pathlib import Path
from protocol.types import File

# 备份配置
BACKUP_DIR = Path(__file__).parent / "backups"
BACKUP_INTERVAL = 60  # 秒
MAX_BACKUPS = 10      # 保留的备份数量


def serialize_table(table) -> dict:
    """序列化表数据
    
    Args:
        table: Table 对象
    
    Returns:
        序列化后的字典
    """
    serialized = {}
    for key, value in table.inner.items():
        if isinstance(value, File):
            # File 对象转为字典
            serialized[key] = {
                "_type": "File",
                "mime": value._mime,
                "value": value._value
            }
        elif isinstance(value, dict):
            serialized[key] = {
                "_type": "dict",
                "data": value
            }
        else:
            serialized[key] = {
                "_type": "raw",
                "data": value
            }
    return serialized


def deserialize_table(data: dict, table):
    """反序列化表数据
    
    Args:
        data: 序列化的数据
        table: 目标 Table 对象
    """
    for key, item in data.items():
        if item.get("_type") == "File":
            table.set(key, File(mime=item["mime"], value=item["value"]))
        elif item.get("_type") == "dict":
            table.set(key, item["data"])
        else:
            table.set(key, item.get("data"))


def save_backup():
    """保存当前数据库状态为备份文件
    
    Returns:
        备份文件的 Path 对象，失败则返回 None
    """
    try:
        from . import tables  # 导入全局 tables 字典
        
        # 创建备份目录
        BACKUP_DIR.mkdir(exist_ok=True)
        
        # 生成备份文件名（时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"db_backup_{timestamp}.bak"
        
        # 序列化所有表
        backup_data = {
            "timestamp": timestamp,
            "tables": {}
        }
        
        for table_name, table in tables.items():
            backup_data["tables"][table_name] = serialize_table(table)
        
        # 保存到文件
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✓ 数据库已备份: {backup_file.name}")
        
        # 清理旧备份
        cleanup_old_backups()
        
        return backup_file
    
    except Exception as e:
        print(f"✗ 备份失败: {e}")
        return None


def cleanup_old_backups():
    """清理旧备份，只保留最新的 MAX_BACKUPS 个"""
    try:
        # 获取所有备份文件
        backup_files = list(BACKUP_DIR.glob("db_backup_*.bak"))
        
        if len(backup_files) <= MAX_BACKUPS:
            return
        
        # 按修改时间排序（最新的在前）
        backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # 删除多余的备份
        for old_backup in backup_files[MAX_BACKUPS:]:
            old_backup.unlink()
            print(f"  - 删除旧备份: {old_backup.name}")
    
    except Exception as e:
        print(f"✗ 清理备份失败: {e}")


def load_latest_backup():
    """加载最新的备份
    
    Returns:
        成功返回 True，失败返回 False
    """
    try:
        from . import Table  # 导入 Table 类
        
        if not BACKUP_DIR.exists():
            print("ℹ 无备份目录")
            return False
        
        # 获取所有备份文件
        backup_files = list(BACKUP_DIR.glob("db_backup_*.bak"))
        
        if not backup_files:
            print("ℹ 无备份文件")
            return False
        
        # 获取最新的备份
        latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
        
        # 加载备份
        with open(latest_backup, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # 恢复所有表
        for table_name, table_data in backup_data["tables"].items():
            table = Table.of(table_name)
            deserialize_table(table_data, table)
        
        print(f"✓ 已从备份恢复: {latest_backup.name}")
        return True
    
    except Exception as e:
        print(f"✗ 加载备份失败: {e}")
        return False


def list_backups():
    """列出所有备份
    
    Returns:
        备份文件信息列表
    """
    if not BACKUP_DIR.exists():
        return []
    
    backup_files = list(BACKUP_DIR.glob("db_backup_*.bak"))
    backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    return [
        {
            "file": f.name,
            "size": f.stat().st_size,
            "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        }
        for f in backup_files
    ]


async def auto_backup_loop():
    """自动备份循环任务"""
    print(f"🔄 自动备份已启动 (间隔: {BACKUP_INTERVAL}秒, 保留: {MAX_BACKUPS}个)")
    
    while True:
        try:
            await asyncio.sleep(BACKUP_INTERVAL)
            save_backup()
        except asyncio.CancelledError:
            print("🛑 自动备份已停止")
            break
        except Exception as e:
            print(f"✗ 自动备份错误: {e}")


def start_auto_backup():
    """启动自动备份（在 FastAPI 启动时调用）
    
    Returns:
        asyncio.Task 对象
    """
    return asyncio.create_task(auto_backup_loop())

