#collect dependencies that VSCode extensions can't detect and will alarm
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi import Request, FastAPI, Query, Cookie
from fastapi.middleware.cors import CORSMiddleware
def first_valid(*args):
    for arg in args:
        if arg is not None:
            return arg
    return None
def first_avail(*args):
    for arg in args:
        if arg is not None and arg is not "":
            return arg
    return None