from Common.util import first_valid
from Database import Table
from Common.base import FinalVis, entry
from datetime import datetime


class Text:
    @staticmethod
    def access(pack) -> FinalVis:
        """主访问方法，根据操作类型分发到相应的方法"""
        op = first_valid(pack.query.get("op", None), "get")
        
        if op == "set":
            return Text.set(pack)
        else:
            # 判断是否是 API 请求
            is_api = getattr(pack, 'by', '') == 'api'
            return Text.getByApi(pack) if is_api else Text.getByWeb(pack)
    
    @staticmethod
    def get_data(entry_key) -> entry:
        """从数据库获取文本数据，返回entry对象"""
        main_table = Table.of("main")
        data = main_table.get(entry_key)
        if data is None:
            return entry(mime="text", value={"text": "No data", "lastSavedTime": None})
        
        # 统一转换为entry格式
        if isinstance(data, entry):
            return data
        
        # 其他类型（原始字符串数据）
        normalized_data = {
            "text": str(data),
            "lastSavedTime": datetime.now()
        }
        return entry(mime="text", value=normalized_data)
        
    @staticmethod
    def getByWeb(pack) -> FinalVis:
        """通过Web方式获取文本"""
        text_file = Text.get_data(pack.entry or pack.path)
        text_content = text_file.value.get("text", "")
        # Web请求：只需要payload，Express渲染器会使用它
        return FinalVis.of("text", payload={"text": text_content})
    
    @staticmethod
    def getByApi(pack) -> FinalVis:
        """通过API方式获取文本"""
        text_file = Text.get_data(pack.entry or pack.path)
        # 安全地转换datetime对象为ISO字符串
        last_saved = text_file.value.get("lastSavedTime")
        last_saved_iso = last_saved.isoformat() if last_saved and hasattr(last_saved, 'isoformat') else ""
        
        response_value = {
            "text": text_file.value.get("text", ""),
            "lastSavedTime": last_saved_iso
        }
        return FinalVis.of("text", response_value, skip=True)
    
    @staticmethod
    def set(pack) -> FinalVis:
        """设置文本内容"""
        content = first_valid(pack.query.get('content', None), "")
        
        # 解码URL编码的内容
        try:
            import urllib.parse
            content = urllib.parse.unquote(content)
        except:
            pass
        
        # 创建entry对象
        saved_time = datetime.now()
        file_data = {
            "text": content,
            "lastSavedTime": saved_time
        }
        text_file = entry(mime="text", value=file_data)
        
        # 直接保存entry对象到主表
        main_table = Table.of("main")
        main_table.set(pack.entry, text_file)
        
        # 触发 ShadowPort 的更新
        if pack.entry:
            ShadowPort.update(pack)
        
        response_data = {
            "success": True,
            "message": "保存成功",
            "data": {
                "text": content,
                "lastSavedTime": saved_time.isoformat()
            }
        }
        
        return FinalVis.of("text", response_data, skip=True)

class ShadowPort(Text):
    portCls = set()
    
    @staticmethod
    def set(port_cls):
        """注册一个 port 类到 ShadowPort"""
        ShadowPort.portCls.add(port_cls)
    
    @staticmethod
    def update(pack):
        """当 text 内容变动时调用，更新所有注册的 port"""
        for port_cls in ShadowPort.portCls:
            try:
                # 调用 port 类的 update 方法来更新
                if hasattr(port_cls, 'update'):
                    port_cls.update(pack)
            except Exception as e:
                # 更新失败不影响主流程
                pass

# 插件注册函数
def registry():
    return {
        "mime": ["text", "note"],
        "port": Text
    }