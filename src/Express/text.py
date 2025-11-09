from Express import extract_str, HTMLResponse, get_template

def registry():
    """
    文本编辑器渲染器
    """
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
        
        # 转义 JavaScript 字符串
        to_js = lambda s: str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
        
        # 基础注入
        html = get_template("text_edit")
        js_inject = f'var inlineContent="{to_js(raw)}";'
        
        # 只有在 payload 中明确设置了通知栏信息时才注入
        #
        if  isinstance(payload, dict) and "infoMessage" in payload :
            info_message = payload.get("infoMessage", "")
            info_type = payload.get("infoType", "info")
            info_dismissible = "true" if payload.get("infoDismissible", True) else "false"
            info_duration = str(payload.get("infoDuration", 3000))
            
            js_inject += f'''
window.infoBarMessage="aef{to_js(info_message)}";
window.infoBarType="{info_type}";
window.infoBarDismissible={info_dismissible};
window.infoBarDuration={info_duration};
'''
        return HTMLResponse(content=html.replace("/*!insert*/", js_inject))
    
    # 同时注册 text 和 note 类型
    return {
        "suffix": ["text"],
        "lambda": render_text
    }


