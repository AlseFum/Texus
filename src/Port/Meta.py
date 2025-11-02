from Common.types import FinalVis, entry
from Common import execute_script
from Database import pub_get
from .Text import Text

class Meta(Text):
    @staticmethod
    def accessScript(pack) -> FinalVis:
        #truly the mime。
        script_falsemeta = pub_get(pack.mime)
        
        # 获取脚本内容
        metaHandler = ""
        if isinstance(script_falsemeta, entry):
            metaHandler = script_falsemeta.value.get("text", "")
        else:
            metaHandler = str(script_falsemeta or "")
        
        # 获取源数据（pack.entry就是源数据）
        source_data = pub_get(pack.entry)
        input_data = ""
        if isinstance(source_data, entry):
            input_data = source_data.value.get("text", "")
        else:
            input_data = str(source_data or "")
        
        # 使用原始脚本内容，添加输入数据作为变量
        enhanced_script = f"""
# 输入数据
input_data = '''{input_data}'''

# 用户脚本
{metaHandler}
"""
        
        # 使用 Common.execute_script 执行脚本
        # 添加额外的全局变量：request 和 source
        extra_globals = {
            'request': pack,
            'source': source_data,
        }
        
        success, output, operations = execute_script(enhanced_script, extra_globals)
        
        if success:
            # 只提取print输出的结果
            if output:
                return FinalVis.of("text", output)
            else:
                # 显示更详细的执行信息
                debug_info = f"""Script executed successfully but produced no output.

Script content:
{metaHandler}

Available variables after execution:
- input_data: {repr(input_data[:100] + '...' if len(input_data) > 100 else input_data)}
- request: {repr(pack)}

Try adding a print statement to your script."""
                return FinalVis.of("text", debug_info)
        else:
            return FinalVis.of("text", f"Script execution error: {output}")