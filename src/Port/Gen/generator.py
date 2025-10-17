import random
import re
from typing import Any, Dict, List, Union, Optional

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
        """计算表达式 - 纯计算，不能有副作用
        
        支持的运算：
        - 数值：+, -, *, /, %
        - 比较：>, <, >=, <=, ==, !=
        - 逻辑：and, or, not
        - 三元运算符：condition ? true_val : false_val
        - 变量引用：$varname
        - item 引用：#itemname
        """
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
