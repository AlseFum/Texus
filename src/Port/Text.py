import json
from util import first_valid
from Database import pub_get, pub_set
from protocol.types import FinalVis, File
from datetime import datetime
from Database import Table
class TextFile(File):
    """文本文件数据类"""
    def __init__(self, text="", lastSaveTime=""):
        super().__init__(mime="text", value=text)
        self.text = text
        self.lastSaveTime = lastSaveTime
    
    def content(self):
        """返回文本内容"""
        return self.text
    def to_dict(self):
        return {
            "text": self.text,
            "lastSaveTime": self.lastSaveTime
        }
    
    @classmethod
    def of(cls, text="", lastSaveTime=""):
        """TextFile的工厂方法"""
        cls.mime="text"
        return cls(text, lastSaveTime)


class Text:
    @staticmethod
    def get_data(entry_or_path):
        """从数据库获取文本数据，返回TextFile对象"""
        text_table = Table.of("text")
        text_data = text_table.get(entry_or_path)
        
        if text_data is not None:
            # 如果从text表获取到数据，直接返回
            if isinstance(text_data, TextFile):
                return text_data
            elif isinstance(text_data, dict):
                right_format=TextFile(text=text_data.get("text", ""), 
                              lastSaveTime=text_data.get("lastSaveTime", datetime.now().isoformat()))
                text_table.set(entry_or_path, right_format.to_dict())
                return right_format
            else:
                right_format=TextFile(text=str(text_data), lastSaveTime=datetime.now().isoformat())
                text_table.set(entry_or_path, right_format.to_dict())
                return right_format
        
        # 如果text表没有数据，尝试从pub表获取
        pub_data = pub_get(entry_or_path)
        if pub_data is not None:
            # 将pub数据转换为TextFile对象
            if isinstance(pub_data, dict):
                right_format=TextFile(text=pub_data.get("text", ""), 
                              lastSaveTime=pub_data.get("lastSaveTime", datetime.now().isoformat()))
                text_table.set(entry_or_path, right_format.to_dict())
                return right_format
            else:
                right_format=TextFile(text=str(pub_data), lastSaveTime=datetime.now().isoformat())
                text_table.set(entry_or_path, right_format)
                return right_format
        
        # 如果都没有数据，返回空的TextFile
        return TextFile.of("No data","")
        # return TextFile(text="", lastSaveTime=datetime.now().isoformat())
    
    @staticmethod
    def getByWeb(pack):
        """通过Web方式获取文本"""
        text_file = Text.get_data(pack.entry or pack.path)
        return FinalVis.of("text", text_file.content())
    
    @staticmethod
    def getByApi(pack):
        """通过API方式获取文本"""
        text_file = Text.get_data(pack.entry or pack.path)
        return FinalVis.of("text", {
            "text": text_file.text,
            "lastSaveTime": text_file.lastSaveTime
        }, skip=True)
    
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
        
        # 创建TextFile对象
        text_file = TextFile(
            text=content,
            lastSaveTime=datetime.now().isoformat()
        )
        
        Table.of("text").set(pack.entry, text_file)
        
        print(f"DEBUG - pack.who: {pack.who}, pack.by: {pack.by}, pack.path: {pack.path}, pack.entry: {pack.entry}")
        print(f"Set text file: {pack.who} {pack.by} {pack.path} -> {pack.entry}", text_file.to_dict())
        response_data = {
            "success": True,
            "message": "保存成功",
            "data": text_file.to_dict()
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