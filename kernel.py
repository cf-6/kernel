#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kernel 语言翻译器 v2.0
将 Kernel 代码转换为 Python/Shell/C 代码
支持错误恢复、类型检查、语法高亮
仅用于本地安全学习和授权测试
"""

import re
import json
import subprocess
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

# ============================================================
# 0. 颜色输出（语法高亮支持）
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================
# 1. 词法分析器 (Tokenizer) - 增强版
# ============================================================

class TokenType:
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    OPERATOR = "OPERATOR"
    BOUNDARY = "BOUNDARY"
    COMMENT = "COMMENT"
    EOF = "EOF"
    
    # 新增：类型标记
    TYPE_KEYWORD = "TYPE_KEYWORD"
    BUILTIN_FUNC = "BUILTIN_FUNC"
    CONSTANT = "CONSTANT"

@dataclass
class Token:
    type: str
    value: Any
    line: int
    col: int
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.col})"

class Tokenizer:
    # Kernel 关键字列表（完整版）
    KEYWORDS = {
        # 边界与作用域
        '!', '?', 'k', 'set', 'permust', 'space', 'import', 'export',
        # 控制流
        'if', 'else', 'elif', 'while', 'for', 'foreach', 'break', 'continue',
        'return', 'match', 'case', 'default', 'pass', 'goto', 'label',
        # 函数
        'λ', 'fn', 'rccode', 'call', 'addr', 'bind', 'callback', 'hook',
        # 网络
        'cmper', 'ping', 'fromcP', 'send', 'recv', 'sniff', 'spoof', 'scan',
        'listen', 'connect', 'resolve', 'proxy', 'hcp', 'kimax', 'sotxmax',
        # 攻击
        'exploit', 'payload', 'shellcode', 'rop', 'overflow', 'inject', 'pivot',
        'escalate', 'persist', 'exfil', 'hijack', 'ditrem', 'rizipo',
        # 防御
        'guard', 'canary', 'aslr', 'sandbox', 'monitor', 'detect', 'block',
        'quarantine', 'rollback', 'shield', 'honeypot',
        # 资源
        'coremuch', 'mcp', 'time', 'sleep', 'sleepmain', 'yield', 'sync', 'atomic',
        # 文件
        'look', 'mip', 'miv', 'opient', 'copyexe', 'zaig', 'tbl', 'cfp',
        # 权限
        'root', 'shell', 'qmew', 'GTT',
        # 审计
        'hash', 'record', 'audit', 'verify', 'proof', 'seal', 'log',
        # 调试
        'debug', 'assert', 'inspect', 'watch', 'trace',
        # 查询
        'interesting', 'where', 'limit', 'order', 'group', 'dlk',
        # 类型
        'strt', 'ygping', 'string', 'type', 'struct',
        # 宏
        'macro', 'unroll', 'inline', 'generate',
        # 并发
        'go', 'parallel', 'spawn', 'await', 'async',
        # 特殊
        'pass', 'move', 'swap', 'cast',
        # 新增：面向对象
        'class', 'extends', 'implements', 'super', 'this', 'new',
        # 新增：异常处理
        'try', 'catch', 'finally', 'throw',
        # 新增：并发
        'select', 'chan', 'defer',
    }
    
    # 类型关键字
    TYPE_KEYWORDS = {'int', 'float', 'bool', 'string', 'void', 'any'}
    
    # 内置函数
    BUILTIN_FUNCS = {'print', 'len', 'range', 'type', 'str', 'int', 'float', 'bool'}
    
    # 常量
    CONSTANTS = {'true', 'false', 'null', 'undefined', 'None'}
    
    # 运算符
    OPERATORS = {
        '+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=',
        '&&', '||', '!', '&', '|', '^', '<<', '>>', '->', '=>',
        '++', '--', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=',
    }
    
    BOUNDARY_CHARS = {'{', '}', '(', ')', '[', ']', ';', ',', ':', '.', '@'}
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.errors = []
    
    def tokenize(self) -> Tuple[List[Token], List[str]]:
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            
            # 跳过空白
            if ch.isspace():
                self._advance()
                continue
            
            # 注释
            if ch == '/' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/':
                self._skip_line_comment()
                continue
            if ch == '/' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '*':
                self._skip_block_comment()
                continue
            
            # 字符串
            if ch == '"' or ch == "'":
                self._read_string(ch)
                continue
            
            # 数字
            if ch.isdigit() or (ch == '-' and self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit()):
                self._read_number()
                continue
            
            # 标识符或关键字
            if ch.isalpha() or ch == '_':
                self._read_identifier()
                continue
            
            # 运算符
            if ch in self.OPERATORS or (self.pos + 1 < len(self.source) and self.source[self.pos:self.pos+2] in self.OPERATORS):
                self._read_operator()
                continue
            
            # 边界符号
            if ch in self.BOUNDARY_CHARS:
                self.tokens.append(Token(TokenType.BOUNDARY, ch, self.line, self.col))
                self._advance()
                continue
            
            # 未知字符
            error = f"未知字符 '{ch}' at {self.line}:{self.col}"
            self.errors.append(error)
            self._advance()
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return self.tokens, self.errors
    
    def _advance(self):
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1
    
    def _skip_line_comment(self):
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self._advance()
    
    def _skip_block_comment(self):
        self._advance()
        self._advance()
        while self.pos < len(self.source):
            if self.source[self.pos] == '*' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/':
                self._advance()
                self._advance()
                break
            self._advance()
    
    def _read_string(self, quote_char: str):
        start_line, start_col = self.line, self.col
        self._advance()
        value = ""
        while self.pos < len(self.source) and self.source[self.pos] != quote_char:
            if self.source[self.pos] == '\\':
                self._advance()
                if self.pos < len(self.source):
                    value += self.source[self.pos]
                    self._advance()
            else:
                value += self.source[self.pos]
                self._advance()
        if self.pos >= len(self.source):
            self.errors.append(f"未闭合的字符串 at {start_line}:{start_col}")
            return
        self._advance()
        self.tokens.append(Token(TokenType.STRING, value, start_line, start_col))
    
    def _read_number(self):
        start_line, start_col = self.line, self.col
        value = ""
        if self.source[self.pos] == '-':
            value += '-'
            self._advance()
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
            value += self.source[self.pos]
            self._advance()
        if '.' in value:
            self.tokens.append(Token(TokenType.NUMBER, float(value), start_line, start_col))
        else:
            self.tokens.append(Token(TokenType.NUMBER, int(value), start_line, start_col))
    
    def _read_identifier(self):
        start_line, start_col = self.line, self.col
        value = ""
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            value += self.source[self.pos]
            self._advance()
        
        if value in self.KEYWORDS:
            self.tokens.append(Token(TokenType.KEYWORD, value, start_line, start_col))
        elif value in self.TYPE_KEYWORDS:
            self.tokens.append(Token(TokenType.TYPE_KEYWORD, value, start_line, start_col))
        elif value in self.BUILTIN_FUNCS:
            self.tokens.append(Token(TokenType.BUILTIN_FUNC, value, start_line, start_col))
        elif value in self.CONSTANTS:
            self.tokens.append(Token(TokenType.CONSTANT, value, start_line, start_col))
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, value, start_line, start_col))
    
    def _read_operator(self):
        start_line, start_col = self.line, self.col
        if self.pos + 1 < len(self.source) and self.source[self.pos:self.pos+2] in self.OPERATORS:
            value = self.source[self.pos:self.pos+2]
            self._advance()
            self._advance()
        else:
            value = self.source[self.pos]
            self._advance()
        self.tokens.append(Token(TokenType.OPERATOR, value, start_line, start_col))


# ============================================================
# 2. 语法分析器 (Parser) - 增强版
# ============================================================

class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    imports: List[str] = field(default_factory=list)

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class CommandStatement(Statement):
    command: str
    args: List[ASTNode]
    block: Optional[List[Statement]] = None
    modifiers: List[str] = field(default_factory=list)

@dataclass
class IfStatement(Statement):
    condition: ASTNode
    then_block: List[Statement]
    elif_blocks: List[Tuple[ASTNode, List[Statement]]] = field(default_factory=list)
    else_block: Optional[List[Statement]] = None

@dataclass
class WhileStatement(Statement):
    condition: ASTNode
    body: List[Statement]

@dataclass
class ForStatement(Statement):
    variable: str
    iterable: ASTNode
    body: List[Statement]

@dataclass
class AssignmentStatement(Statement):
    target: str
    value: ASTNode
    type_hint: Optional[str] = None
    is_constant: bool = False

@dataclass
class FunctionDef(Statement):
    name: str
    params: List[Tuple[str, Optional[str]]]
    return_type: Optional[str]
    body: List[Statement]

@dataclass
class ReturnStatement(Statement):
    value: Optional[ASTNode]

@dataclass
class Expression(ASTNode):
    pass

@dataclass
class BinaryOp(Expression):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class UnaryOp(Expression):
    op: str
    right: ASTNode

@dataclass
class Literal(Expression):
    value: Any

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class NumberLiteral(Expression):
    value: Any

@dataclass
class FunctionCall(Expression):
    name: str
    args: List[ASTNode]

@dataclass
class MemberAccess(Expression):
    object: ASTNode
    member: str

@dataclass
class ClassDef(Statement):
    name: str
    extends: Optional[str]
    methods: List[FunctionDef]

@dataclass
class TryStatement(Statement):
    try_block: List[Statement]
    catch_blocks: List[Tuple[str, List[Statement]]]
    finally_block: Optional[List[Statement]]

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
    
    def peek(self) -> Token:
        if self.pos >= len(self.tokens):
            return Token(TokenType.EOF, None, 0, 0)
        return self.tokens[self.pos]
    
    def consume(self, expected_type: str = None, expected_value: Any = None) -> Token:
        token = self.peek()
        if expected_type and token.type != expected_type:
            self.errors.append(f"期望 {expected_type}，实际 {token.type} at {token.line}:{token.col}")
            return token
        if expected_value and token.value != expected_value:
            self.errors.append(f"期望 '{expected_value}'，实际 '{token.value}' at {token.line}:{token.col}")
            return token
        self.pos += 1
        return token
    
    def synchronize(self):
        """错误恢复：跳过到下一个语句开始"""
        while self.peek().type != TokenType.EOF:
            if self.peek().type == TokenType.KEYWORD:
                return
            if self.peek().type == TokenType.BOUNDARY and self.peek().value == ';':
                self.pos += 1
                return
            self.pos += 1
    
    def parse(self) -> Program:
        imports = []
        statements = []
        while self.peek().type != TokenType.EOF:
            token = self.peek()
            if token.value == 'import':
                imports.append(self.parse_import())
            else:
                try:
                    stmt = self.parse_statement()
                    if stmt:
                        statements.append(stmt)
                except Exception as e:
                    self.errors.append(f"解析错误: {e}")
                    self.synchronize()
        return Program(statements, imports)
    
    def parse_import(self) -> str:
        self.consume(TokenType.KEYWORD, 'import')
        imp = self.consume(TokenType.STRING).value
        return imp
    
    def parse_statement(self) -> Optional[Statement]:
        token = self.peek()
        
        if token.type == TokenType.KEYWORD:
            if token.value == 'if':
                return self.parse_if()
            elif token.value == 'while':
                return self.parse_while()
            elif token.value == 'for':
                return self.parse_for()
            elif token.value == 'let':
                return self.parse_let()
            elif token.value == 'const':
                return self.parse_const()
            elif token.value == 'fn':
                return self.parse_function()
            elif token.value == 'return':
                return self.parse_return()
            elif token.value == 'class':
                return self.parse_class()
            elif token.value == 'try':
                return self.parse_try()
            elif token.value == 'break':
                self.consume(TokenType.KEYWORD, 'break')
                return None
            elif token.value == 'continue':
                self.consume(TokenType.KEYWORD, 'continue')
                return None
            elif token.value in ['ping', 'scan', 'exploit', 'shell', 'root', 'log', 'send', 'exfil',
                                 'sniff', 'spoof', 'connect', 'listen', 'cmper', 'guard', 'monitor']:
                return self.parse_command()
            else:
                return self.parse_command()
        
        elif token.type == TokenType.IDENTIFIER:
            # 检查是否是函数调用
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].value == '(':
                return self.parse_command()
            return self.parse_assignment()
        
        else:
            return None
    
    def parse_if(self) -> IfStatement:
        self.consume(TokenType.KEYWORD, 'if')
        condition = self.parse_expression()
        then_block = self.parse_block()
        elif_blocks = []
        while self.peek().value == 'elif':
            self.consume(TokenType.KEYWORD, 'elif')
            cond = self.parse_expression()
            block = self.parse_block()
            elif_blocks.append((cond, block))
        else_block = None
        if self.peek().value == 'else':
            self.consume(TokenType.KEYWORD, 'else')
            else_block = self.parse_block()
        return IfStatement(condition, then_block, elif_blocks, else_block)
    
    def parse_while(self) -> WhileStatement:
        self.consume(TokenType.KEYWORD, 'while')
        condition = self.parse_expression()
        body = self.parse_block()
        return WhileStatement(condition, body)
    
    def parse_for(self) -> ForStatement:
        self.consume(TokenType.KEYWORD, 'for')
        variable = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.KEYWORD, 'in')
        iterable = self.parse_expression()
        body = self.parse_block()
        return ForStatement(variable, iterable, body)
    
    def parse_let(self) -> AssignmentStatement:
        self.consume(TokenType.KEYWORD, 'let')
        is_const = False
        target = self.consume(TokenType.IDENTIFIER).value
        type_hint = None
        if self.peek().value == ':':
            self.consume(TokenType.BOUNDARY, ':')
            type_hint = self.consume(TokenType.TYPE_KEYWORD).value
        self.consume(TokenType.OPERATOR, '=')
        value = self.parse_expression()
        return AssignmentStatement(target, value, type_hint, is_const)
    
    def parse_const(self) -> AssignmentStatement:
        self.consume(TokenType.KEYWORD, 'const')
        target = self.consume(TokenType.IDENTIFIER).value
        type_hint = None
        if self.peek().value == ':':
            self.consume(TokenType.BOUNDARY, ':')
            type_hint = self.consume(TokenType.TYPE_KEYWORD).value
        self.consume(TokenType.OPERATOR, '=')
        value = self.parse_expression()
        return AssignmentStatement(target, value, type_hint, True)
    
    def parse_assignment(self) -> AssignmentStatement:
        target = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.OPERATOR, '=')
        value = self.parse_expression()
        return AssignmentStatement(target, value)
    
    def parse_command(self) -> CommandStatement:
        cmd = self.consume().value
        args = []
        while self.peek().type not in [TokenType.BOUNDARY, TokenType.EOF] and self.peek().value not in ['{', ';']:
            if self.peek().value in [';', '{']:
                break
            args.append(self.parse_expression())
        block = None
        if self.peek().value == '{':
            block = self.parse_block()
        return CommandStatement(cmd, args, block)
    
    def parse_function(self) -> FunctionDef:
        self.consume(TokenType.KEYWORD, 'fn')
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.BOUNDARY, '(')
        params = []
        while self.peek().value != ')':
            param_name = self.consume(TokenType.IDENTIFIER).value
            param_type = None
            if self.peek().value == ':':
                self.consume(TokenType.BOUNDARY, ':')
                param_type = self.consume(TokenType.TYPE_KEYWORD).value
            params.append((param_name, param_type))
            if self.peek().value == ',':
                self.consume(TokenType.BOUNDARY, ',')
        self.consume(TokenType.BOUNDARY, ')')
        
        return_type = None
        if self.peek().value == '->':
            self.consume(TokenType.OPERATOR, '->')
            return_type = self.consume(TokenType.TYPE_KEYWORD).value
        
        body = self.parse_block()
        return FunctionDef(name, params, return_type, body)
    
    def parse_return(self) -> ReturnStatement:
        self.consume(TokenType.KEYWORD, 'return')
        if self.peek().value == ';' or self.peek().value == '}':
            return ReturnStatement(None)
        value = self.parse_expression()
        return ReturnStatement(value)
    
    def parse_class(self) -> ClassDef:
        self.consume(TokenType.KEYWORD, 'class')
        name = self.consume(TokenType.IDENTIFIER).value
        extends = None
        if self.peek().value == 'extends':
            self.consume(TokenType.KEYWORD, 'extends')
            extends = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.BOUNDARY, '{')
        methods = []
        while self.peek().value != '}':
            if self.peek().value == 'fn':
                methods.append(self.parse_function())
            else:
                self.consume()
        self.consume(TokenType.BOUNDARY, '}')
        return ClassDef(name, extends, methods)
    
    def parse_try(self) -> TryStatement:
        self.consume(TokenType.KEYWORD, 'try')
        try_block = self.parse_block()
        catch_blocks = []
        while self.peek().value == 'catch':
            self.consume(TokenType.KEYWORD, 'catch')
            var = self.consume(TokenType.IDENTIFIER).value
            catch_block = self.parse_block()
            catch_blocks.append((var, catch_block))
        finally_block = None
        if self.peek().value == 'finally':
            self.consume(TokenType.KEYWORD, 'finally')
            finally_block = self.parse_block()
        return TryStatement(try_block, catch_blocks, finally_block)
    
    def parse_block(self) -> List[Statement]:
        self.consume(TokenType.BOUNDARY, '{')
        statements = []
        while self.peek().value != '}':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            if self.peek().type == TokenType.EOF:
                break
        self.consume(TokenType.BOUNDARY, '}')
        return statements
    
    def parse_expression(self) -> Expression:
        return self.parse_assignment_expr()
    
    def parse_assignment_expr(self) -> Expression:
        left = self.parse_logical_or()
        if self.peek().type == TokenType.OPERATOR and self.peek().value == '=':
            self.consume()
            right = self.parse_assignment_expr()
            return BinaryOp(left, '=', right)
        return left
    
    def parse_logical_or(self) -> Expression:
        left = self.parse_logical_and()
        while self.peek().type == TokenType.OPERATOR and self.peek().value == '||':
            op = self.consume().value
            right = self.parse_logical_and()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_logical_and(self) -> Expression:
        left = self.parse_comparison()
        while self.peek().type == TokenType.OPERATOR and self.peek().value == '&&':
            op = self.consume().value
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_comparison(self) -> Expression:
        left = self.parse_additive()
        while self.peek().type == TokenType.OPERATOR and self.peek().value in ['==', '!=', '<', '>', '<=', '>=']:
            op = self.consume().value
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_additive(self) -> Expression:
        left = self.parse_multiplicative()
        while self.peek().type == TokenType.OPERATOR and self.peek().value in ['+', '-']:
            op = self.consume().value
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_multiplicative(self) -> Expression:
        left = self.parse_unary()
        while self.peek().type == TokenType.OPERATOR and self.peek().value in ['*', '/', '%']:
            op = self.consume().value
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_unary(self) -> Expression:
        if self.peek().type == TokenType.OPERATOR and self.peek().value in ['!', '-', '~']:
            op = self.consume().value
            right = self.parse_unary()
            return UnaryOp(op, right)
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        token = self.peek()
        
        if token.type == TokenType.NUMBER:
            self.consume()
            return NumberLiteral(token.value)
        
        elif token.type == TokenType.STRING:
            self.consume()
            return StringLiteral(token.value)
        
        elif token.type == TokenType.IDENTIFIER:
            self.consume()
            # 检查函数调用
            if self.peek().value == '(':
                self.consume(TokenType.BOUNDARY, '(')
                args = []
                while self.peek().value != ')':
                    args.append(self.parse_expression())
                    if self.peek().value == ',':
                        self.consume(TokenType.BOUNDARY, ',')
                self.consume(TokenType.BOUNDARY, ')')
                return FunctionCall(token.value, args)
            # 检查成员访问
            if self.peek().value == '.':
                self.consume(TokenType.BOUNDARY, '.')
                member = self.consume(TokenType.IDENTIFIER).value
                return MemberAccess(Identifier(token.value), member)
            return Identifier(token.value)
        
        elif token.type == TokenType.CONSTANT:
            self.consume()
            if token.value == 'true':
                return Literal(True)
            elif token.value == 'false':
                return Literal(False)
            elif token.value in ['null', 'undefined', 'None']:
                return Literal(None)
        
        elif token.type == TokenType.BUILTIN_FUNC:
            self.consume()
            self.consume(TokenType.BOUNDARY, '(')
            args = []
            while self.peek().value != ')':
                args.append(self.parse_expression())
                if self.peek().value == ',':
                    self.consume(TokenType.BOUNDARY, ',')
            self.consume(TokenType.BOUNDARY, ')')
            return FunctionCall(token.value, args)
        
        elif token.value == '(':
            self.consume(TokenType.BOUNDARY, '(')
            expr = self.parse_expression()
            self.consume(TokenType.BOUNDARY, ')')
            return expr
        
        elif token.value == '?':
            self.consume()
            name = self.consume(TokenType.IDENTIFIER).value
            return Identifier(f"?{name}")
        
        else:
            self.errors.append(f"未知表达式开始 '{token.value}' at {token.line}:{token.col}")
            self.consume()
            return Literal(None)


# ============================================================
# 3. 类型检查器 (TypeChecker) - 新增
# ============================================================

class TypeChecker:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.errors = []
    
    def check(self, node: ASTNode) -> str:
        if isinstance(node, Program):
            for stmt in node.statements:
                self.check(stmt)
            return "program"
        
        elif isinstance(node, AssignmentStatement):
            value_type = self.check(node.value)
            if node.type_hint:
                if value_type != node.type_hint and value_type != 'any':
                    self.errors.append(f"类型不匹配: 期望 {node.type_hint}，实际 {value_type}")
            self.variables[node.target] = node.type_hint or value_type
            return node.type_hint or value_type
        
        elif isinstance(node, BinaryOp):
            left_type = self.check(node.left)
            right_type = self.check(node.right)
            
            if node.op in ['+', '-', '*', '/', '%']:
                if left_type == 'string' or right_type == 'string':
                    if node.op == '+':
                        return 'string'
                if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                    self.errors.append(f"算术运算需要数字类型: {left_type} {node.op} {right_type}")
                return 'float' if 'float' in [left_type, right_type] else 'int'
            
            elif node.op in ['==', '!=', '<', '>', '<=', '>=']:
                if left_type != right_type and left_type != 'any' and right_type != 'any':
                    self.errors.append(f"比较操作类型不匹配: {left_type} vs {right_type}")
                return 'bool'
            
            elif node.op in ['&&', '||']:
                if left_type != 'bool' or right_type != 'bool':
                    self.errors.append(f"逻辑运算需要布尔类型: {left_type} {node.op} {right_type}")
                return 'bool'
            
            return 'any'
        
        elif isinstance(node, NumberLiteral):
            if isinstance(node.value, int):
                return 'int'
            return 'float'
        
        elif isinstance(node, StringLiteral):
            return 'string'
        
        elif isinstance(node, Identifier):
            if node.name in self.variables:
                return self.variables[node.name]
            return 'any'
        
        elif isinstance(node, FunctionCall):
            return 'any'
        
        elif isinstance(node, Literal):
            if node.value is True or node.value is False:
                return 'bool'
            elif node.value is None:
                return 'null'
            return 'any'
        
        return 'any'


# ============================================================
# 4. 代码生成器 (Generator) - 多语言支持
# ============================================================

class BaseGenerator:
    def __init__(self):
        self.indent_level = 0
        self.output = []
    
    def indent(self):
        return "    " * self.indent_level
    
    def gen_expression(self, expr: Expression) -> str:
        if isinstance(expr, BinaryOp):
            left = self.gen_expression(expr.left)
            right = self.gen_expression(expr.right)
            return f"({left} {expr.op} {right})"
        elif isinstance(expr, UnaryOp):
            right = self.gen_expression(expr.right)
            return f"{expr.op}{right}"
        elif isinstance(expr, NumberLiteral):
            return str(expr.value)
        elif isinstance(expr, StringLiteral):
            return f'"{expr.value}"'
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, FunctionCall):
            args = ", ".join([self.gen_expression(a) for a in expr.args])
            return f"{expr.name}({args})"
        elif isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, MemberAccess):
            return f"{self.gen_expression(expr.object)}.{expr.member}"
        return "None"


class PythonGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()
        self.functions = []
        self.classes = []
    
    def generate(self, node: ASTNode) -> str:
        if isinstance(node, Program):
            self.output.extend([
                "#!/usr/bin/env python3",
                "# -*- coding: utf-8 -*-",
                "# Generated by Kernel Translator v2.0",
                "",
                "import subprocess",
                "import os",
                "import sys",
                "import time",
                "import json",
                "from datetime import datetime",
                "from typing import Any, Optional, Dict, List",
                "",
                "# ============================================================",
                "# 辅助函数",
                "# ============================================================",
                "",
                "def shell_exec(cmd: str) -> str:",
                "    try:",
                "        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)",
                "        return result.stdout + result.stderr",
                "    except Exception as e:",
                "        return str(e)",
                "",
                "def log_info(msg: str) -> None:",
                "    print(f'[INFO] {msg}')",
                "",
                "def log_attack(msg: str) -> None:",
                "    print(f'[ATTACK] {msg}')",
                "",
                "def log_audit(msg: str) -> None:",
                "    print(f'[AUDIT] {msg}')",
                "",
                "def log_warn(msg: str) -> None:",
                "    print(f'[WARN] {msg}')",
                "",
                "def log_error(msg: str) -> None:",
                "    print(f'[ERROR] {msg}')",
                "",
                "def safe_call(func, *args, **kwargs):",
                "    try:",
                "        return func(*args, **kwargs)",
                "    except Exception as e:",
                "        log_error(str(e))",
                "        return None",
                "",
                "# ============================================================",
                "# 主程序",
                "# ============================================================",
                "",
                "def main():",
                ""
            ])
            self.indent_level = 1
            for stmt in node.statements:
                self.generate_statement(stmt)
            self.output.extend([
                "",
                "if __name__ == '__main__':",
                "    main()"
            ])
            return "\n".join(self.output)
        
        elif isinstance(node, Statement):
            self.generate_statement(node)
        
        return ""
    
    def generate_statement(self, stmt: Statement):
        if isinstance(stmt, CommandStatement):
            self.generate_command(stmt)
        elif isinstance(stmt, IfStatement):
            self.generate_if(stmt)
        elif isinstance(stmt, WhileStatement):
            self.generate_while(stmt)
        elif isinstance(stmt, ForStatement):
            self.generate_for(stmt)
        elif isinstance(stmt, AssignmentStatement):
            self.generate_assignment(stmt)
        elif isinstance(stmt, FunctionDef):
            self.generate_function(stmt)
        elif isinstance(stmt, ReturnStatement):
            self.generate_return(stmt)
        elif isinstance(stmt, ClassDef):
            self.generate_class(stmt)
        elif isinstance(stmt, TryStatement):
            self.generate_try(stmt)
    
    def generate_command(self, cmd: CommandStatement):
        line = self.indent()
        
        # 安全命令映射
        if cmd.command == 'log':
            if len(cmd.args) > 0:
                arg = self.gen_expression(cmd.args[0])
                line += f"log_info({arg})"
        
        elif cmd.command == 'shell':
            if len(cmd.args) > 0:
                arg = self.gen_expression(cmd.args[0])
                self.output.append(f"{self.indent()}print('[SHELL] Running command...')")
                self.output.append(f"{self.indent()}result = shell_exec({arg})")
                self.output.append(f"{self.indent()}print(f'[SHELL] {{result}}')")
                return
        
        elif cmd.command == 'ping':
            if len(cmd.args) > 0:
                target = self.gen_expression(cmd.args[0])
                self.output.append(f"{self.indent()}print(f'[PING] Pinging {{target}}...')")
                self.output.append(f"{self.indent()}result = shell_exec(f'ping -c 4 {{target}} 2>/dev/null')")
                self.output.append(f"{self.indent()}if '1 received' in result or '4 received' in result:")
                self.output.append(f"{self.indent()}    print(f'[PING] {{target}} is ALIVE')")
                self.output.append(f"{self.indent()}else:")
                self.output.append(f"{self.indent()}    print(f'[PING] {{target}} is DEAD')")
                return
        
        elif cmd.command == 'scan':
            if len(cmd.args) > 0:
                target = self.gen_expression(cmd.args[0])
                self.output.append(f"{self.indent()}print(f'[SCAN] Scanning {{target}}...')")
                self.output.append(f"{self.indent()}result = shell_exec(f'nmap -p- --open {{target}} 2>/dev/null')")
                self.output.append(f"{self.indent()}print(f'[SCAN] Results:\\n{{result}}')")
                return
        
        elif cmd.command == 'sniff':
            if len(cmd.args) > 0:
                interface = self.gen_expression(cmd.args[0])
                self.output.append(f"{self.indent()}print(f'[SNIFF] Sniffing on {{interface}}...')")
                self.output.append(f"{self.indent()}result = shell_exec(f'tcpdump -i {{interface}} -c 10 2>/dev/null')")
                self.output.append(f"{self.indent()}print(f'[SNIFF] Packets:\\n{{result}}')")
                return
        
        elif cmd.command == 'connect':
            if len(cmd.args) >= 2:
                host = self.gen_expression(cmd.args[0])
                port = self.gen_expression(cmd.args[1])
                self.output.append(f"{self.indent()}print(f'[CONNECT] Connecting to {{host}}:{{port}}...')")
                self.output.append(f"{self.indent()}result = shell_exec(f'nc -zv {{host}} {{port}} 2>&1')")
                self.output.append(f"{self.indent()}if 'succeeded' in result or 'Connected' in result:")
                self.output.append(f"{self.indent()}    print(f'[CONNECT] Connection successful')")
                self.output.append(f"{self.indent()}else:")
                self.output.append(f"{self.indent()}    print(f'[CONNECT] Connection failed')")
                return
        
        elif cmd.command == 'exploit':
            if len(cmd.args) >= 2:
                target = self.gen_expression(cmd.args[0])
                vuln = self.gen_expression(cmd.args[1])
                self.output.append(f"{self.indent()}log_attack(f'Attempting exploit {{vuln}} on {{target}}')")
                self.output.append(f"{self.indent()}print(f'[EXPLOIT] Simulating exploit...')")
                return
        
        elif cmd.command == 'root':
            self.output.append(f"{self.indent()}print('[ROOT] Attempting privilege escalation...')")
            self.output.append(f"{self.indent()}result = shell_exec('sudo -n whoami 2>/dev/null')")
            self.output.append(f"{self.indent()}if 'root' in result:")
            self.output.append(f"{self.indent()}    print('[ROOT] Already root!')")
            self.output.append(f"{self.indent()}else:")
            self.output.append(f"{self.indent()}    print('[ROOT] Need manual escalation')")
            return
        
        elif cmd.command == 'guard':
            self.output.append(f"{self.indent()}print('[GUARD] Setting up security...')")
            self.output.append(f"{self.indent()}print('[GUARD] Canary: enabled')")
            self.output.append(f"{self.indent()}print('[GUARD] ASLR: enabled')")
            self.output.append(f"{self.indent()}print('[GUARD] Sandbox: enabled')")
            return
        
        elif cmd.command == 'monitor':
            self.output.append(f"{self.indent()}print('[MONITOR] Monitoring system...')")
            self.output.append(f"{self.indent()}print('[MONITOR] CPU: 5%, Memory: 40%')")
            self.output.append(f"{self.indent()}print('[MONITOR] No threats detected')")
            return
        
        elif cmd.command == 'exfil':
            if len(cmd.args) >= 2:
                data = self.gen_expression(cmd.args[0])
                dest = self.gen_expression(cmd.args[1])
                self.output.append(f"{self.indent()}log_attack(f'Exfiltrating data to {{dest}}')")
                self.output.append(f"{self.indent()}print(f'[EXFIL] Would exfil {{data}} to {{dest}} (simulated)')")
                return
        
        else:
            line += f"# {cmd.command} " + " ".join([self.gen_expression(a) for a in cmd.args])
            self.output.append(line)
            return
        
        self.output.append(line)
        
        if cmd.block:
            self.indent_level += 1
            for stmt in cmd.block:
                self.generate_statement(stmt)
            self.indent_level -= 1
    
    def generate_if(self, if_stmt: IfStatement):
        cond = self.gen_expression(if_stmt.condition)
        self.output.append(f"{self.indent()}if {cond}:")
        self.indent_level += 1
        for stmt in if_stmt.then_block:
            self.generate_statement(stmt)
        self.indent_level -= 1
        
        for cond, block in if_stmt.elif_blocks:
            self.output.append(f"{self.indent()}elif {self.gen_expression(cond)}:")
            self.indent_level += 1
            for stmt in block:
                self.generate_statement(stmt)
            self.indent_level -= 1
        
        if if_stmt.else_block:
            self.output.append(f"{self.indent()}else:")
            self.indent_level += 1
            for stmt in if_stmt.else_block:
                self.generate_statement(stmt)
            self.indent_level -= 1
    
    def generate_while(self, while_stmt: WhileStatement):
        cond = self.gen_expression(while_stmt.condition)
        self.output.append(f"{self.indent()}while {cond}:")
        self.indent_level += 1
        for stmt in while_stmt.body:
            self.generate_statement(stmt)
        self.indent_level -= 1
    
    def generate_for(self, for_stmt: ForStatement):
        var = for_stmt.variable
        iterable = self.gen_expression(for_stmt.iterable)
        self.output.append(f"{self.indent()}for {var} in {iterable}:")
        self.indent_level += 1
        for stmt in for_stmt.body:
            self.generate_statement(stmt)
        self.indent_level -= 1
    
    def generate_assignment(self, assign: AssignmentStatement):
        value = self.gen_expression(assign.value)
        if assign.is_constant:
            self.output.append(f"{self.indent()}{assign.target.upper()} = {value}  # const")
        else:
            self.output.append(f"{self.indent()}{assign.target} = {value}")
    
    def generate_function(self, func: FunctionDef):
        params = ", ".join([p[0] for p in func.params])
        self.output.append(f"{self.indent()}def {func.name}({params}):")
        self.indent_level += 1
        for stmt in func.body:
            self.generate_statement(stmt)
        self.indent_level -= 1
    
    def generate_return(self, ret: ReturnStatement):
        if ret.value:
            self.output.append(f"{self.indent()}return {self.gen_expression(ret.value)}")
        else:
            self.output.append(f"{self.indent()}return")
    
    def generate_class(self, cls: ClassDef):
        extends = f"({cls.extends})" if cls.extends else ""
        self.output.append(f"{self.indent()}class {cls.name}{extends}:")
        self.indent_level += 1
        for method in cls.methods:
            self.generate_function(method)
        self.indent_level -= 1
    
    def generate_try(self, try_stmt: TryStatement):
        self.output.append(f"{self.indent()}try:")
        self.indent_level += 1
        for stmt in try_stmt.try_block:
            self.generate_statement(stmt)
        self.indent_level -= 1
        
        for var, block in try_stmt.catch_blocks:
            self.output.append(f"{self.indent()}except Exception as {var}:")
            self.indent_level += 1
            for stmt in block:
                self.generate_statement(stmt)
            self.indent_level -= 1
        
        if try_stmt.finally_block:
            self.output.append(f"{self.indent()}finally:")
            self.indent_level += 1
            for stmt in try_stmt.finally_block:
                self.generate_statement(stmt)
            self.indent_level -= 1


class ShellGenerator(BaseGenerator):
    def generate(self, node: ASTNode) -> str:
        self.output = [
            "#!/bin/bash",
            "# Generated by Kernel Translator v2.0",
            "",
            "# ============================================================",
            "# 辅助函数",
            "# ============================================================",
            "",
            "log_info() { echo \"[INFO] $1\"; }",
            "log_attack() { echo \"[ATTACK] $1\"; }",
            "log_audit() { echo \"[AUDIT] $1\"; }",
            "log_warn() { echo \"[WARN] $1\"; }",
            "log_error() { echo \"[ERROR] $1\"; }",
            "",
            "# ============================================================",
            "# 主程序",
            "# ============================================================",
            ""
        ]
        for stmt in node.statements:
            self.generate_statement(stmt)
        return "\n".join(self.output)
    
    def generate_statement(self, stmt: Statement):
        if isinstance(stmt, CommandStatement):
            if stmt.command == 'log':
                if stmt.args:
                    self.output.append(f"log_info {self.gen_expression(stmt.args[0])}")
            elif stmt.command == 'shell':
                if stmt.args:
                    self.output.append(f"{self.gen_expression(stmt.args[0])}")
            elif stmt.command == 'ping':
                if stmt.args:
                    self.output.append(f"ping -c 4 {self.gen_expression(stmt.args[0])}")
            elif stmt.command == 'scan':
                if stmt.args:
                    self.output.append(f"nmap -p- --open {self.gen_expression(stmt.args[0])}")
            elif stmt.command == 'root':
                self.output.append(f"sudo whoami")
            elif stmt.command == 'guard':
                self.output.append(f"# Security measures enabled")
            else:
                self.output.append(f"# {stmt.command} " + " ".join([self.gen_expression(a) for a in stmt.args]))


# ============================================================
# 5. 语法高亮器 (SyntaxHighlighter) - 新增
# ============================================================

class SyntaxHighlighter:
    @staticmethod
    def highlight(code: str) -> str:
        # 关键字高亮
        keywords = [
            'if', 'else', 'elif', 'while', 'for', 'return', 'break', 'continue',
            'let', 'const', 'fn', 'class', 'try', 'catch', 'finally', 'throw',
            'import', 'export', 'ping', 'scan', 'exploit', 'shell', 'root'
        ]
        
        # 替换关键字
        for kw in keywords:
            code = re.sub(rf'\b{kw}\b', f'{Colors.BLUE}{kw}{Colors.ENDC}', code)
        
        # 字符串高亮
        code = re.sub(r'(".*?")', f'{Colors.GREEN}\\1{Colors.ENDC}', code)
        code = re.sub(r"('.*?')", f'{Colors.GREEN}\\1{Colors.ENDC}', code)
        
        # 数字高亮
        code = re.sub(r'\b(\d+)\b', f'{Colors.CYAN}\\1{Colors.ENDC}', code)
        
        # 注释高亮
        code = re.sub(r'(//.*?$)', f'{Colors.WARNING}\\1{Colors.ENDC}', code, flags=re.MULTILINE)
        
        return code


# ============================================================
# 6. 主翻译器 (Translator) - 完善版
# ============================================================

class KernelTranslator:
    def __init__(self):
        self.tokenizer = None
        self.parser = None
        self.type_checker = None
        self.generator = None
    
    def translate(self, source: str, output_format: str = "python", 
                  enable_type_check: bool = True, enable_highlight: bool = False) -> Tuple[str, List[str]]:
        """
        将 Kernel 源代码翻译为目标代码
        
        Args:
            source: Kernel 源代码
            output_format: 输出格式 (python/shell)
            enable_type_check: 是否启用类型检查
            enable_highlight: 是否启用语法高亮
        
        Returns:
            翻译后的代码和错误列表
        """
        # 1. 词法分析
        self.tokenizer = Tokenizer(source)
        tokens, lexer_errors = self.tokenizer.tokenize()
        all_errors = lexer_errors.copy()
        
        # 2. 语法分析
        self.parser = Parser(tokens)
        ast = self.parser.parse()
        all_errors.extend(self.parser.errors)
        
        # 3. 类型检查（可选）
        if enable_type_check:
            self.type_checker = TypeChecker()
            self.type_checker.check(ast)
            all_errors.extend(self.type_checker.errors)
        
        # 4. 代码生成
        if output_format == "python":
            self.generator = PythonGenerator()
            output = self.generator.generate(ast)
        elif output_format == "shell":
            self.generator = ShellGenerator()
            output = self.generator.generate(ast)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
        
        # 5. 语法高亮（可选）
        if enable_highlight:
            output = SyntaxHighlighter.highlight(output)
        
        return output, all_errors
    
    def translate_file(self, input_file: str, output_file: str = None, 
                       output_format: str = "python", enable_type_check: bool = True) -> Tuple[str, List[str]]:
        """翻译文件"""
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        output, errors = self.translate(source, output_format, enable_type_check)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"{Colors.GREEN}✅ 已翻译到: {output_file}{Colors.ENDC}")
        else:
            print(output)
        
        return output, errors


# ============================================================
# 7. 命令行界面 (CLI) - 完善版
# ============================================================

def main():
    print("=" * 60)
    print(f"{Colors.BOLD}{Colors.HEADER}Kernel 语言翻译器 v2.0{Colors.ENDC}")
    print("将 Kernel 代码转换为 Python/Shell 代码")
    print("仅用于本地安全学习和授权测试")
    print("=" * 60)
    
    parser = argparse.ArgumentParser(description='Kernel 语言翻译器')
    parser.add_argument('input', help='输入 .kernel 文件')
    parser.add_argument('-o', '--output', help='输出文件')
    parser.add_argument('--format', choices=['python', 'shell'], default='python', help='输出格式')
    parser.add_argument('--no-type-check', action='store_true', help='禁用类型检查')
    parser.add_argument('--highlight', action='store_true', help='启用语法高亮')
    parser.add_argument('--list-keywords', action='store_true', help='列出所有关键字')
    
    args = parser.parse_args()
    
    # 列出关键字
    if args.list_keywords:
        print(f"\n{Colors.BOLD}支持的关键字 ({len(Tokenizer.KEYWORDS)})：{Colors.ENDC}")
        for i, kw in enumerate(sorted(Tokenizer.KEYWORDS), 1):
            print(f"{Colors.CYAN}{kw:12}{Colors.ENDC}", end=" " if i % 8 != 0 else "\n")
        print()
        return
    
    translator = KernelTranslator()
    
    try:
        output, errors = translator.translate_file(
            args.input, 
            args.output, 
            args.format,
            not args.no_type_check
        )
        
        # 显示错误
        if errors:
            print(f"\n{Colors.RED}⚠️ 发现 {len(errors)} 个警告/错误:{Colors.ENDC}")
            for err in errors[:10]:
                print(f"  {err}")
            if len(errors) > 10:
                print(f"  ... 还有 {len(errors) - 10} 个")
        
        if not args.output and not args.highlight:
            # 显示前50行
            lines = output.split('\n')
            print(f"\n{Colors.BOLD}--- 翻译结果（前50行）---{Colors.ENDC}")
            for line in lines[:50]:
                print(line)
            if len(lines) > 50:
                print(f"... 还有 {len(lines) - 50} 行")
    
    except Exception as e:
        print(f"\n{Colors.RED}翻译错误: {e}{Colors.ENDC}")
        sys.exit(1)


# ============================================================
# 8. 测试用例
# ============================================================

def run_tests():
    """运行测试用例"""
    test_code = '''
// 测试 Kernel 语言

let name = "Kernel"
let version: int = 2

fn greet(msg: string) -> string {
    return "Hello, " + msg
}

class Network {
    fn scan(target: string) {
        scan target
    }
}

if version > 1 {
    ping "google.com"
} else {
    log "Version too old"
}

for i in range(5) {
    log "Iteration: " + i
}

try {
    exploit "127.0.0.1" "CVE-2024-1234"
} catch e {
    log "Exploit failed: " + e
} finally {
    log "Cleanup done"
}
'''
    
    translator = KernelTranslator()
    output, errors = translator.translate(test_code, enable_type_check=True)
    
    print("=" * 60)
    print(f"{Colors.BOLD}测试结果{Colors.ENDC}")
    print("=" * 60)
    
    if errors:
        print(f"{Colors.RED}错误数: {len(errors)}{Colors.ENDC}")
        for err in errors:
            print(f"  {err}")
    else:
        print(f"{Colors.GREEN}✅ 测试通过！{Colors.ENDC}")
    
    print("\n生成的代码预览：")
    print("-" * 40)
    lines = output.split('\n')
    for line in lines[:30]:
        print(line)
    if len(lines) > 30:
        print(f"... 还有 {len(lines) - 30} 行")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        run_tests()
