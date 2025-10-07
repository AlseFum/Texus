from .Meta import Meta
from .Text import Text
from protocol.types import FinalVis
from Database import pub_get
class Port:
    def access(pack):
        return FinalVis.of("raw",pub_get(pack.entry) if pub_get(pack.entry) is not None else "(empty)")
class Raw(Port):
    pass
from .Gen import Gen

def dispatch(which):
    if which == "meta":
        return Meta
    elif which in ["raw"]:
        return Raw
    elif which in ["gen"]:
        return Gen
    return Text
