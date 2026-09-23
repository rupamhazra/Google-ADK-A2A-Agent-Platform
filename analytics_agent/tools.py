import ast
import operator

_ALLOWED_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY:
        return _ALLOWED_BINARY[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_evaluate(node.operand))
    raise ValueError("Only numeric arithmetic expressions are allowed")


def calculator(expression: str) -> dict:
    """Safely evaluates a numeric arithmetic expression."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree)
        return {"status": "success", "expression": expression, "result": result}
    except Exception as exc:
        return {"status": "error", "expression": expression, "error": str(exc)}
