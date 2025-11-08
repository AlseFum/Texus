from typing import Dict

class Access:
    """HTTP请求到内部访问对象的转换"""
    
    def __init__(self, path: str = "", entry: str = "", 
                 who: str = "", by: str = "", 
                 query: Dict[str, str] = None, cookies: Dict[str, str] = None,
                 suffix: str = ""):
        self.who = who
        self.by = by
        self.path = path
        self.query = query or {}
        self.cookies = cookies or {}
        self.entry = entry
        # URL 路径后缀（原本经常误称为 mime，这里单独记录为 suffix）
        self.suffix = suffix
    
    @staticmethod
    def of(who: str, by: str, path: str, 
           query: Dict[str, str] = None, cookies: Dict[str, str] = None,
           entry: str = "", suffix: str = ""):
        """兼容性工厂方法"""
        return Access(path=path, entry=entry, who=who, by=by, 
                     query=query or {}, cookies=cookies or {}, suffix=suffix)


class Renderee():
    """渲染接口，定义所有可渲染对象的基本行为
    
    约定：
    - payload: 仅用于显示层的临时数据，不参与持久化/反序列化
    - payload 与 skip 互斥：若提供 payload，则强制 skip=False；若 skip=True，则忽略 payload
    """
    
    def __init__(
        self,
        viewtype: str = "",
        value: any = None,
        skip: bool = False,
        mime: str | None = None,
        payload: Dict | None = None,
    ):
        # 兼容旧参数名 mime：若提供则优先生效
        self._viewtype = (mime if (mime and not viewtype) else viewtype) or ""
        self._value = value
        # 互斥处理：payload 优先于 skip
        if payload is not None:
            self._skip = False
            self._payload = dict(payload)
        else:
            self._skip = bool(skip)
            self._payload = None
    
    @property
    def value(self):
        """获取渲染内容"""
        return self._value
    
    # 新命名：用于 Express 渲染的视图类型
    @property
    def viewtype(self):
        return self._viewtype
    
    @viewtype.setter
    def viewtype(self, vt: str):
        self._viewtype = vt or ""
    
    # 旧命名兼容：mime 等价于 viewtype
    @property
    def mime(self):
        return self._viewtype
    
    @mime.setter
    def mime(self, m: str):
        self._viewtype = m or ""
    
    @property
    def skip(self):
        """是否应该跳过渲染"""
        return self._skip
    
    @property
    def payload(self) -> Dict | None:
        """显示层临时数据（不持久化、不反序列化）"""
        return self._payload
    
    @payload.setter
    def payload(self, data: Dict | None):
        # 设置 payload 时，强制关闭 skip
        self._payload = (dict(data) if isinstance(data, dict) else None)
        if self._payload is not None:
            self._skip = False
    
    @classmethod
    def of(
        cls,
        viewtype: str = "",
        value: any = None,
        skip: bool = False,
        mime: str | None = None,
        payload: Dict | None = None,
    ):
        """工厂方法（兼容旧的 mime 命名）"""
        vt = (mime if (mime and not viewtype) else viewtype) or ""
        return cls(viewtype=vt, value=value, skip=skip, payload=payload)

class FinalVis(Renderee):
    """Port模块的视觉内容实现"""
    pass  # 继承父类的所有功能

class entry(Renderee):
    """文件对象实现 - 存储在数据库中的内容
    
    说明：
    - viewtype 仅作为渲染辅助信息（辅助选择 Express 视图），不是业务强约束；可为空。
    - 序列化与反序列化不应强加 skip 语义，skip 仅在运行期使用。
    """
    
    def __init__(self, mime: str = "", value: any = None, skip: bool = False, viewtype: str = ""):
        # 兼容：同时接受 mime/viewtype，逻辑同 Renderee
        vt = (mime if (mime and not viewtype) else viewtype) or ""
        super().__init__(viewtype=vt, value=value, skip=skip)
        self.lastModifiedTime = None
    
    def to_dict(self):
        """将 entry 对象转换为字典"""
        return {
            # 仅保存 mime（使用内部 viewtype 值以兼容读写）
            "mime": self._viewtype,
            "value": self._value,
            "lastModifiedTime": self.lastModifiedTime
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建 entry 对象"""
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典格式")
        
        # 创建新实例
        vt = data.get("viewtype")
        if vt is None:
            vt = data.get("mime", "")
        instance = cls(
            viewtype=vt,
            value=data.get("value", None),
            # 反序列化不引入 skip 语义，保持运行期决定
            skip=False
        )
        
        # 设置 lastModifiedTime
        if "lastModifiedTime" in data:
            instance.lastModifiedTime = data["lastModifiedTime"]
        
        return instance


