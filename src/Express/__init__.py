import os
from protocol.types import FinalVis,Renderee
from util import HTMLResponse

def useRaw(v):
    content = extract_str(v)
    js_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    
    return HTMLResponse(content=RAW_HTML_TEMPLATE.replace("/*!insert*/", f'text = "{js_content}";'))
def useNote(v):
    html = get_template("text_edit")
    js_content = extract_str(v).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    js_assignment = f'var inlineContent="{js_content}";'    
    return HTMLResponse(content=html.replace("/*!insert*/", js_assignment))

def extract_str(v):
    # 优先使用 to_raw 方法，其次 content 方法
    if v is not None:
        if hasattr(v, "to_raw") and callable(getattr(v, "to_raw")):
            return str(v.to_raw())
        if hasattr(v, "content") and callable(getattr(v, "content")):
            return str(v.content())
    return ""
def get_template(where:str):
  html=""
  template_path = os.path.join(os.path.dirname(__file__), where+"/dist/index.html")
  try:
      with open(template_path, "r", encoding="utf-8") as f:
          html = f.read()
  except FileNotFoundError:
      html = RAW_HTML_TEMPLATE
  return html

RAW_HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>-</title>
  <style>
    html, body { height: 100%; }
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; color: #111; background: #fafafa; }
    .container { max-width: 720px; margin: 0 auto; padding: 24px; }
    .card { background: #fff; border: 1px solid #eaeaea; border-radius: 12px; padding: 20px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .title { margin: 0 0 12px; font-size: 18px; font-weight: 600; color: #222; }
    .text { white-space: pre-wrap; word-break: break-word; color: #333; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1 class="title"></h1>
      <div id="content" class="text"></div>
    </div>
  </div>
  <script>
    const area=document.getElementById("content");
    let text = "Oops, nothing here";
    /*!insert*/
    area.innerHTML=text;
  </script>
</body>
</html>"""

mimes={

}
mimes["note"]=useNote
mimes["text"]=useNote
mimes["raw"]=useRaw
def wrap(v: Renderee):
    if v.mime() in mimes:
        return mimes[v.mime()](v)
    return useRaw(v)