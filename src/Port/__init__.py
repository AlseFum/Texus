from .Meta import Meta
from .Note import Note
def dispatch(which):
    if(which == "meta"):
        return Meta
    return Note