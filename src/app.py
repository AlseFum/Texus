from Common.util import Request, FileResponse, HTMLResponse, JSONResponse, FastAPI, Query, Cookie, CORSMiddleware
from Common.logger import setup_logging, get_logger
from Database import getmime, init_backup_system, stop_backup_system
from Express import wrap
import Port
from server.assets_support import scan_assets_directories, serve
from server.translate import replaceByBody, request2access

# 初始化日志系统（在创建 FastAPI app 之前）
setup_logging()
logger = get_logger("app")

app = FastAPI(title="Note Server", version="0.1.0")

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("应用启动中...")
    
    # 初始化备份系统
    logger.info("初始化备份系统...")
    init_backup_system(
        backup_dir=".backup",
        max_backups=15,
        backup_interval=10,
        format="line"
    )
    
    # 初始化定时任务管理器（模块级单例）
    logger.info("启动定时任务管理器...")
    from Port.Timer import timer_manager
    timer_manager.start()
    
    logger.info("应用启动完成")
    logger.info("=" * 60)

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=" * 60)
    logger.info("应用关闭中...")
    
    # 停止定时任务管理器（模块级单例）
    logger.info("停止定时任务管理器...")
    from Port.Timer import timer_manager
    timer_manager.stop()
    
    logger.info("停止备份系统...")
    stop_backup_system()
    
    logger.info("应用已关闭")
    logger.info("=" * 60)
    
   
# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # 允许的前端源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)
#------------
scan_assets_directories()
@app.get("/assets/{path:path}")
async def serve_assets(path: str):
    """提供 assets 文件"""
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
from Common.util import first_avail
def visit_internal(pack):
    which = first_avail(getattr(pack, "suffix", None), getmime(pack.entry), "text")
    Dispatcher = Port.dispatch(which)
    
    logger.debug(f"访问: entry={pack.entry}, mime={which}, dispatcher={Dispatcher.__name__}")
    
    # 如果Dispatcher是Default（dispatch匹配失败）且mime不为空（说明有后缀），尝试Meta脚本处理
    if Dispatcher == Port.Default and getattr(pack, "suffix", None):
        # 直接查找mime对应的entry
        from Database import Table
        main_table = Table.of("main")
        if main_table.get(pack.suffix):  # 如果找到了对应的entry
            logger.debug(f"使用 Meta Port 处理后缀: {pack.suffix}")
            # 使用Meta Port 处理
            MetaPort = Port.dispatch("meta")
            # Meta Port 使用 accessScript 处理带后缀的请求
            from Port.Meta import Meta
            output = Meta.accessScript(pack)
            return output.value if output.skip else wrap(output)
        #no else, else just uses Text to do every rest things.
    
    try:
        output = Dispatcher.access(pack)
        return output.value if output.skip else wrap(output)
    except Exception as e:
        logger.error(f"处理请求失败: entry={pack.entry}, error={str(e)}", exc_info=True)
        raise


