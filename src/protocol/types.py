from enum import Enum
from typing import Dict
class Accessor(Enum):
    User="user"
    Script="script"
    Agent="agent"
class AccessPlatform(Enum):
    Web="web"
    API="api"
class Access:
    def __init__(self, who: Accessor, by: AccessPlatform, path: str, 
                 query: Dict[str,str], cookies: Dict[str,str], mime: str = "", 
                 entry: str = "", body: Dict = None):
        self.who = who
        self.by = by
        self.path = path
        self.query = query
        self.cookies = cookies
        self.mime = mime
        self.entry = entry
        self.body = body or {}
    
    # 类属性，方便访问枚举值
    User = Accessor.User
    Web = AccessPlatform.Web
    Script = Accessor.Script
    Agent = Accessor.Agent
    API = AccessPlatform.API
class VisualContent:
    pagetype:str
    skip:bool
    value:any
