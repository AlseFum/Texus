import json
from util import first_valid
from Database import pub_get, pub_set
from protocol.types import VisualContent
from datetime import datetime
class NoteEntry:
    lastSaveTime = ""
    text = ""
class Note:
    def access(pack):
        op = first_valid(pack.query.get("op", None),"get")
        v = VisualContent()
        if op == "get":
            
            # 判断是否是 API 请求
            is_api = getattr(pack, 'by', '') == 'api'
            
            # 从数据库获取数据
            raw_data = pub_get(pack.entry or pack.path)
            
            # 尝试解析为对象格式
            try:
                if raw_data and isinstance(raw_data, str):
                    note_obj = json.loads(raw_data)
                else:
                    note_obj = raw_data if raw_data else {"text": "", "lastSaveTime": ""}
            except:
                # 如果解析失败，说明是旧格式的纯文本，转换为新格式
                note_obj = {
                    "text": raw_data if raw_data else "",
                    "lastSaveTime": ""
                }
            
            if is_api:
                # API 请求直接返回 JSON 格式
                v.skip = True
                v.value = note_obj
            else:
                # 普通请求返回页面
                v.pagetype = "note"
                v.skip = False
                v.value = note_obj.get("text", "")
            return v
        
        elif op == "set":
            # 处理保存操作
            content = first_valid(pack.query.get('content', None), "")
            # 解码前端编码的内容
            try:
                import urllib.parse
                content = urllib.parse.unquote(content)
            except:
                pass  # 如果解码失败，使用原始内容
            
            # 构建对象格式
            note_obj = {
                "text": content,
                "lastSaveTime": datetime.now().isoformat()
            }
            
            # 存储为 JSON 字符串
            success = pub_set(pack.entry or pack.path, json.dumps(note_obj, ensure_ascii=False))
            
            print(f"Got set request, saved at {note_obj['lastSaveTime']}")
            
            v = VisualContent()
            v.pagetype = "note" 
            v.skip = True
            v.value = {
                "success": success,
                "message": "保存成功" if success else "保存失败",
                "data": note_obj
            }
            return v
        
        # 默认返回获取操作
        v = VisualContent()
        v.pagetype = "note"
        v.skip = False
        raw_data = pub_get(pack.entry or pack.path)
        try:
            if raw_data and isinstance(raw_data, str):
                note_obj = json.loads(raw_data)
                v.value = note_obj.get("text", "")
            else:
                v.value = raw_data if raw_data else ""
        except:
            v.value = raw_data if raw_data else ""
        return v