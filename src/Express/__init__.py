import os
import importlib
from typing import Callable, Dict, Optional, Any
from Common.base import Renderee, entry
from Common.util import HTMLResponse

def useRaw(v: Renderee):
    """
    兜底渲染：以 raw 模板渲染纯文本。
    若 raw 插件存在，会覆盖该渲染器。
    """
    payload = getattr(v, "payload", None)
    # 内容与标题（无需异常分支）
    if isinstance(payload, dict):
        content = str(payload.get("text", "")) if "text" in payload else extract_str(v)
        title_raw = str(payload.get("title", "") or "")
    else:
        content = extract_str(v)
        title_raw = str(getattr(v, "title", "") or (v.value.get("title", "") if hasattr(v, "value") and isinstance(v.value, dict) else ""))
    # 转义注入
    to_js = lambda s: s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    html = get_template("raw")
    return HTMLResponse(content=html.replace("/*!insert*/", f'var text = "{to_js(content)}"; var title = "{to_js(title_raw)}";'))

# note/text 将改由插件提供（见 note.py / text.py），此处不再内置实现

def extract_str(v):
    # 优先使用 to_raw 方法，其次 value 属性
    if v is not None:
        if hasattr(v, "to_raw") and callable(getattr(v, "to_raw")):
            return str(v.to_raw())
        if hasattr(v, "value"):
            return str(v.value)
    return ""
def get_template(where: str) -> str:
    """
    读取指定模板目录下的 dist/index.html。
    若不存在则回退到极简占位模板（仅保底，不建议依赖）。
    """
    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, where, "dist", "index.html")
    # 基于 mtime 的简易缓存
    global TEMPLATE_CACHE
    if 'TEMPLATE_CACHE' not in globals():
        TEMPLATE_CACHE = {}
    # 极简占位模板：避免返回空串导致注入失败
    minimal_fallback = (
        '<!doctype html><html><head><meta charset="utf-8"><title>-</title></head>'
        '<body><pre id="content"></pre><script>/*!insert*/'
        'document.getElementById("content").textContent=(typeof text!=="undefined"?text:"");'
        "</script></body></html>"
    )
    if os.path.exists(template_path):
        mtime = os.path.getmtime(template_path)
        cached = TEMPLATE_CACHE.get(where)
        if cached and cached.get("mtime") == mtime:
            return cached.get("html", minimal_fallback)
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()
        TEMPLATE_CACHE[where] = {"path": template_path, "mtime": mtime, "html": html}
        return html
    else:
        return minimal_fallback

#

# 视图渲染器注册表（以 viewtype 为键）
renderers: Dict[str, Callable[[Renderee], HTMLResponse]] = {}
# 仅保留 raw 的默认渲染，其它 viewtype 由插件或外部注册
renderers["raw"] = useRaw

class RendererRegistry:
    def __init__(self, initial: Optional[Dict[str, Callable[[Renderee], HTMLResponse]]] = None):
        self._renderers = renderers if initial is None else initial
    def register_viewtype(self, viewtype: str, renderer: Callable[[Renderee], HTMLResponse]):
        if not viewtype or not callable(renderer):
            raise ValueError("Invalid viewtype or renderer")
        self._renderers[viewtype] = renderer
    def get_renderer(self, viewtype: str) -> Callable[[Renderee], HTMLResponse]:
        return self._renderers.get(viewtype, useRaw)

registry = RendererRegistry()

def register_renderer(viewtype: str, renderer: Callable[[Renderee], HTMLResponse]):
    registry.register_viewtype(viewtype, renderer)

def wrap(v):
    """包装对象为 HTML 响应
    
    Args:
        v: 可以是 Renderee 或 entry 对象
           - 如果是 entry，会自动转换为 Renderee
           - 如果是 Renderee，直接使用
    
    Returns:
        HTMLResponse: 渲染后的 HTML 响应
    """
    # 自动转换 entry 为 Renderee
    if isinstance(v, entry):
        v = v.to_renderee()
    
    # 获取渲染器类型键
    key = getattr(v, "viewtype", "") or getattr(v, "suffix", "") or ""
    renderer = registry.get_renderer(key)
    return renderer(v)

def _load_plugins_from_express_root():
    base_dir = os.path.dirname(__file__)
    package_name = __name__
    for fname in os.listdir(base_dir):
        if not fname.endswith(".py"):
            continue
        if fname == "__init__.py":
            continue
        module_name = f"{package_name}.{fname[:-3]}"
        mod = importlib.import_module(module_name)
        if hasattr(mod, "registry") and callable(getattr(mod, "registry")):
            info = mod.registry()
            _register_plugin_dict(info)

def _register_plugin_dict(info: Dict[str, Any]):
    """
    按约定从插件信息中注册渲染器：
    - 必须提供 suffix（字符串或字符串数组）
    - 必须提供可调用的 lambda/handler/render 之一
    """
    if not isinstance(info, dict):
        return
    targets = info.get("suffix")
    func = info.get("lambda") or info.get("handler") or info.get("render")
    if not func or not callable(func) or targets is None:
        return
    def renderer(v: Renderee):
        return func(v)
    if isinstance(targets, (list, tuple)):
        for t in targets:
            if isinstance(t, str) and t:
                register_renderer(t, renderer)
    elif isinstance(targets, str) and targets:
        register_renderer(targets, renderer)


def load_plugins():
    _load_plugins_from_express_root()
    env = os.environ.get("EXPRESS_PLUGINS", "").strip()
    if env:
        for mod_name in [x.strip() for x in env.split(",") if x.strip()]:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "registry") and callable(getattr(mod, "registry")):
                info = mod.registry()
                _register_plugin_dict(info)

# 模块导入时自动加载插件
load_plugins()