from .generator import Generator, Context
from .file import GenFile
from protocol.types import File
from datetime import datetime
import re

class ParseError(Exception):
    """解析错误异常"""
    pass

class Parser:
    """
    基于缩进的生成器解析器
    
    支持的语法：
    - 缩进层级结构
    - 变量声明：$var : num, $var = value
    - 表达式：#[expr]
    - 副作用：#{effect}
    - 行内随机：#(a|b|c)
    - 权重：:n:option 或 #[expr]:option
    - Item引用：$item 或 $"item"
    - 注释：// 和 /* */
    """
    
    def __init__(self, source_file):
        """初始化解析器
        
        Args:
            source_file: File 对象，包含模板文本和元数据
        """
        self.source_file = source_file
        self.text = source_file._value.get("text", "")
        self.lines = self.text.split('\n')
        self.current_line = 0
        self.items = {}  # 存储 item 定义
        self.variables = {}  # 存储变量声明
    
    def parse(self):
        """解析入口，返回 GenFile 对象"""
        if not self.text:
            root = Generator("PlainList", [])
        else:
            # 解析所有内容
            self._parse_document()
            
            # 如果有定义的第一个 item，使用它作为根
            if self.items:
                first_item_name = list(self.items.keys())[0]
                root_gen = self.items[first_item_name]
                
                # 创建一个包装器，先初始化变量，再生成
                root = self._create_root_with_vars(root_gen)
            else:
                root = Generator("PlainList", [])
        
        # 创建 Context 并传入 items
        # 注意：实际的 Context 会在 gen() 时创建
        
        # 创建 GenFile
        value = {
            "template": self.text,
            "sourceTimestamp": self.source_file._value.get("lastSavedTime"),
            "parsedTime": datetime.now()
        }
        
        genfile = GenFile(value=value, root=root)
        # 存储 items 以便生成时使用
        genfile.items = self.items
        genfile.variables = self.variables
        
        return genfile
    
    def _create_root_with_vars(self, root_gen):
        """创建包含变量初始化的根生成器"""
        # 创建一个特殊的生成器，重写 gen 方法来初始化 context
        class RootGenerator(Generator):
            def __init__(self, root, items, variables):
                super().__init__("PlainList", [root])
                self.root = root
                self.stored_items = items
                self.stored_variables = variables
            
            def gen(self, context=None):
                # 创建新的 context
                ctx = Context(items=self.stored_items)
                
                # 初始化变量
                for var_name, var_info in self.stored_variables.items():
                    if 'value' in var_info:
                        value = var_info['value']
                        if isinstance(value, Generator):
                            # 如果是生成器，先生成值
                            ctx.set_variable(var_name, value)
                        else:
                            ctx.set_variable(var_name, value)
                    else:
                        # 使用默认值
                        var_type = var_info.get('type', 'str')
                        if var_type == 'num':
                            ctx.set_variable(var_name, 0)
                        else:
                            ctx.set_variable(var_name, "")
                
                # 生成根内容
                return self.root.gen(ctx)
        
        return RootGenerator(root_gen, self.items, self.variables)
    
    def _parse_document(self):
        """解析整个文档"""
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            stripped = line.strip()
            
            # 跳过空行
            if not stripped:
                self.current_line += 1
                continue
            
            # 跳过注释
            if stripped.startswith('//'):
                self.current_line += 1
                continue
            
            # 变量声明
            if stripped.startswith('$'):
                self._parse_variable_declaration(stripped)
                self.current_line += 1
                continue
            
            # Item 定义（非缩进的行）
            indent = self._get_indent(line)
            if indent == 0 and not stripped.startswith('$'):
                self._parse_item_definition(stripped)
            else:
                self.current_line += 1
    
    def _parse_variable_declaration(self, line):
        """解析变量声明"""
        # $var : num
        if ':' in line and '=' not in line:
            parts = line.split(':', 1)
            var_name = parts[0].strip()[1:]  # 移除 $
            var_type = parts[1].strip()
            self.variables[var_name] = {'type': var_type}
        
        # $var = value
        elif '=' in line:
            parts = line.split('=', 1)
            var_name = parts[0].strip()[1:]  # 移除 $
            value_str = parts[1].strip()
            
            # 解析值
            if value_str.startswith('"') and value_str.endswith('"'):
                # 字符串字面量
                value = value_str[1:-1]
            elif value_str.startswith('#[') and value_str.endswith(']'):
                # 表达式
                expr = value_str[2:-1]
                value = Generator("Expression", expr)
            elif value_str.startswith('#'):
                # Item 引用
                item_name = value_str[1:]
                value = Generator("ItemRef", item_name)
            else:
                # 数字或其他
                try:
                    value = float(value_str)
                    if value == int(value):
                        value = int(value)
                except:
                    value = value_str
            
            self.variables[var_name] = {'value': value}
    
    def _parse_item_definition(self, item_name):
        """解析 item 定义及其子项"""
        # 保存 item 名称
        start_line = self.current_line
        self.current_line += 1
        
        # 收集所有子项
        children = []
        base_indent = None
        
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            stripped = line.strip()
            
            # 空行跳过
            if not stripped:
                self.current_line += 1
                continue
            
            # 注释跳过
            if stripped.startswith('//'):
                self.current_line += 1
                continue
            
            indent = self._get_indent(line)
            
            # 如果是同级或更低级别的 item，结束
            if indent == 0:
                break
            
            # 设置基础缩进
            if base_indent is None:
                base_indent = indent
            
            # 只处理直接子项
            if indent == base_indent:
                # 解析这一行
                child = self._parse_line_content(stripped)
                children.append(child)
            
            self.current_line += 1
        
        # 创建 Roulette 生成器（从子项中随机选一个）
        if children:
            self.items[item_name] = Generator("Roulette", children)
        else:
            # 没有子项，item 名本身就是内容
            self.items[item_name] = item_name
    
    def _parse_line_content(self, line):
        """解析一行的内容，支持权重、表达式、变量等"""
        # 检查权重
        weight = 1
        content = line
        
        # 权重语法：:n:content 或 #[expr]:content
        if line.startswith('#['):
            # 动态权重
            match = re.match(r'^#\[([^\]]+)\]:(.*)$', line)
            if match:
                weight_expr = match.group(1)
                content = match.group(2)
                weight = Generator("Expression", weight_expr)
        elif line.startswith(':'):
            # 静态权重
            match = re.match(r'^:(\d+):(.*)$', line)
            if match:
                weight = int(match.group(1))
                content = match.group(2)
        
        # 解析内容（可能包含变量、表达式、行内随机等）
        parsed_content = self._parse_inline_content(content)
        
        # 如果内容是 Generator，设置权重
        if isinstance(parsed_content, Generator):
            parsed_content.weight = weight
            return parsed_content
        
        # 如果是字符串，包装成 Generator
        gen = Generator("PlainList", [parsed_content] if isinstance(parsed_content, str) else parsed_content)
        gen.weight = weight
        return gen
    
    def _parse_inline_content(self, text):
        """解析行内内容，处理变量、表达式、副作用、行内随机等"""
        if not text:
            return ""
        
        parts = []
        pos = 0
        
        while pos < len(text):
            char = text[pos]
            
            # 转义字符
            if char == '\\' and pos + 1 < len(text):
                next_char = text[pos + 1]
                if next_char in ['$', '#', '\\', '[', ']', '{', '}']:
                    parts.append(next_char)
                    pos += 2
                continue
            
            # 变量引用 $var
            if char == '$':
                # 提取变量名
                var_match = re.match(r'\$(\w+)', text[pos:])
                if var_match:
                    var_name = var_match.group(1)
                    parts.append(Generator("Variable", var_name))
                    pos += len(var_match.group(0))
                    continue
                
                # 带引号的引用 $"item"
                quote_match = re.match(r'\$"([^"]+)"', text[pos:])
                if quote_match:
                    item_name = quote_match.group(1)
                    parts.append(Generator("ItemRef", item_name))
                    pos += len(quote_match.group(0))
                    continue
            
            # # 开头的特殊语法
            if char == '#':
                # 表达式 #[...]
                if pos + 1 < len(text) and text[pos + 1] == '[':
                    end = self._find_matching_bracket(text, pos + 1, '[', ']')
                    if end != -1:
                        expr = text[pos + 2:end]
                        parts.append(Generator("Expression", expr))
                        pos = end + 1
                        continue
                
                # 副作用 #{...}
                if pos + 1 < len(text) and text[pos + 1] == '{':
                    end = self._find_matching_bracket(text, pos + 1, '{', '}')
                    if end != -1:
                        effect = text[pos + 2:end]
                        parts.append(Generator("SideEffect", effect))
                        pos = end + 1
                        continue
                
                # 行内随机 #(a|b|c)
                if pos + 1 < len(text) and text[pos + 1] == '(':
                    end = self._find_matching_bracket(text, pos + 1, '(', ')')
                    if end != -1:
                        options_str = text[pos + 2:end]
                        options = self._parse_inline_options(options_str)
                        parts.append(Generator("InlineRandom", options))
                        pos = end + 1
                continue
            
                # Item 引用 #item（后面跟空格或结束）
                item_match = re.match(r'#(\w+)', text[pos:])
                if item_match:
                    item_name = item_match.group(1)
                    parts.append(Generator("ItemRef", item_name))
                    pos += len(item_match.group(0))
                continue
            
            # 普通字符
            parts.append(char)
            pos += 1
        
        # 合并连续的字符串
        merged = []
        current_str = []
        
        for part in parts:
            if isinstance(part, str):
                current_str.append(part)
            else:
                if current_str:
                    merged.append(''.join(current_str))
                    current_str = []
                merged.append(part)
        
        if current_str:
            merged.append(''.join(current_str))
        
        # 如果只有一个元素，直接返回
        if len(merged) == 1:
            return merged[0]
        
        # 如果全是字符串，合并
        if all(isinstance(p, str) for p in merged):
            return ''.join(merged)
        
        # 返回 PlainList
        return Generator("PlainList", merged)
    
    def _parse_inline_options(self, options_str):
        """解析行内选项 #(a|b|c)，支持权重"""
        # 简单分割（不支持嵌套）
        parts = options_str.split('|')
        options = []
        
        for part in parts:
            part = part.strip()
            
            # 检查权重
            weight = 1
            content = part
            
            if part.startswith('#['):
                # 动态权重
                match = re.match(r'^#\[([^\]]+)\]:(.*)$', part)
                if match:
                    weight_expr = match.group(1)
                    content = match.group(2).strip()
                    weight = Generator("Expression", weight_expr)
            elif part.startswith(':'):
                # 静态权重
                match = re.match(r'^:(\d+):(.*)$', part)
                if match:
                    weight = int(match.group(1))
                    content = match.group(2).strip()
            
            # 解析内容
            parsed = self._parse_inline_content(content)
            
            # 包装成 Generator 并设置权重
            if isinstance(parsed, Generator):
                parsed.weight = weight
                options.append(parsed)
            else:
                gen = Generator("PlainList", [parsed])
                gen.weight = weight
                options.append(gen)
        
        return options
    
    def _find_matching_bracket(self, text, start, open_char, close_char):
        """查找匹配的括号"""
        count = 1
        pos = start + 1
        
        while pos < len(text) and count > 0:
            if text[pos] == '\\' and pos + 1 < len(text):
                pos += 2
                continue
            
            if text[pos] == open_char:
                count += 1
            elif text[pos] == close_char:
                count -= 1
            
            pos += 1
        
        if count == 0:
            return pos - 1
        return -1
    
    def _get_indent(self, line):
        """获取行的缩进级别（空格数）"""
        count = 0
        for char in line:
            if char == ' ':
                count += 1
            elif char == '\t':
                count += 4  # tab 算 4 个空格
            else:
                break
        return count
