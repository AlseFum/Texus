from .Meta import Meta
from .Note import Note
from .GenNote import GenNote
from protocol.types import VisualContent
from Database import pub_get

class Raw:
    def access(pack):
        return VisualContent.of("raw",pub_get(pack.entry) if pub_get(pack.entry) else "(empty)")


def dispatch(which):
    if which == "meta":
        return Meta
    elif which in ["gen"]:
        return GenNote
    elif which in ["raw"]:
        return Raw
    return Note
