"""Real compile, syntax-policy and acceptance checks for the bundled demo."""
import ast
import json
import subprocess
import sys

ALLOWED = {
    ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Return,
    ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare, ast.Name, ast.Load,
    ast.Constant, ast.And, ast.Or, ast.Not, ast.USub, ast.Add, ast.Sub,
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq,
}

WORKER = '''import json, sys
source, cases = json.load(sys.stdin)
scope = {"__builtins__": {}}
exec(compile(source, "booking_policy.py", "exec"), scope)
results = []
for case in cases:
    try:
        actual = scope["can_book"](*case["args"])
        passed = type(actual) is bool and actual == case["expected"]
        results.append({"id": case["id"], "passed": passed, "actual": actual})
    except Exception as exc:
        results.append({"id": case["id"], "passed": False, "error": type(exc).__name__})
print(json.dumps(results))
'''


def verify(source, spec):
    """Return structured gates. Only a deliberately tiny Python subset is accepted."""
    gates = []
    try:
        tree = ast.parse(source)
        compile(tree, 'booking_policy.py', 'exec')
    except (SyntaxError, ValueError) as exc:
        return [{'gate': 'compile', 'passed': False, 'detail': str(exc)}]
    gates.append({'gate': 'compile', 'passed': True})
    allowed = all(type(node) in ALLOWED for node in ast.walk(tree))
    function = tree.body[0] if len(tree.body) == 1 else None
    allowed = allowed and isinstance(function, ast.FunctionDef)
    if allowed:
        allowed = (function.name == 'can_book' and not function.decorator_list
                   and not function.args.defaults and not function.args.kw_defaults
                   and not function.args.kwonlyargs and not function.args.posonlyargs
                   and function.args.vararg is None and function.args.kwarg is None
                   and [a.arg for a in function.args.args] == ['capacity', 'booked', 'requested']
                   and len(function.body) == 1 and isinstance(function.body[0], ast.Return)
                   and all(node.id in {'capacity', 'booked', 'requested'}
                           for node in ast.walk(tree) if isinstance(node, ast.Name)))
    gates.append({'gate': 'restricted_syntax', 'passed': bool(allowed)})
    if not allowed:
        return gates
    try:
        proc = subprocess.run(
            [sys.executable, '-I', '-c', WORKER],
            input=json.dumps([source, spec['acceptance']]), text=True,
            capture_output=True, timeout=5, check=True,
        )
        results = json.loads(proc.stdout)
    except (subprocess.SubprocessError, ValueError) as exc:
        gates.append({'gate': 'acceptance', 'passed': False, 'detail': type(exc).__name__})
        return gates
    gates.append({'gate': 'acceptance', 'passed': all(c['passed'] for c in results), 'cases': results})
    return gates
