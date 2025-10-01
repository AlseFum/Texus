import os
from protocol.types import VisualContent
from fastapi.responses import HTMLResponse, JSONResponse
mimes={

}
def wrap(v: VisualContent):
    if v.pagetype in mimes:
        return mimes[v.pagetype](v)
    template_path = os.path.join(os.path.dirname(__file__), "raw.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        html = "/*!insert*/"
    
    # 安全地获取值，确保是字符串
    content = ""
    if v is not None and v.value is not None:
        content = str(v.value)
    
    # 支持多种插值方式
    # 对于 JavaScript 插值，需要正确转义内容
    js_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    js_assignment = f'text = "{js_content}";'
    
    rendered = html.replace("/*!insert*/", js_assignment).replace("{{ text }}", content)  # 向后兼容
    
    return HTMLResponse(content=rendered)
def useNote(v):
    template_path = os.path.join(os.path.dirname(__file__), "note/dist/index.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        html = "/*!insert*/"
    
    # 安全地获取值，确保是字符串
    content = ""
    if v is not None and v.value is not None:
        content = str(v.value)
    
    # 支持多种插值方式
    # 对于 JavaScript 插值，需要正确转义内容
    js_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    js_assignment = f'var inlineContent="{js_content}";'
    
    rendered = html.replace("/*!insert*/", js_assignment).replace("{{ text }}", content)  # 向后兼容
    
    return HTMLResponse(content=rendered)
mimes["note"]=useNote