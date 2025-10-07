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
        1. 从 pub 表获取内容作为模板和时间戳
        2. 检查 gen 表缓存，比较时间戳
        3. 如果缓存有效，使用缓存的 Generator
        4. 否则重新解析并更新缓存
        5. 调用 gen() 生成最终内容并输出
        """
        # 1. 从 pub 表获取内容作为模板
        pub_data = pub_get(pack.entry)
        
        if pub_data is None:
            return FinalVis.of("raw", "(empty)")
        
        # 获取 pub 表的内容和时间戳
        if isinstance(pub_data, File):
            template_text = pub_data._value.get("text", "")
            pub_timestamp = pub_data._value.get("lastSavedTime")
        elif isinstance(pub_data, dict):
            template_text = pub_data.get("text", "")
            pub_timestamp = pub_data.get("lastSavedTime")
        else:
            template_text = str(pub_data)
            pub_timestamp = None
        
        # 2. 检查 gen 表缓存
        gen_table = Table.of("GEN")
        cache = gen_table.get(pack.entry)
        generator = None
        need_parse = True
        
        if cache is not None and isinstance(cache, dict):
            cached_timestamp = cache.get("sourceTimestamp")
            cached_template = cache.get("template", "")
            cached_generator = cache.get("generator")
            
            # 3. 比较时间戳和模板内容，判断缓存是否有效
            if (cached_timestamp == pub_timestamp and 
                cached_template == template_text and 
                cached_generator is not None):
                generator = cached_generator
                need_parse = False
        
        # 4. 如果需要，重新解析模板
        if need_parse:
            try:
                parser = Parser(template_text)
                generator = parser.parse()
                
                # 更新 gen 表缓存（保存 Generator 对象引用）
                gen_table.set(pack.entry, {
                    "template": template_text,
                    "sourceTimestamp": pub_timestamp,
                    "generator": generator,  # 直接保存对象引用
                    "parsedTime": datetime.now()
                })
                
            except ParseError as e:
                return FinalVis.of("raw", f"解析错误: {e}\n模板: {template_text}")
            except Exception as e:
                return FinalVis.of("raw", f"生成器错误: {e}\n模板: {template_text}")
        
        # 5. 生成内容并输出
        try:
            # 获取随机种子（如果提供）
            seed = pack.query.get('seed', None)
            if seed is not None:
                try:
                    seed = int(seed)
                except:
                    seed = None
            
            result = generator.gen(seed)
            return FinalVis.of("raw", str(result))
        except Exception as e:
            return FinalVis.of("raw", f"生成错误: {e}")

