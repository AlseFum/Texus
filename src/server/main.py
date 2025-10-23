from util import Request, FileResponse, HTMLResponse, JSONResponse, FastAPI, Query, Cookie, CORSMiddleware
from Database import getmime, init_backup_system, stop_backup_system
from Express import wrap
import Port
from .assets_support import scan_assets_directories, serve
from .translate import replaceByBody, request2access

app = FastAPI(title="Note Server", version="0.1.0")

# 启动事件
@app.on_event("startup")
async def startup_event():
    # 初始化备份系统
    init_backup_system(
        backup_dir="src/Database/.backup",  # 备份目录
        max_backups=10,                      # 保留10个备份
        backup_interval=60,                  # 每10秒备份一次
        format="toml"                        # 使用TOML格式
    )
    

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    # 停止备份系统
    stop_backup_system()
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
scan_assets_directories()
@app.get("/assets/{path:path}")
async def serve_assets(path: str):
    """服务 assets 文件"""
    return serve(path)
#------------
@app.get("/api/{path:path}")
async def api_get(path: str, request: Request):
    pack = request2access(request, path=path, by="api")
    return await visit(pack)

@app.post("/api/{path:path}")
async def api_post(path: str, request: Request):
    pack = request2access(request, path=path, by="api")
    return await visit(await replaceByBody(pack, request))
#------------   
@app.get("/{path:path}")  # 使用 `{path:path}` 捕获任意路径
async def visit_get(request: Request):
    return await visit( request2access(request))

# POST 路由处理
@app.post("/{path:path}")
async def visit_post(request: Request):
    return await visit(await replaceByBody(request2access(request), request))
#------------
async def visit(pack):
    if pack.entry == "mock":
        return pack
    return visit_internal(pack)
from util import first_avail
def visit_internal(pack):
    mime = first_avail(pack.mime, getmime(pack.entry), "text")
    Dispatcher = Port.dispatch(mime)
    
    # 如果Dispatcher是Text且mime不为空（说明有后缀），尝试Meta脚本处理
    if Dispatcher == Port.Text and pack.mime and pack.mime != "text":
        # 直接查找mime对应的entry
        from Database import pub_get
        meta_script = pub_get(pack.mime)
        if meta_script:  # 如果找到了对应的entry
            # 使用Meta.accessScript处理
            output = Port.Meta.accessScript(pack)
            return output.value if output.skip else wrap(output)
        else:
            # 如果后缀不为空但没有找到对应的entry，返回错误
            from protocol.types import FinalVis
            error_msg = f"Not Available!"
            return FinalVis.of("raw", error_msg).value
    
    output = Dispatcher.access(pack)
    return output.value if output.skip else wrap(output)
