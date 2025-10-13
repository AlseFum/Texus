from util import first_valid
from Database import pub_get, pub_set
from protocol.types import FinalVis, entry
from datetime import datetime


class Text:
    @staticmethod
    def get_data(entry):
        """从数据库获取文本数据，返回entry对象"""
        # 直接从pub表获取数据
        pub_data = pub_get(entry)
        if pub_data is None:
        # 如果没有数据，返回空的entry
          return entry(mime="text", value={"text": "No data", "lastSavedTime": None})
        if pub_data is not None:
            # 将pub数据转换为entry对象
            if isinstance(pub_data, entry):
                return pub_data
            elif isinstance(pub_data, dict):
                # 如果已经是正确格式的字典
                right_format = entry(mime="text", value={
                    "text": pub_data.get("text", ""),
                    "lastSavedTime": pub_data.get("lastSavedTime", datetime.now())
                })
                pub_set(entry, right_format)
                return right_format
            else:
                # 如果是原始字符串数据，转换为entry对象
                right_format = entry(mime="text", value={
                    "text": str(pub_data),
                    "lastSavedTime": datetime.now()
                })
                pub_set(entry, right_format._value)
                return right_format
        
    @staticmethod
    def getByWeb(pack):
        """通过Web方式获取文本"""
        text_file = Text.get_data(pack.entry or pack.path)
        return FinalVis.of("text", text_file._value.get("text", ""))
    
    @staticmethod
    def getByApi(pack):
        """通过API方式获取文本"""
        text_file = Text.get_data(pack.entry or pack.path)
        # 转换datetime对象为ISO字符串用于API返回
        response_value = {
            "text": text_file._value.get("text", ""),
            "lastSavedTime": text_file._value.get("lastSavedTime").isoformat() if text_file._value.get("lastSavedTime") else ""
        }
        return FinalVis.of("text", response_value, skip=True)
    
    @staticmethod
    def set(pack):
        """设置文本内容"""
        content = first_valid(pack.query.get('content', None), "")
        
        # 解码前端编码的内容
        try:
            import urllib.parse
            content = urllib.parse.unquote(content)
        except:
            pass  # 如果解码失败，使用原始内容
        
        # 创建entry对象，保存datetime对象
        saved_time = datetime.now()
        file_data = {
            "text": content,
            "lastSavedTime": saved_time
        }
        text_file = entry(mime="text", value=file_data)
        
        # 直接保存到pub表
        pub_set(pack.entry, text_file._value)

        print(f"Set text file: {pack.who} {pack.by} {pack.path} -> {pack.entry}", {"text": content, "lastSavedTime": saved_time.isoformat()})
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
    def access(pack):
        from protocol.types import Renderee

        """主访问方法，根据操作类型分发到相应的方法"""
        op = first_valid(pack.query.get("op", None), "get")
        
        if op == "set":
            return Text.set(pack)
        else:
            # 判断是否是 API 请求
            is_api = getattr(pack, 'by', '') == 'api'
            if is_api:
                return Text.getByApi(pack)
            else:
                return Text.getByWeb(pack)