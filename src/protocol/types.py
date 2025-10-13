from enum import Enum
from typing import Dict

class Access:
    def __init__(self, who: str, by: str, path: str, 
                 query: Dict[str,str], cookies: Dict[str,str], mime: str = "", 
                 entry: str = ""):
        self.who = who
        self.by = by
        self.path = path
        self.query = query
        self.cookies = cookies
        self.mime = mime
        self.entry = entry
    
    # 类属性，方便访问枚举值
    User = "user"
    Web = "web"
    Script = "script"
    Agent = "agent"
    API = "api"


class Renderee():
    """渲染接口，定义所有可渲染对象的基本行为"""
    
    def __init__(self, mime: str = "", value: any = None, skip: bool = False):
        self._mime = mime
        self._value = value
        self._skip = skip
    
    def content(self):
        """获取渲染内容"""
        return self._value
    
    def mime(self):
        """获取页面类型"""
        return self._mime
    
    def skip(self):
        """是否应该跳过渲染"""
        return self._skip
    
    @classmethod
    def of(cls, mime: str = "", value: any = None, skip: bool = False):
        """工厂方法"""
        return cls(mime, value, skip)

class FinalVis(Renderee):
    """Port模块的视觉内容实现"""
    pass  # 继承父类的所有功能

class entry(Renderee):
    """文件对象实现"""
    #
    lastModifiedTime = None
    
    def to_dict(self):
        """将 entry 对象转换为字典"""
        return {
            "mime": self._mime,
            "value": self._value,
            "skip": self._skip,
            "lastModifiedTime": self.lastModifiedTime
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建 entry 对象"""
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典格式")
        
        # 创建新实例
        instance = cls(
            mime=data.get("mime", ""),
            value=data.get("value", None),
            skip=data.get("skip", False)
        )
        
        # 设置 lastModifiedTime
        if "lastModifiedTime" in data:
            instance.lastModifiedTime = data["lastModifiedTime"]
        
        return instance