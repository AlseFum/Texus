from typing import Dict
from enum import Enum

class WhoType(Enum):
    """访问者类型枚举"""
    USER = "user"
    AGENT = "agent"

class ByType(Enum):
    """访问方式类型枚举"""
    WEB = "web"
    API = "api"
    SCRIPT = "script"
    AGENT = "agent"

class Access:
    """HTTP请求到内部访问对象的转换"""
    
    def __init__(self, path: str = "", mime: str = "", entry: str = "", 
                 who: str = "", by: str = "", 
                 query: Dict[str, str] = None, cookies: Dict[str, str] = None):
        self.who = who
        self.by = by
        self.path = path
        self.query = query or {}
        self.cookies = cookies or {}
        self.mime = mime
        self.entry = entry
    
    @staticmethod
    def of(who: str, by: str, path: str, 
           query: Dict[str, str] = None, cookies: Dict[str, str] = None,
           mime: str = "", entry: str = ""):
        """兼容性工厂方法"""
        return Access(path=path, mime=mime, entry=entry, who=who, by=by, 
                     query=query or {}, cookies=cookies or {})


class Renderee():
    """渲染接口，定义所有可渲染对象的基本行为"""
    
    def __init__(self, mime: str = "", value: any = None, skip: bool = False):
        self._mime = mime
        self._value = value
        self._skip = skip
    
    @property
    def value(self):
        """获取渲染内容"""
        return self._value
    
    @property
    def mime(self):
        """获取页面类型"""
        return self._mime
    
    @property
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
    """文件对象实现 - 存储在数据库中的内容"""
    
    def __init__(self, mime: str = "", value: any = None, skip: bool = False):
        super().__init__(mime, value, skip)
        self.lastModifiedTime = None
    
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