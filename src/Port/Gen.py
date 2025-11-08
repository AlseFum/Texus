"""
Gen Port - 生成器模块

合并了原来的 generator.py, parser.py, file.py 和 __init__.py
"""
import random
import re
from typing import Any, Dict, List, Union, Optional
from datetime import datetime
from Common.base import FinalVis, entry
from Database import Table


# ============================================================================
# Generator 相关类
# ============================================================================

class GeneratorError(Exception):
    """生成器错误"""
    pass


class Context:
    """生成上下文 - 管理变量、引用和递归深度"""
    
    def __init__(self, items: Dict[str, Any] = None, parent: 'Context' = None):
        """初始化上下文
        
        Args:
            items: item 定义字典 {name: Generator}
            parent: 父上下文（用于变量作用域）
        """
        self.variables: Dict[str, Any] = {}  # 变量存储
        self.items: Dict[str, Any] = items or {}  # item 定义
        self.parent = parent
        self.recursion_depth = 0  # 递归深度
        self.max_recursion = 100  # 最大递归深度
        self.local_items: Dict[str, Any] = {}  # 局部item定义（内部item）
    
    def get_variable(self, name: str) -> Any:
        """获取变量值"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get_variable(name)
        return None
    
    def set_variable(self, name: str, value: Any):
        """设置变量值"""
        self.variables[name] = value
    
    def set_local_item(self, name: str, value: Any):
        """设置局部item定义"""
        self.local_items[name] = value
    
    def get_item(self, name: str) -> Any:
        """获取 item 定义"""
        # 首先检查局部item
        if name in self.local_items:
            return self.local_items[name]
        # 然后检查全局item
        if name in self.items:
            return self.items[name]
        # 最后检查父上下文
        if self.parent:
            return self.parent.get_item(name)
        return None
    
    def check_recursion(self):
        """检查递归深度"""
        if self.recursion_depth >= self.max_recursion:
            raise GeneratorError(f"递归深度超过限制 {self.max_recursion}")
        self.recursion_depth += 1
    
    def exit_recursion(self):
        """退出递归"""
        self.recursion_depth -= 1


class Generator:
    """生成器核心类
    
    支持的生成器类型：
    - PlainList: 顺序拼接所有元素
    - Roulette: 随机选择其中一个元素（支持权重）
    - Variable: 变量引用
    - ItemRef: 引用其他 item
    - Expression: 表达式计算 #[]
    - SideEffect: 副作用 #{}
    - InlineRandom: 行内快速随机 #()
    - Conditional: 条件语句
    - Repeat: 重复生成 #*n 或 #*[expr]
    """
    
    # 生成器类型
    PlainList = "PlainList"
    Roulette = "Roulette"
    Variable = "Variable"
    ItemRef = "ItemRef"
    Expression = "Expression"
    SideEffect = "SideEffect"
    InlineRandom = "InlineRandom"
    Conditional = "Conditional"
    Repeat = "Repeat"
    
    def __init__(self, type: str, thing: Any, weight: Union[int, 'Generator'] = 1):
        """初始化生成器
        
        Args:
            type: 生成器类型
            thing: 生成器内容（根据类型不同而不同）
            weight: 权重（可以是数字或 Generator 表达式）
        """
        self.type = type
        self.thing = thing
        self.weight = weight
    
    def gen(self, context: Context = None) -> str:
        """生成内容
        
        Args:
            context: 生成上下文
            
        Returns:
            生成的字符串内容
        """
        if context is None:
            context = Context()
        
        context.check_recursion()
        
        try:
            result = self._gen_internal(context)
            return result
        finally:
            context.exit_recursion()
    
    def _gen_internal(self, context: Context) -> str:
        """内部生成逻辑"""
        
        if self.type == self.PlainList:
            # 顺序拼接所有元素
            result = []
            for item in self.thing:
                if isinstance(item, Generator):
                    result.append(str(item.gen(context)))
                else:
                    result.append(str(item))
            return ''.join(result)
        
        elif self.type == self.Roulette:
            # 随机选择（支持权重）
            options = self.thing
            weights = []
            
            # 计算权重
            for option in options:
                if isinstance(option, Generator):
                    # 获取 option 的权重
                    w = option.weight
                    if isinstance(w, Generator):
                        # 动态权重，需要计算
                        w_value = w.gen(context)
                        try:
                            w = float(w_value)
                        except:
                            w = 1
                    weights.append(w)
                else:
                    weights.append(1)
            
            # 随机选择
            selected = random.choices(options, weights=weights, k=1)[0]
            
            if isinstance(selected, Generator):
                return selected.gen(context)
            return str(selected)
        
        elif self.type == self.Variable:
            # 变量引用
            var_name = self.thing
            value = context.get_variable(var_name)
            if value is None:
                return "None"
            if isinstance(value, Generator):
                return value.gen(context)
            return str(value)
        
        elif self.type == self.ItemRef:
            # 引用其他 item
            item_name = self.thing
            item = context.get_item(item_name)
            if item is None:
                return f"[undefined: {item_name}]"
            if isinstance(item, Generator):
                return item.gen(context)
            return str(item)
        
        elif self.type == self.Expression:
            # 表达式计算 #[]
            expr = self.thing
            return self._eval_expression(expr, context)
        
        elif self.type == self.SideEffect:
            # 副作用 #{} - 不输出内容，只修改状态
            effect = self.thing
            self._execute_side_effect(effect, context)
            return ""
        
        elif self.type == self.InlineRandom:
            # 行内快速随机 #() - 支持权重
            options = self.thing
            weights = []
            
            # 计算权重
            for option in options:
                if isinstance(option, Generator):
                    w = option.weight
                    if isinstance(w, Generator):
                        # 动态权重，需要计算
                        w_value = w.gen(context)
                        try:
                            w = float(w_value)
                        except:
                            w = 1
                    weights.append(w)
                else:
                    weights.append(1)
            
            # 随机选择
            selected = random.choices(options, weights=weights, k=1)[0]
            
            if isinstance(selected, Generator):
                return selected.gen(context)
            return str(selected)
        
        elif self.type == self.Conditional:
            # 条件语句
            return self._eval_conditional(self.thing, context)
        
        elif self.type == self.Repeat:
            # 重复生成 #*n 或 #*[expr]
            repeat_data = self.thing
            count = repeat_data.get('count', 1)
            content = repeat_data.get('content')
            use_index = repeat_data.get('use_index', False)
            
            # 计算重复次数
            if isinstance(count, Generator):
                count_str = count.gen(context)
                try:
                    count = int(float(count_str))
                except:
                    count = 1
            
            # 重复生成
            results = []
            for i in range(count):
                if use_index:
                    # 设置索引变量 #i（从1开始）
                    context.set_variable('i', i + 1)
                
                if isinstance(content, Generator):
                    results.append(content.gen(context))
                else:
                    results.append(str(content))
            
            return ''.join(results)
        
        return str(self.thing)
    
    def _eval_expression(self, expr: str, context: Context) -> str:
        """计算表达式 - 纯计算，不能有副作用"""
        # 替换变量和 item 引用
        expr = self._replace_refs_in_expr(expr, context)
        
        # 处理三元运算符
        if '?' in expr and ':' in expr:
            return self._eval_ternary(expr, context)
        
        # 直接计算表达式
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"[expr error: {e}]"
    
    def _replace_refs_in_expr(self, expr: str, context: Context) -> str:
        """替换表达式中的变量和 item 引用"""
        # 先处理转义字符 \$ -> $
        expr = expr.replace('\\$', '$')
        
        # 替换 $varname
        def replace_var(match):
            var_name = match.group(1)
            value = context.get_variable(var_name)
            if value is None:
                return "0"
            if isinstance(value, (int, float)):
                return str(value)
            if isinstance(value, str):
                return f'"{value}"'
            if isinstance(value, Generator):
                result = value.gen(context)
                try:
                    float(result)
                    return result
                except:
                    return f'"{result}"'
            return str(value)
        
        expr = re.sub(r'\$(\w+)', replace_var, expr)
        
        # 替换 #itemname
        def replace_item(match):
            item_name = match.group(1)
            item = context.get_item(item_name)
            if item is None:
                return '""'
            if isinstance(item, Generator):
                result = item.gen(context)
                return f'"{result}"'
            return f'"{item}"'
        
        expr = re.sub(r'#(\w+)', replace_item, expr)
        
        return expr
    
    def _eval_ternary(self, expr: str, context: Context) -> str:
        """计算三元运算符：condition ? true_val : false_val"""
        # 简单分割（不处理嵌套）
        parts = expr.split('?', 1)
        if len(parts) != 2:
            return expr
        
        condition = parts[0].strip()
        rest = parts[1].split(':', 1)
        if len(rest) != 2:
            return expr
        
        true_val = rest[0].strip()
        false_val = rest[1].strip()
        
        # 计算条件
        try:
            cond_result = eval(condition, {"__builtins__": {}}, {})
            if cond_result:
                # 移除引号（如果是字符串字面量）
                if true_val.startswith('"') and true_val.endswith('"'):
                    return true_val[1:-1]
                return true_val
            else:
                if false_val.startswith('"') and false_val.endswith('"'):
                    return false_val[1:-1]
                return false_val
        except:
            return expr
    
    def _execute_side_effect(self, effect: str, context: Context):
        """执行副作用 - 修改变量值"""
        effect = effect.strip()
        
        # 支持的运算符：=, +=, -=, *=, /=, ++, --
        
        # 前/后自增自减
        if match := re.match(r'^\$(\w+)\+\+$', effect):
            var_name = match.group(1)
            value = context.get_variable(var_name) or 0
            context.set_variable(var_name, value + 1)
            return
        
        if match := re.match(r'^\+\+\$(\w+)$', effect):
            var_name = match.group(1)
            value = context.get_variable(var_name) or 0
            context.set_variable(var_name, value + 1)
            return
        
        if match := re.match(r'^\$(\w+)--$', effect):
            var_name = match.group(1)
            value = context.get_variable(var_name) or 0
            context.set_variable(var_name, value - 1)
            return
        
        if match := re.match(r'^--\$(\w+)$', effect):
            var_name = match.group(1)
            value = context.get_variable(var_name) or 0
            context.set_variable(var_name, value - 1)
            return
        
        # 复合赋值运算符
        operators = ['+=', '-=', '*=', '/=', '=']
        for op in operators:
            if op in effect:
                parts = effect.split(op, 1)
                if len(parts) == 2:
                    var_part = parts[0].strip()
                    value_part = parts[1].strip()
                    
                    # 提取变量名
                    if not var_part.startswith('$'):
                        continue
                    var_name = var_part[1:]
                    
                    # 计算右侧值
                    if value_part.startswith('#') and not value_part.startswith('#['):
                        # item 引用
                        item_name = value_part[1:]
                        item = context.get_item(item_name)
                        if isinstance(item, Generator):
                            new_value = item.gen(context)
                        else:
                            new_value = item
                    elif value_part.startswith('#[') and value_part.endswith(']'):
                        # 表达式
                        expr = value_part[2:-1]
                        new_value = self._eval_expression(expr, context)
                        try:
                            new_value = float(new_value)
                        except:
                            pass
                    elif value_part.startswith('"') and value_part.endswith('"'):
                        # 字符串字面量
                        new_value = value_part[1:-1]
                    else:
                        # 表达式或数字
                        try:
                            replaced = self._replace_refs_in_expr(value_part, context)
                            new_value = eval(replaced, {"__builtins__": {}}, {})
                        except:
                            new_value = value_part
                    
                    # 执行运算
                    if op == '=':
                        context.set_variable(var_name, new_value)
                    elif op == '+=':
                        old_value = context.get_variable(var_name) or 0
                        context.set_variable(var_name, old_value + new_value)
                    elif op == '-=':
                        old_value = context.get_variable(var_name) or 0
                        context.set_variable(var_name, old_value - new_value)
                    elif op == '*=':
                        old_value = context.get_variable(var_name) or 0
                        context.set_variable(var_name, old_value * new_value)
                    elif op == '/=':
                        old_value = context.get_variable(var_name) or 0
                        if new_value != 0:
                            context.set_variable(var_name, old_value / new_value)
                    
                    return
    
    def _eval_conditional(self, cond_data: Dict, context: Context) -> str:
        """计算条件语句"""
        # 条件数据格式：{'branches': [(condition, Generator), ...], 'else': Generator}
        branches = cond_data.get('branches', [])
        else_branch = cond_data.get('else')
        
        for condition, generator in branches:
            # 计算条件
            cond_expr = self._replace_refs_in_expr(condition, context)
            try:
                result = eval(cond_expr, {"__builtins__": {}}, {})
                if result:
                    if isinstance(generator, Generator):
                        return generator.gen(context)
                    return str(generator)
            except:
                continue
        
        # else 分支
        if else_branch:
            if isinstance(else_branch, Generator):
                return else_branch.gen(context)
            return str(else_branch)
        
        return ""


# ============================================================================
# GenFile 类
# ============================================================================

class GenFile(entry):
    def __init__(self, value, root=None):
        self.root = root
        super().__init__(mime="gen", value=value)
    
    def to_dict(self):
        """重写 to_dict 方法，处理 GenFile 的特殊逻辑"""
        base_dict = super().to_dict()
        
        if self.root is not None:
            # 调用 generator 生成文本
            generated_text = self.root.gen()
            base_dict["value"] = {
                "text": generated_text,
                "lastSavedTime": self.value.get("lastSavedTime"),
                "sourceTimestamp": self.value.get("sourceTimestamp")
            }
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建 GenFile 对象"""
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典格式")
        
        # 创建基础 entry 对象
        base_entry = super(GenFile, cls).from_dict(data)
        
        # 创建 GenFile 实例
        instance = cls(
            value=base_entry.value,
            root=None  # root 需要单独处理，因为它是 Generator 对象
        )
        
        # 复制其他属性
        instance.lastModifiedTime = base_entry.lastModifiedTime
        
        return instance
    
    def gen(self, seed=None):
        """生成内容"""
        if self.root is not None:
            return self.root.gen(seed)
        return None


# ============================================================================
# Parser 类
# ============================================================================

class ParseError(Exception):
    """解析错误异常"""
    pass


class Parser:
    """基于缩进的生成器解析器"""
    
    def __init__(self, source_file):
        """初始化解析器
        
        Args:
            source_file: entry 对象，包含模板文本和元数据
        """
        self.source_file = source_file
        self.text = source_file.value.get("text", "")
        self.lines = self.text.split('\n')
        self.current_line = 0
        self.items = {}  # 存储 item 定义
        self.variables = {}  # 存储变量声明
        
        # 预处理：移除所有注释
        self.lines = self._remove_comments(self.text)
    
    def _remove_comments(self, source_text):
        """预处理：移除所有注释（单行和多行）"""
        processed_text = self._remove_comments_from_text(source_text)
        return processed_text.split('\n')

    def _remove_comments_from_text(self, source):
        """从整个文本中移除注释（逐字解析）"""
        result = []
        i = 0
        in_multiline_comment = False
        in_string = False
        
        while i < len(source):
            char = source[i]
            
            # 检查是否在字符串字面量中
            if char == '"' and not in_multiline_comment:
                in_string = not in_string
                result.append(char)
                i += 1
                continue
            
            # 如果在字符串中，直接保留字符
            if in_string:
                result.append(char)
                i += 1
                continue
            
            # 检查单行注释
            if not in_multiline_comment and i + 1 < len(source) and source[i:i+2] == '//':
                # 单行注释，跳过到行尾
                while i < len(source) and source[i] != '\n':
                    i += 1
                continue
            
            # 检查多行注释开始
            if not in_multiline_comment and i + 1 < len(source) and source[i:i+2] == '/*':
                in_multiline_comment = True
                i += 2
                continue
            
            # 检查多行注释结束
            if in_multiline_comment and i + 1 < len(source) and source[i:i+2] == '*/':
                in_multiline_comment = False
                i += 2
                continue
            
            # 如果不在注释中，保留字符
            if not in_multiline_comment:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def parse(self):
        """解析入口，返回 GenFile 对象"""
        if not self.text:
            root = Generator("PlainList", [])
        else:
            # 解析所有内容
            self._parse_document()
            
            # 选择根入口：优先使用 'main'，否则使用第一个 item
            if self.items:
                # 优先查找 'main' item
                if 'START' in self.items:
                    root_gen = self.items['START']
                if 'main' in self.items:
                    root_gen = self.items['main']
                else:
                    # 使用第一个 item
                    first_item_name = list(self.items.keys())[0]
                    root_gen = self.items[first_item_name]
                
                # 创建一个包装器，先初始化变量，再生成
                root = self._create_root_with_vars(root_gen)
            else:
                root = Generator("PlainList", [])
        
        # 创建 GenFile
        value = {
            "template": self.text,
            "sourceTimestamp": self.source_file.value.get("lastSavedTime"),
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
        # 移除开头的 $
        line = line[1:].strip()
        
        # 解析变量名和修饰符
        var_name = line
        modifiers = []
        
        # 检查关键字修饰符
        keywords = ['const', 'once']
        for keyword in keywords:
            if line.startswith(keyword + ' '):
                modifiers.append(keyword)
                line = line[len(keyword):].strip()
        
        # 提取变量名（到第一个空格或冒号或等号）
        name_end = len(line)
        for char in [':', '=', ' ']:
            pos = line.find(char)
            if pos != -1 and pos < name_end:
                name_end = pos
        
        var_name = line[:name_end].strip()
        rest = line[name_end:].strip()
        
        # $var : num
        if rest.startswith(':'):
            var_type = rest[1:].strip()
            self.variables[var_name] = {
                'type': var_type,
                'modifiers': modifiers
            }
        
        # $var : type = value
        elif ':' in rest and '=' in rest:
            # 处理 $var : type = value 格式
            type_part, value_part = rest.split('=', 1)
            var_type = type_part.split(':', 1)[1].strip()
            value_str = value_part.strip()
            
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
            
            self.variables[var_name] = {
                'type': var_type,
                'value': value,
                'modifiers': modifiers
            }
        
        # $var = value
        elif rest.startswith('='):
            value_str = rest[1:].strip()
            
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
            
            self.variables[var_name] = {
                'value': value,
                'modifiers': modifiers
            }
    
    def _parse_item_definition(self, item_name):
        """解析 item 定义及其子项"""
        # 处理带引号的item名称
        if item_name.startswith('"') and item_name.endswith('"'):
            item_name = item_name[1:-1]
        
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
            
            indent = self._get_indent(line)
            
            # 如果是同级或更低级别的 item，结束
            if indent == 0:
                break
            
            # 设置基础缩进
            if base_indent is None:
                base_indent = indent
            
            # 只处理直接子项
            if indent == base_indent:
                # 检查是否需要多行合并
                merged_line = stripped
                line_idx = self.current_line
                
                # 如果行尾有 \，则与下一行合并
                while merged_line.endswith('\\'):
                    merged_line = merged_line[:-1]  # 移除末尾的 \
                    line_idx += 1
                    if line_idx < len(self.lines):
                        next_line = self.lines[line_idx].strip()
                        # 跳过空行
                        while next_line == '':
                            line_idx += 1
                            if line_idx >= len(self.lines):
                                break
                            next_line = self.lines[line_idx].strip()
                        if line_idx < len(self.lines) and self._get_indent(self.lines[line_idx]) == base_indent:
                            merged_line += next_line
                            self.current_line = line_idx
                        else:
                            break
                    else:
                        break
                
                # 解析合并后的行
                child = self._parse_line_content(merged_line)
                
                # 检查是否有内部item定义
                if self._has_internal_items(line_idx):
                    child = self._parse_with_internal_items(child, line_idx, base_indent)
                
                children.append(child)
            
            self.current_line += 1
        
        # 创建 Roulette 生成器（从子项中随机选一个）
        if children:
            self.items[item_name] = Generator("Roulette", children)
        else:
            # 没有子项，创建一个空的生成器
            self.items[item_name] = Generator("PlainList", [""])
    
    def _parse_line_content(self, line):
        """解析一行的内容，支持权重、表达式、变量等"""
        # 检查权重
        weight = 1
        content = line
        
        # 检查 ^n 权重语法
        if line.startswith('^'):
            # 静态权重 ^n
            match = re.match(r'^\^(\d+)\s+(.*)$', line)
            if match:
                weight = int(match.group(1))
                content = match.group(2)
            # 动态权重 ^[expr]
            elif line.startswith('^['):
                match = re.match(r'^\^\[([^\]]+)\]\s+(.*)$', line)
                if match:
                    weight_expr = match.group(1)
                    content = match.group(2)
                    weight = Generator("Expression", weight_expr)
        
        # 检查旧的权重语法（保持兼容）
        elif line.startswith(':#['):
            # 动态权重（以冒号开头）
            match = re.match(r'^:#\[([^\]]+)\]:(.*)$', line)
            if match:
                weight_expr = match.group(1)
                content = match.group(2)
                weight = Generator("Expression", weight_expr)
        elif line.startswith('#['):
            # 动态权重（直接开头）
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
                # 特殊字符转义
                if next_char in ['$', '#', '\\', '[', ']', '{', '}']:
                    parts.append(next_char)
                    pos += 2
                    continue
                # 格式控制转义
                elif next_char == 'n':
                    parts.append('\n')
                    pos += 2
                    continue
                elif next_char == 't':
                    parts.append('\t')
                    pos += 2
                    continue
                elif next_char == 's':
                    parts.append(' ')
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
                # 重复生成 #*n 或 #*[expr]
                if pos + 1 < len(text) and text[pos + 1] == '*':
                    repeat_result = self._parse_repeat(text[pos:])
                    if repeat_result:
                        parts.append(repeat_result['generator'])
                        pos += repeat_result['length']
                        continue
                
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
            
                # 带引号的item引用 #"item with spaces"
                quote_item_match = re.match(r'#"([^"]+)"', text[pos:])
                if quote_item_match:
                    item_name = quote_item_match.group(1)
                    parts.append(Generator("ItemRef", item_name))
                    pos += len(quote_item_match.group(0))
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
            
            # 检查 ^n 权重语法
            if part.startswith('^'):
                # 静态权重 ^n
                match = re.match(r'^\^(\d+)\s+(.*)$', part)
                if match:
                    weight = int(match.group(1))
                    content = match.group(2).strip()
                # 动态权重 ^[expr]
                elif part.startswith('^['):
                    match = re.match(r'^\^\[([^\]]+)\]\s+(.*)$', part)
                    if match:
                        weight_expr = match.group(1)
                        content = match.group(2).strip()
                        weight = Generator("Expression", weight_expr)
            
            # 检查旧的权重语法（保持兼容）
            elif part.startswith(':#['):
                # 动态权重（以冒号开头）
                match = re.match(r'^:#\[([^\]]+)\]:(.*)$', part)
                if match:
                    weight_expr = match.group(1)
                    content = match.group(2).strip()
                    weight = Generator("Expression", weight_expr)
            elif part.startswith('#['):
                # 动态权重（直接开头）
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
    
    def _parse_repeat(self, text):
        """解析重复语法 #*n 或 #*[expr] 或 #*n`content`"""
        # #*[expr]item 或 #*[expr]`content`
        if text.startswith('#*['):
            end_bracket = self._find_matching_bracket(text, 2, '[', ']')
            if end_bracket == -1:
                return None
            
            count_expr = text[3:end_bracket]
            count_gen = Generator("Expression", count_expr)
            rest = text[end_bracket + 1:]
            
            # 检查是否是 `content` 形式
            if rest.startswith('`'):
                end_backtick = rest.find('`', 1)
                if end_backtick != -1:
                    content = rest[1:end_backtick]
                    # 检查content中是否有$i，决定use_index
                    use_index = '$i' in content or '#i' in content
                    content_gen = self._parse_inline_content(content)
                    
                    repeat_gen = Generator("Repeat", {
                        'count': count_gen,
                        'content': content_gen,
                        'use_index': use_index
                    })
                    return {'generator': repeat_gen, 'length': end_bracket + 1 + end_backtick + 1}
            
            # #*[expr]item 形式
            item_match = re.match(r'(\w+)', rest)
            if item_match:
                item_name = item_match.group(1)
                content_gen = Generator("ItemRef", item_name)
                repeat_gen = Generator("Repeat", {
                    'count': count_gen,
                    'content': content_gen,
                    'use_index': False
                })
                return {'generator': repeat_gen, 'length': end_bracket + 1 + len(item_name)}
        
        # #*nitem 或 #*n`content`
        match = re.match(r'#\*(\d+)', text)
        if match:
            count = int(match.group(1))
            rest = text[len(match.group(0)):]
            
            # 检查是否是 `content` 形式
            if rest.startswith('`'):
                end_backtick = rest.find('`', 1)
                if end_backtick != -1:
                    content = rest[1:end_backtick]
                    # 检查content中是否有$i或#i
                    use_index = '$i' in content or '#i' in content
                    content_gen = self._parse_inline_content(content)
                    
                    repeat_gen = Generator("Repeat", {
                        'count': count,
                        'content': content_gen,
                        'use_index': use_index
                    })
                    return {'generator': repeat_gen, 'length': len(match.group(0)) + end_backtick + 1}
            
            # #*nitem 形式
            item_match = re.match(r'(\w+)', rest)
            if item_match:
                item_name = item_match.group(1)
                content_gen = Generator("ItemRef", item_name)
                repeat_gen = Generator("Repeat", {
                    'count': count,
                    'content': content_gen,
                    'use_index': False
                })
                return {'generator': repeat_gen, 'length': len(match.group(0)) + len(item_name)}
        
        return None
    
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
    
    def _has_internal_items(self, line_idx):
        """检查指定行之后是否有内部item定义"""
        if line_idx + 1 >= len(self.lines):
            return False
        
        # 检查下一行的缩进是否更深
        next_line = self.lines[line_idx + 1]
        next_indent = self._get_indent(next_line)
        current_indent = self._get_indent(self.lines[line_idx])
        
        return next_indent > current_indent
    
    def _parse_with_internal_items(self, child, line_idx, base_indent):
        """解析带有内部item的内容"""
        # 创建一个特殊的生成器，在生成时设置局部item
        class InternalItemGenerator(Generator):
            def __init__(self, child, parser, line_idx, base_indent):
                super().__init__("InternalItem", child)
                self.child = child
                self.parser = parser
                self.line_idx = line_idx
                self.base_indent = base_indent
            
            def gen(self, context=None):
                if context is None:
                    context = Context()
                
                # 解析内部item
                internal_items = self.parser._parse_internal_items(self.line_idx, self.base_indent)
                
                # 设置到上下文中
                for name, item in internal_items.items():
                    context.set_local_item(name, item)
                
                # 生成内容
                return self.child.gen(context)
        
        return InternalItemGenerator(child, self, line_idx, base_indent)
    
    def _parse_internal_items(self, start_line_idx, base_indent):
        """解析内部item定义"""
        internal_items = {}
        line_idx = start_line_idx + 1
        
        while line_idx < len(self.lines):
            line = self.lines[line_idx]
            stripped = line.strip()
            
            # 空行跳过
            if not stripped:
                line_idx += 1
                continue
            
            indent = self._get_indent(line)
            
            # 如果缩进不够深，结束
            if indent <= base_indent:
                break
            
            # 如果是直接子项（比base_indent深一级），解析为内部item
            if indent == base_indent + 4:  # 假设4个空格为一级缩进
                # 提取item名称
                item_name = stripped
                if item_name.startswith('"') and item_name.endswith('"'):
                    item_name = item_name[1:-1]
                
                # 解析子项
                children = []
                line_idx += 1
                
                while line_idx < len(self.lines):
                    sub_line = self.lines[line_idx]
                    sub_stripped = sub_line.strip()
                    
                    if not sub_stripped:
                        line_idx += 1
                        continue
                    
                    sub_indent = self._get_indent(sub_line)
                    if sub_indent <= indent:
                        break
                    
                    if sub_indent == indent + 4:
                        # 解析子项内容
                        child = self._parse_line_content(sub_stripped)
                        children.append(child)
                    
                    line_idx += 1
                
                # 创建内部item
                if children:
                    internal_items[item_name] = Generator("Roulette", children)
                else:
                    internal_items[item_name] = Generator("PlainList", [""])
            else:
                line_idx += 1
        
        return internal_items
    
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


# ============================================================================
# Gen Port 类
# ============================================================================

class Gen:
    """生成器 Port - 从 pub 表读取内容并生成随机文本
    
    使用 gen 表缓存解析后的 Generator 对象，根据时间戳判断是否需要重新解析
    """
    
    @staticmethod
    def access(pack) -> FinalVis:
        """主访问方法"""
        main_table = Table.of("main")
        gen_table = Table.of("GEN")
        
        # 1. 从主表获取内容
        data = main_table.get(pack.entry)
        if data is None:
            return FinalVis.of("raw", payload={"text": "(empty)"})
        
        # 统一转换为 entry 格式
        if isinstance(data, entry):
            pub_file = data
        elif isinstance(data, dict):
            pub_file = entry(mime="text", value=data)
        else:
            pub_file = entry(mime="text", value={"text": str(data)})
            # 如果是原始数据，保存为entry对象
            main_table.set(pack.entry, pub_file)
        
        pub_timestamp = pub_file.value.get("lastSavedTime")
        
        # 2. 检查 gen 表缓存
        cached_genfile = gen_table.get(pack.entry)
        genfile = None
        
        # 3. 判断缓存是否有效
        if isinstance(cached_genfile, GenFile):
            cached_timestamp = cached_genfile.value.get("sourceTimestamp")
            if cached_timestamp == pub_timestamp and cached_genfile.root is not None:
                genfile = cached_genfile
        
        # 4. 如果需要，重新解析
        if genfile is None:
            try:
                genfile = Parser(pub_file).parse()
                gen_table.set(pack.entry, genfile)
            except Exception as e:
                return FinalVis.of("raw", payload={"text": f"Error: {e}"})
        
        # 5. 生成内容并输出
        result = genfile.gen()
        is_api = getattr(pack, 'by', '') == 'api'
        result_str = str(result)
        if is_api:
            # API请求：只需要value
            return FinalVis.of("raw", value=result_str, skip=True)
        else:
            # Web请求：只需要payload
            return FinalVis.of("raw", payload={"text": result_str})


# 插件注册函数
def registry():
    return {
        "mime": "gen",
        "port": Gen
    }

