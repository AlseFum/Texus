from protocol.types import FinalVis, entry
from util import first_valid
from Database import pub_get, pub_set
from datetime import datetime

class Meta:
    @staticmethod
    def get_data(entry_key) -> entry:
        """从数据库获取文本数据，返回entry对象"""
        pub_data = pub_get(entry_key)
        if pub_data is None:
            return entry(mime="text", value={"text": "No data", "lastSavedTime": None})
        
        # 统一转换为entry格式
        if isinstance(pub_data, entry):
            return pub_data
        elif isinstance(pub_data, dict):
            normalized_data = {
                "text": pub_data.get("text", ""),
                "lastSavedTime": pub_data.get("lastSavedTime", datetime.now())
            }
            result_entry = entry(mime="text", value=normalized_data)
            pub_set(entry_key, result_entry)  # 直接保存entry对象
            return result_entry
        else:
            # 原始字符串数据
            normalized_data = {
                "text": str(pub_data),
                "lastSavedTime": datetime.now()
            }
            result_entry = entry(mime="text", value=normalized_data)
            pub_set(entry_key, result_entry)  # 直接保存entry对象
            return result_entry
        
    @staticmethod
    def getByWeb(pack) -> FinalVis:
        """通过Web方式获取文本"""
        text_file = Meta.get_data(pack.entry or pack.path)
        return FinalVis.of("text", text_file.value.get("text", ""))
    
    @staticmethod
    def getByApi(pack) -> FinalVis:
        """通过API方式获取文本"""
        text_file = Meta.get_data(pack.entry or pack.path)
        # 安全地转换datetime对象为ISO字符串
        last_saved = text_file.value.get("lastSavedTime")
        last_saved_iso = last_saved.isoformat() if last_saved and hasattr(last_saved, 'isoformat') else ""
        
        response_value = {
            "text": text_file.value.get("text", ""),
            "lastSavedTime": last_saved_iso
        }
        return FinalVis.of("text", response_value, skip=True)
    
    @staticmethod
    def set(pack) -> FinalVis:
        """设置文本内容"""
        content = first_valid(pack.query.get('content', None), "")
        
        # 解码URL编码的内容
        try:
            import urllib.parse
            content = urllib.parse.unquote(content)
        except:
            pass
        
        # 创建entry对象
        saved_time = datetime.now()
        file_data = {
            "text": content,
            "lastSavedTime": saved_time
        }
        text_file = entry(mime="text", value=file_data)
        
        # 直接保存entry对象
        pub_set(pack.entry, text_file)
        
        response_data = {
            "success": True,
            "message": "保存成功",
            "data": {
                "text": content,
                "lastSavedTime": saved_time.isoformat()
            }
        }
        
        return FinalVis.of("text", response_data, skip=True)
    
    @staticmethod
    def access(pack) -> FinalVis:
        """主访问方法，根据操作类型分发到相应的方法"""
        op = first_valid(pack.query.get("op", None), "get")
        
        if op == "set":
            return Meta.set(pack)
        else:
            # 判断是否是 API 请求
            is_api = getattr(pack, 'by', '') == 'api'
            return Meta.getByApi(pack) if is_api else Meta.getByWeb(pack)
    @staticmethod
    def accessScript(pack) -> FinalVis:
        script_data = pub_get(pack.mime)
        
        # 获取脚本内容
        script_content = ""
        if isinstance(script_data, dict):
            script_content = script_data.get("text", "")
        elif hasattr(script_data, 'value') and isinstance(script_data.value, dict):
            script_content = script_data.value.get("text", "")
        else:
            script_content = str(script_data or "")
        
        
        # 获取源数据（pack.entry就是源数据）
        source_data = pub_get(pack.entry)
        input_data = ""
        if isinstance(source_data, dict):
            input_data = source_data.get("text", "")
        elif hasattr(source_data, 'value') and isinstance(source_data.value, dict):
            input_data = source_data.value.get("text", "")
        else:
            input_data = str(source_data or "")
        
        # 直接使用原始脚本内容，添加输入数据作为变量
        enhanced_script = f"""
# 输入数据
input_data = '''{input_data}'''

# 用户脚本
{script_content}
"""
        
        # 直接执行脚本并处理返回值
        try:
            # 创建安全的执行环境
            from .Exec import DatabaseAPI
            import re
            db_api = DatabaseAPI()
            safe_globals = {
                '__builtins__': {
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'print': print,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'sorted': sorted,
                    'reversed': reversed,
                    'any': any,
                    'all': all,
                },
                'db': db_api,  # 提供数据库API
                're': re,      # 正则表达式
                'request': pack,  # 传入的pack对象
                'result': None,   # 用于提取结果的变量
                'source': source_data,  # 源数据对象
            }
            
            # 捕获输出
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                # 执行用户脚本
                exec(enhanced_script, safe_globals, {})
                output = captured_output.getvalue()
                
                # 只提取print输出的结果
                if output:
                    return FinalVis.of("text", output)
                else:
                    # 显示更详细的执行信息
                    debug_info = f"""Script executed successfully but produced no output.

Script content:
{script_content}

Available variables after execution:
- input_data: {repr(input_data[:100] + '...' if len(input_data) > 100 else input_data)}
- request: {repr(pack)}

Try adding a print statement to your script."""
                    return FinalVis.of("text", debug_info)
                
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            return FinalVis.of("text", f"Script execution error: {str(e)}")