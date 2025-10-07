from .generator import Generator

class ParseError(Exception):
    """解析错误异常"""
    pass

class Parser:
    """
    BNF风格的生成器解析器
    
    语法规则：
    - [a|b|c]     : Roulette - 随机选择其中一个
    - {a|b|c}     : Roulette - 随机选择其中一个（另一种写法）
    - 普通文本     : 直接输出
    - 支持嵌套    : [a|{b|c}|[d|e]]
    - 转义字符    : \\[ \\] \\{ \\} \\| 表示字面字符
    
    示例：
    "你好[世界|朋友]" -> 随机输出 "你好世界" 或 "你好朋友"
    "{早上|中午|晚上}好" -> 输出 "早上好"、"中午好" 或 "晚上好"
    "[{很|非常}[高兴|开心]|还行]" -> 嵌套生成
    """
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)
    
    def parse(self):
        """解析入口，返回 Generator 对象"""
        if not self.text:
            return Generator("PlainList", [])
        
        result = self._parse_sequence()
        
        # 如果结果是单个元素，直接返回
        if isinstance(result, list) and len(result) == 1 and isinstance(result[0], str):
            return Generator("PlainList", result)
        
        return result if isinstance(result, Generator) else Generator("PlainList", result if isinstance(result, list) else [result])
    
    def _current_char(self):
        """获取当前字符"""
        if self.pos >= self.length:
            return None
        return self.text[self.pos]
    
    def _peek_char(self, offset=1):
        """预览后续字符"""
        pos = self.pos + offset
        if pos >= self.length:
            return None
        return self.text[pos]
    
    def _advance(self):
        """前进一个字符"""
        self.pos += 1
    
    def _parse_sequence(self, end_chars=None):
        """解析序列，直到遇到结束字符"""
        if end_chars is None:
            end_chars = []
        
        elements = []
        current_text = []
        
        while self.pos < self.length:
            char = self._current_char()
            
            # 检查是否到达结束字符
            if char in end_chars:
                break
            
            # 转义字符
            if char == '\\':
                next_char = self._peek_char()
                if next_char in ['[', ']', '{', '}', '|', '\\']:
                    self._advance()
                    current_text.append(next_char)
                    self._advance()
                    continue
                else:
                    current_text.append(char)
                    self._advance()
                    continue
            
            # Roulette 选择器 [a|b|c]
            if char == '[':
                if current_text:
                    elements.append(''.join(current_text))
                    current_text = []
                self._advance()
                roulette = self._parse_roulette()
                elements.append(roulette)
                continue
            
            # Sequence 序列器 {a|b|c}
            if char == '{':
                if current_text:
                    elements.append(''.join(current_text))
                    current_text = []
                self._advance()
                sequence = self._parse_braced_sequence()
                elements.append(sequence)
                continue
            
            # 普通字符
            current_text.append(char)
            self._advance()
        
        # 添加剩余文本
        if current_text:
            elements.append(''.join(current_text))
        
        # 如果只有一个元素且是字符串，直接返回
        if len(elements) == 1 and isinstance(elements[0], str):
            return elements[0]
        
        # 如果所有元素都是字符串，合并它们
        if all(isinstance(e, str) for e in elements):
            return ''.join(elements)
        
        # 否则返回 PlainList 生成器
        return Generator("PlainList", elements)
    
    def _parse_roulette(self):
        """解析 Roulette [a|b|c]"""
        options = []
        current_option = []
        
        while self.pos < self.length:
            char = self._current_char()
            
            # 结束 Roulette
            if char == ']':
                # 添加最后一个选项
                if current_option or len(options) == 0:
                    option = self._build_option(current_option)
                    options.append(option)
                self._advance()
                break
            
            # 分隔符
            if char == '|':
                option = self._build_option(current_option)
                options.append(option)
                current_option = []
                self._advance()
                continue
            
            # 转义字符
            if char == '\\':
                next_char = self._peek_char()
                if next_char in ['[', ']', '{', '}', '|', '\\']:
                    self._advance()
                    current_option.append(('text', next_char))
                    self._advance()
                    continue
                else:
                    current_option.append(('text', char))
                    self._advance()
                    continue
            
            # 嵌套 Roulette
            if char == '[':
                self._advance()
                nested = self._parse_roulette()
                current_option.append(('gen', nested))
                continue
            
            # 嵌套 Sequence
            if char == '{':
                self._advance()
                nested = self._parse_braced_sequence()
                current_option.append(('gen', nested))
                continue
            
            # 普通字符
            current_option.append(('text', char))
            self._advance()
        
        if not options:
            raise ParseError(f"空的 Roulette 在位置 {self.pos}")
        
        return Generator("Roulette", options)
    
    def _parse_braced_sequence(self):
        """解析花括号序列 {a|b|c}"""
        elements = []
        current_element = []
        
        while self.pos < self.length:
            char = self._current_char()
            
            # 结束序列
            if char == '}':
                # 添加最后一个元素
                if current_element or len(elements) == 0:
                    element = self._build_option(current_element)
                    elements.append(element)
                self._advance()
                break
            
            # 分隔符 - 在花括号中，| 表示并列元素
            if char == '|':
                element = self._build_option(current_element)
                elements.append(element)
                current_element = []
                self._advance()
                continue
            
            # 转义字符
            if char == '\\':
                next_char = self._peek_char()
                if next_char in ['[', ']', '{', '}', '|', '\\']:
                    self._advance()
                    current_element.append(('text', next_char))
                    self._advance()
                    continue
                else:
                    current_element.append(('text', char))
                    self._advance()
                    continue
            
            # 嵌套 Roulette
            if char == '[':
                self._advance()
                nested = self._parse_roulette()
                current_element.append(('gen', nested))
                continue
            
            # 嵌套 Sequence
            if char == '{':
                self._advance()
                nested = self._parse_braced_sequence()
                current_element.append(('gen', nested))
                continue
            
            # 普通字符
            current_element.append(('text', char))
            self._advance()
        
        if not elements:
            raise ParseError(f"空的序列在位置 {self.pos}")
        
        # 花括号表示一个 Roulette（从多个选项中选一个）
        return Generator("Roulette", elements)
    
    def _build_option(self, tokens):
        """从 token 列表构建选项（字符串或 Generator）"""
        if not tokens:
            return ""
        
        # 如果只有一个 token
        if len(tokens) == 1:
            token_type, token_value = tokens[0]
            if token_type == 'text':
                return token_value
            else:  # 'gen'
                return token_value
        
        # 多个 tokens，需要组合
        result = []
        for token_type, token_value in tokens:
            if token_type == 'text':
                result.append(token_value)
            else:  # 'gen'
                result.append(token_value)
        
        # 如果全是字符串，合并
        if all(isinstance(x, str) for x in result):
            return ''.join(result)
        
        # 否则返回 PlainList
        return Generator("PlainList", result)

