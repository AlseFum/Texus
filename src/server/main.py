from fastapi import FastAPI,Query,Cookie,Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from Database import getmime
from Express import wrap
import Port
from .assets_support import scan_assets_directories, serve
from .funcs import replaceByBody, request2access

app = FastAPI(title="Note Server", version="0.1.0")

# 启动时扫描assets目录
scan_assets_directories()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # 允许的前端源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)
#------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}
#------------
@app.get("/api/{path:path}")
async def api_get(path: str, request: Request):
    pack = request2access(request, path=f"/api/{path}", by="api")
    return await visit(pack)

@app.post("/api/{path:path}")
async def api_post(path: str, request: Request):
    pack = request2access(request, path=f"/api/{path}", by="api")
    return await visit(await replaceByBody(pack, request))
#------------
@app.get("/assets/{path:path}")
async def serve_assets(path: str):
    """服务 assets 文件"""
    return serve(path)
#------------   
@app.get("/{path:path}")  # 使用 `{path:path}` 捕获任意路径
async def visit_get(request: Request):
    return await visit( request2access(request))

# POST 路由处理
@app.post("/{path:path}")
async def visit_post(request: Request):
    return await visit(await replaceByBody(await request2access(request), request))
#------------

async def visit(pack):
    return visit_internal(pack)
from util import first_avail
def visit_internal(pack):
    if pack.entry == "mock":
        return pack
    
    mime = first_avail(pack.mime, getmime(pack.entry), "text")
    # 根据 MIME 类型选择合适的 Port
    Dispatcher = Port.dispatch(mime)
    visualContent = Dispatcher.access(pack)
    return visualContent.content() if visualContent.skip() else wrap(visualContent)
