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


class Renderee:
    """渲染对象 - 用于表示层的数据包装
    
    属性：
    - viewtype: 视图类型（用于选择渲染器）
    - value: 渲染内容
    - skip: 是否跳过渲染直接返回 value
    - payload: 显示层临时数据（不持久化）
    """
    
    def __init__(self, viewtype: str = "", value: any = None, skip: bool = False, payload: Dict = None):
        self.viewtype = viewtype
        self.value = value
        self.skip = skip
        self.payload = payload
    
    @classmethod
    def of(cls, viewtype: str = "", value: any = None, skip: bool = False, payload: Dict = None):
        """工厂方法
        
        使用指南：
        - Web请求（需要渲染）：只传 viewtype 和 payload
          例：FinalVis.of("text", payload={"text": content})
        
        - API请求（返回JSON）：只传 viewtype、value 和 skip=True
          例：FinalVis.of("text", value={"success": True}, skip=True)
        """
        return cls(viewtype=viewtype, value=value, skip=skip, payload=payload)

class FinalVis(Renderee):
    """Port模块的视觉内容实现"""
    pass  # 继承父类的所有功能

class entry:
    """文件对象 - 存储在数据库中的内容
    
    纯数据类，专注于持久化存储。
    通过 to_renderee() 方法可转换为 Renderee 对象用于渲染。
    """
    
    def __init_subclass__(cls, mime: str = None, **kwargs):
        """子类初始化时自动注册到备份系统
        
        使用方式:
            class TimerEntry(entry, mime="timer"):
                ...
        """
        super().__init_subclass__(**kwargs)
        if mime:
            # 延迟导入避免循环依赖
            from Database.backup import register_entry_class
            register_entry_class(mime, cls)
    
    def __init__(self, mime: str = "", value: any = None):
        self.mime = mime
        self.value = value
        self.lastModifiedTime = None
    
    def to_dict(self):
        """转换为字典（用于持久化）"""
        from datetime import datetime
        
        def _serialize_value(val):
            """递归序列化 value 字段"""
            if isinstance(val, datetime):
                return val.isoformat()
            elif isinstance(val, dict):
                return {k: _serialize_value(v) for k, v in val.items()}
            elif isinstance(val, (list, tuple)):
                return [_serialize_value(item) for item in val]
            else:
                return val
        
        result = {
            "mime": self.mime,
            "value": _serialize_value(self.value)
        }
        
        # 只有 lastModifiedTime 存在时才包含
        if self.lastModifiedTime is not None:
            result["lastModifiedTime"] = self.lastModifiedTime.isoformat() if isinstance(self.lastModifiedTime, datetime) else self.lastModifiedTime
        
        return result
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建 entry 对象（用于反序列化）"""
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典格式")
        
        instance = cls(
            mime=data.get("mime", ""),
            value=data.get("value")
        )
        instance.lastModifiedTime = data.get("lastModifiedTime")
        return instance
    
    def to_renderee(self, skip: bool = False, payload: Dict = None):
        """转换为可渲染对象"""
        return Renderee(
            viewtype=self.mime,
            value=self.value,
            skip=skip,
            payload=payload
        )
    
    def to_line(self) -> str:
        """将 value 转换为单行文本表示
        
        使用 JSON 单行格式，并对换行符等特殊字符进行转义
        """
        import json
        from datetime import datetime
        
        def _serialize_for_line(val):
            """递归序列化为 JSON 可接受的格式"""
            if isinstance(val, datetime):
                return val.isoformat()
            elif isinstance(val, dict):
                return {k: _serialize_for_line(v) for k, v in val.items()}
            elif isinstance(val, (list, tuple)):
                return [_serialize_for_line(item) for item in val]
            else:
                return val
        
        serialized = _serialize_for_line(self.value)
        # 使用 separators 参数确保紧凑单行输出
        line = json.dumps(serialized, ensure_ascii=False, separators=(',', ':'))
        return line
    
    @classmethod
    def from_line(cls, line: str):
        """从单行文本恢复 value
        
        Args:
            line: JSON 格式的单行文本
            
        Returns:
            解析后的 value
        """
        import json
        return json.loads(line)


