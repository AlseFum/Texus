from Express import extract_str, HTMLResponse, get_template

def registry():
    def render_note(v):
        # 优先使用 payload.text
        raw = None
        payload = getattr(v, "payload", None)
        if isinstance(payload, dict) and "text" in payload:
            try:
                raw = str(payload.get("text", ""))
            except Exception:
                raw = extract_str(v)
        else:
            raw = extract_str(v)
        # 注入到 text_edit 模板
        html = get_template("text_edit")
        js_content = raw.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
        return HTMLResponse(content=html.replace("/*!insert*/", f'var inlineContent="{js_content}";'))
    return {
        "suffix": ["note"],
        "lambda": render_note
    }


