from Common.base import FinalVis
from Database import Table

class Raw:
    """Raw Port - 原始数据显示"""
    
    @staticmethod
    def access(pack):
        main_table = Table.of("main")
        data = main_table.get(pack.entry)
        return FinalVis.of("raw", data if data is not None else "(empty)")

# 插件注册函数
def registry():
    return {
        "mime": "raw",
        "port": Raw
    }

