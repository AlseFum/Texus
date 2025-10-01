from fastapi import FastAPI,Query,Cookie,Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from Database import getmime
from Express import wrap
import Port
from protocol.types import Access
from .determine import determine_access_type

app = FastAPI(title="Note Server", version="0.1.0")

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
    pack = await request2pack(request)
    # 修正 entry 和 path
    pack.entry = path.split("/")[0] if path else ""
    pack.path = path
    pack.by = "api"  # 强制 platform 为 api
    return await visit(pack)

@app.post("/api/{path:path}")
async def api_post(path: str, request: Request):
    body = await request.json()
    return await visit(process_query(api_get(path, request), body))
#------------
@app.get("/assets/{path:path}")
async def serve_assets(path: str):
    # 定义多个 assets 目录
    base_dir = os.path.join(os.path.dirname(__file__), "..", "Express")
    assets_dirs = [
        os.path.join(base_dir, "note", "dist", "assets"),
        os.path.join(base_dir, "console", "dist", "assets"), 
        os.path.join(base_dir, "blog", "dist", "assets"),
        os.path.join(base_dir, "img", "dist", "assets"),
        # 可以继续添加更多目录
    ]
    
    # 遍历所有可能的 assets 目录
    for assets_dir in assets_dirs:
        file_path = os.path.join(assets_dir, path)
        
        if os.path.exists(file_path) and os.path.commonpath([assets_dir, file_path]) == assets_dir:
            # 确定 MIME 类型
            media_type = None
            if path.endswith('.js'):
                media_type = 'application/javascript'
            elif path.endswith('.css'):
                media_type = 'text/css'
            elif path.endswith('.json'):
                media_type = 'application/json'
            elif path.endswith('.woff') or path.endswith('.woff2'):
                media_type = 'font/woff2' if path.endswith('.woff2') else 'font/woff'
            elif path.endswith('.png'):
                media_type = 'image/png'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                media_type = 'image/jpeg'
            elif path.endswith('.svg'):
                media_type = 'image/svg+xml'
            
            return FileResponse(file_path, media_type=media_type)
    
    return {"error": "Asset not found"}
#------------   
@app.get("/{path:path}")  # 使用 `{path:path}` 捕获任意路径
async def visit_get(request: Request):
    return await visit(await request2pack(request))

# POST 路由处理
@app.post("/{path:path}")
async def visit_post(request: Request):
    try:
        body = await request.json()
    except:
        body = {}
    
    return await visit(process_query(await request2pack(request),body))

async def request2pack(request: Request):
    """将请求转换为字典格式的 pack"""
    # 解析路径信息
    path = request.url.path
    primary = path.split("/")[1] if path != "/" else ""
    primary_entry, primary_mime = (primary.rsplit(".", 1) + [""])[:2]
    
    # 通过 User-Agent 判断请求类型
    access_by = determine_access_type(request)
    
    # 优先使用 query 参数中的 role，然后是 fromScript（向后兼容）
    role_param = request.query_params.get("role", "").lower()
    if role_param in ["user", "script", "agent"]:
        who = role_param
    elif request.query_params.get("fromScript"):
        who = "script" if request.query_params.get("fromScript") == "script" else "agent"
    else:
        who = "user"
    pack = Access(
        who=who,
        by=access_by.value if hasattr(access_by, 'value') else str(access_by),
        path=path,
        query=dict(request.query_params),
        cookies=dict(request.cookies),
        mime=primary_mime,
        entry=primary_entry,
        body={}
    )
    return pack
def process_query(pack, body):
    """只对查询参数进行特殊值插值处理"""
    if not body:
        return pack
    for q_key, q_value in list(pack.query.items()):
        if isinstance(q_value, str) and q_value.startswith("$"):
            body_key = q_value[1:]
            if body_key in body:
                pack.query[q_key] = str(body[body_key])
    for q_key, q_value in list(pack.cookie.items()):
        if isinstance(q_value, str) and q_value.startswith("$"):
            body_key = q_value[1:]
            if body_key in body:
                pack.cookies[q_key] = str(body[body_key])
    
    return pack

async def visit(pack):
    return visit_internal(pack)
from util import first_valid
def visit_internal(pack):
    if pack.entry == "mock":
        return pack
    
    # 确定最终使用的 MIME 类型
    # 优先级：数据库中注册的 MIME > pack.mime > 默认 "text"
    mime = first_valid(getmime(pack.entry),pack.mime,"text")

    
    # 根据 MIME 类型选择合适的 Port
    Dispatcher = Port.dispatch(mime)
    visualContent = Dispatcher.access(pack)
    return visualContent.value if visualContent.skip else wrap(visualContent)
