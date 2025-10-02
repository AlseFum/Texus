import os
from protocol.types import VisualContent
from fastapi.responses import HTMLResponse, JSONResponse
mimes={

}
def wrap(v: VisualContent):
    if v.pagetype in mimes:
        return mimes[v.pagetype](v)
    return useRaw(v)
def useRaw(v):
    content = extract_str(v)
    js_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    
    return HTMLResponse(content=RAW_HTML_TEMPLATE.replace("/*!insert*/", f'text = "{js_content}";'))
def useNote(v):
    html = get_template("note")
    print("use note")
    content = extract_str(v)
    js_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    js_assignment = f'var inlineContent="{js_content}";'    
    return HTMLResponse(content=html.replace("/*!insert*/", js_assignment))
mimes["note"]=useNote
mimes["raw"]=useRaw


def extract_str(v):
  if v is not None and v.value is not None:
      if hasattr(v.value, 'to_dict') and callable(getattr(v.value, 'to_dict')):
          # 优先使用 to_dict() 方法
          return str(v.value.to_dict())
      elif hasattr(v.value, '__dict__') and not isinstance(v.value.__dict__, dict):
          # 如果 __dict__ 被重写为非字典，使用 vars()
          return str(vars(v.value))
      elif hasattr(v.value, '__dict__'):
          # 自定义类对象，使用实际的 __dict__ 属性
          return str(v.value.__dict__)
      elif isinstance(v.value, dict):
          # 已经是字典，直接转字符串
          return str(v.value)
      else:
          # 其他类型，转字符串
          return str(v.value)
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