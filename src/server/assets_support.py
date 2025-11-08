"""
Assets 支持模块
"""
import os
import glob
from Common.util import FileResponse

# 全局变量存储扫描到的assets目录
ASSETS_DIRS = []

def scan_assets_directories():
    """扫描并初始化 assets 目录"""
    global ASSETS_DIRS
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Express"))
    
    # 扫描模式：寻找 */dist/assets 目录
    patterns = [
        os.path.join(base_dir, "*", "dist", "assets"),
        os.path.join(base_dir, "*", "*", "dist", "assets"),
    ]
    
    found_dirs = []
    for pattern in patterns:
        found_dirs.extend(glob.glob(pattern))
    
    # 去重并验证目录存在
    ASSETS_DIRS = [d for d in set(found_dirs) if os.path.isdir(d)]
    
    print(f"扫描到 {len(ASSETS_DIRS)} 个assets目录:")
    for assets_dir in ASSETS_DIRS:
        print(f"  - {assets_dir}")
    
    return ASSETS_DIRS

def serve(path):
    """服务 assets 文件"""
    global ASSETS_DIRS
    
    # 遍历所有可能的 assets 目录
    for assets_dir in ASSETS_DIRS:
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


