"""
atlas_core_new/core/agent/tools.py

Tool capabilities for AI personas: web search, calculator, code execution.
"""

import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    result: Any
    error: Optional[str] = None


class Calculator:
    """Safe mathematical calculator using AST parsing."""
    
    SAFE_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'pow': pow,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'floor': math.floor,
        'ceil': math.ceil,
    }
    
    SAFE_CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
    }

    def calculate(self, expression: str) -> ToolResult:
        """Safely evaluate a mathematical expression using AST."""
        import ast
        
        try:
            if not expression or not expression.strip():
                return ToolResult(success=False, result=None, error="Empty expression")
            
            if len(expression) > 200:
                return ToolResult(success=False, result=None, error="Expression too long")
            
            tree = ast.parse(expression, mode='eval')
            result = self._eval_node(tree.body)
            return ToolResult(success=True, result=result)
        except ValueError as e:
            return ToolResult(success=False, result=None, error=str(e))
        except SyntaxError:
            return ToolResult(success=False, result=None, error="Invalid expression syntax")
        except Exception as e:
            return ToolResult(success=False, result=None, error=f"Calculation error: {str(e)}")
    
    def _eval_node(self, node):
        """Recursively evaluate AST nodes."""
        import ast
        
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        
        elif isinstance(node, ast.Name):
            if node.id in self.SAFE_CONSTANTS:
                return self.SAFE_CONSTANTS[node.id]
            raise ValueError(f"Unknown variable: {node.id}")
        
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            ops = {
                ast.Add: lambda a, b: a + b,
                ast.Sub: lambda a, b: a - b,
                ast.Mult: lambda a, b: a * b,
                ast.Div: lambda a, b: a / b,
                ast.Pow: lambda a, b: a ** b,
                ast.Mod: lambda a, b: a % b,
                ast.FloorDiv: lambda a, b: a // b,
            }
            op_type = type(node.op)
            if op_type not in ops:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            return ops[op_type](left, right)
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return +operand
            raise ValueError(f"Unsupported unary operator")
        
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.SAFE_FUNCTIONS:
                args = [self._eval_node(arg) for arg in node.args]
                return self.SAFE_FUNCTIONS[node.func.id](*args)
            raise ValueError(f"Unknown function: {getattr(node.func, 'id', 'unknown')}")
        
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")


class CodeRunner:
    """
    Safe Python code execution for educational purposes.
    NOTE: This is disabled for security. Use the code explainer instead.
    """
    
    ENABLED = False
    
    def execute(self, code: str) -> ToolResult:
        """Code execution is disabled for security. Returns explanation instead."""
        if not self.ENABLED:
            return ToolResult(
                success=False,
                result=None,
                error="Code execution is disabled for security. Use the AI personas to explain code concepts instead."
            )
        return ToolResult(success=False, result=None, error="Not implemented")


class WebSearchSimulator:
    """
    Web search tool. In production, this would connect to a real search API.
    For now, provides educational responses based on known topics.
    """
    
    def search(self, query: str) -> ToolResult:
        """Simulate a web search for educational content."""
        return ToolResult(
            success=True,
            result={
                "query": query,
                "note": "Web search is available. The AI will use its knowledge to provide relevant information.",
                "status": "AI knowledge base used"
            }
        )


class ToolRegistry:
    """Registry and executor for all available tools."""
    
    def __init__(self):
        self.calculator = Calculator()
        self.code_runner = CodeRunner()
        self.web_search = WebSearchSimulator()
        
        self.tools = {
            "calculate": {
                "name": "Calculator",
                "description": "Perform mathematical calculations",
                "handler": self._handle_calculate
            },
            "run_code": {
                "name": "Code Runner",
                "description": "Execute Python code for learning",
                "handler": self._handle_code
            },
            "search": {
                "name": "Web Search",
                "description": "Search for information",
                "handler": self._handle_search
            }
        }

    def list_tools(self) -> List[dict]:
        """List available tools."""
        return [
            {"id": k, "name": v["name"], "description": v["description"]}
            for k, v in self.tools.items()
        ]

    def execute(self, tool_id: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a tool with given parameters."""
        if tool_id not in self.tools:
            return ToolResult(success=False, result=None, error=f"Unknown tool: {tool_id}")
        
        return self.tools[tool_id]["handler"](params)

    def _handle_calculate(self, params: Dict[str, Any]) -> ToolResult:
        expression = params.get("expression", "")
        return self.calculator.calculate(expression)

    def _handle_code(self, params: Dict[str, Any]) -> ToolResult:
        code = params.get("code", "")
        return self.code_runner.execute(code)

    def _handle_search(self, params: Dict[str, Any]) -> ToolResult:
        query = params.get("query", "")
        return self.web_search.search(query)


tool_registry = ToolRegistry()
