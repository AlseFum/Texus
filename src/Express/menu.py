from Express import extract_str, HTMLResponse, get_template

def registry():
    def render_menu(v):
        entry = extract_str(v) or ""
        html = get_template("menu")
        js_assignment = f'var __ENTRY__ = {entry!r};'
        return HTMLResponse(content=html.replace("/*!insert*/", js_assignment))
    return {
        "suffix": "menu",
        "lambda": render_menu
    }


