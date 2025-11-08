from Express import extract_str, HTMLResponse, get_template

def registry():
    def render_text(v):
        payload = getattr(v, "payload", None)
        raw = None
        if isinstance(payload, dict) and "text" in payload:
            try:
                raw = str(payload.get("text", ""))
            except Exception:
                raw = extract_str(v)
        else:
            raw = extract_str(v)
        html = get_template("text_edit")
        js_content = raw.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
        return HTMLResponse(content=html.replace("/*!insert*/", f'var inlineContent="{js_content}";'))
    return {
        "suffix": ["text"],
        "lambda": render_text
    }


