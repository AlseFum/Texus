from util import first_valid
from Database import pub_get, pub_set
from protocol.types import FinalVis, entry
from datetime import datetime


class Text:
    @staticmethod
    def get_data(entry_key) -> entry:
        """从数据库获取文本数据，返回entry对象"""
        pub_data = pub_get(entry_key)
        if pub_data is None:
            return entry(mime="text", value={"text": "No data", "lastSavedTime": None})
        
        # 统一转换为entry格式
        if isinstance(pub_data, entry):
            return pub_data
        elif isinstance(pub_data, dict):
            normalized_data = {
                "text": pub_data.get("text", ""),
                "lastSavedTime": pub_data.get("lastSavedTime", datetime.now())
            }
            result_entry = entry(mime="text", value=normalized_data)
            pub_set(entry_key, result_entry)  # 直接保存entry对象
            return result_entry
        else:
            # 原始字符串数据
            normalized_data = {
                "text": str(pub_data),
                "lastSavedTime": datetime.now()
            }
            result_entry = entry(mime="text", value=normalized_data)
            pub_set(entry_key, result_entry)  # 直接保存entry对象
            return result_entry
        
    @staticmethod
    def getByWeb(pack) -> FinalVis:
        """通过Web方式获取文本"""
        text_file = Text.get_data(pack.entry or pack.path)
        return FinalVis.of("text", text_file.value.get("text", ""))
    
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
        
        # 直接保存entry对象
        pub_set(pack.entry, text_file)
        
        response_data = {
            "success": True,
            "message": "保存成功",
            "data": {
                "text": content,
                "lastSavedTime": saved_time.isoformat()
            }
        }
        
        return FinalVis.of("text", response_data, skip=True)
    
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