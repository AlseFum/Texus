from protocol.types import FinalVis, File
from Database import Table, pub_get, pub_set
from util import first_valid
from datetime import datetime

from .generator import Generator
from .parser import Parser, ParseError
from .file import GenFile

# 导出公共接口
__all__ = ['Gen', 'Generator', 'Parser', 'ParseError', 'GenFile']


class Gen:
    """生成器 Port - 从 pub 表读取内容并生成随机文本
    
    使用 gen 表缓存解析后的 Generator 对象，根据时间戳判断是否需要重新解析
    """
    
    @staticmethod
    def access(pack):
        """主访问方法
        
        工作流程：
        1. 从 pub 表获取内容
        2. 检查 gen 表缓存，比较时间戳
        3. 如果缓存有效，使用缓存的 GenFile
        4. 否则重新解析并更新缓存
        5. 调用 GenFile.gen() 生成最终内容并输出
        """
        # 1. 从 pub 表获取内容
        pub_data = pub_get(pack.entry)
        
        if pub_data is None:
            return FinalVis.of("raw", "(empty)")
        
        # 统一转换为 File 格式
        if isinstance(pub_data, File):
            pub_file = pub_data
        elif isinstance(pub_data, dict):
            pub_file = File(mime="text", value=pub_data)
        else:
            pub_file = File(mime="text", value={"text": str(pub_data)})
        
        pub_timestamp = pub_file._value.get("lastSavedTime")
        
        # 2. 检查 gen 表缓存
        gen_table = Table.of("GEN")
        cached_genfile = gen_table.get(pack.entry)
        genfile = None
        need_parse = True
        
        # 3. 判断缓存是否有效
        if isinstance(cached_genfile, GenFile):
            cached_timestamp = cached_genfile._value.get("sourceTimestamp")
            if cached_timestamp == pub_timestamp and cached_genfile.root is not None:
                genfile = cached_genfile
                need_parse = False
        
        # 4. 如果需要，重新解析
        if need_parse:
            try:
                genfile = Parser(pub_file).parse()
                # 更新 gen 表缓存
                gen_table.set(pack.entry, genfile)
            except Exception as e:
                return FinalVis.of("raw", f"Error: {e}")
        
        # 5. 生成内容并输出
        result = genfile.gen()
        return FinalVis.of("raw", str(result))

