from Common.base import FinalVis
from Database import Table

class Raw:
    """Raw Port - 原始数据显示"""
    
    @staticmethod
    def access(pack):
        main_table = Table.of("main")
        data = main_table.get(pack.entry)
        display_data = data if data is not None else "(empty)"
        # 如果data是entry对象，提取其文本内容
        if hasattr(display_data, 'value'):
            if isinstance(display_data.value, dict) and 'text' in display_data.value:
                display_data = display_data.value['text']
            elif hasattr(display_data, 'to_raw') and callable(display_data.to_raw):
                display_data = display_data.to_raw()
        # Web请求：只需要payload
        return FinalVis.of("raw", payload={"text": str(display_data)})

# 插件注册函数
def registry():
    return {
        "mime": "raw",
        "port": Raw
    }

