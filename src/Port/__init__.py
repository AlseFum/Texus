from .Meta import Meta
from .Text import Text
from .Exec import Exec
from Common.types import FinalVis
from Database import pub_get
class Port:
    def access(pack):
        return FinalVis.of("raw",pub_get(pack.entry) if pub_get(pack.entry) is not None else "(empty)")
class Raw(Port):
    pass
from .Gen import Gen
from .Timer import Timer

class Default(Text):
    """默认 Port，继承自 Text，用于表示 dispatch 匹配失败的情况
    这个类主要用于给 Meta 使用，当 mime 类型匹配失败时返回此 Port
    """
    pass

def dispatch(which):
    if which == "meta":
        return Meta
    elif which in ["raw"]:
        return Raw
    elif which in ["py"]:
        return Exec
    elif which in ["gen"]:
        return Gen
    elif which in ["timer"]:
        return Timer
    elif which == "text":
        return Text
    return Default
