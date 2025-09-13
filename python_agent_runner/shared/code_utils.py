import ast

def _add_parent_references(tree):
    """Helper to add a .parent attribute to each node in the AST."""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

def summarize_python_code(source_code: str) -> str:
    """
    Parses Python source code using AST and returns a structural summary.

    Args:
        source_code (str): The Python code to analyze.

    Returns:
        str: A formatted string summarizing the code's structure.
    """
    summary = []
    try:
        tree = ast.parse(source_code)
        _add_parent_references(tree)
        
        imports = []
        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or '.'
                names = ", ".join(alias.name for alias in node.names)
                imports.append(f"from {module} import {names}")
            elif isinstance(node, ast.FunctionDef) and isinstance(node.parent, ast.Module):
                # Top-level functions only (parent is the main module)
                args = ", ".join(arg.arg for arg in node.args.args)
                functions.append(f"def {node.name}({args})")
            elif isinstance(node, ast.ClassDef):
                bases = ", ".join(base.id for base in node.bases if isinstance(base, ast.Name))
                class_summary = f"class {node.name}({bases}):"
                methods = [
                    f"  - def {item.name}({', '.join(arg.arg for arg in item.args.args)})"
                    for item in node.body if isinstance(item, ast.FunctionDef)
                ]
                classes.append((class_summary, methods))

        if imports:
            summary.append("IMPORTS:")
            summary.extend([f"  - {i}" for i in sorted(list(set(imports)))])
        
        if functions:
            summary.append("FUNCTIONS:")
            summary.extend([f"  - {f}" for f in functions])

        if classes:
            summary.append("CLASSES:")
            for class_summary, methods in classes:
                summary.append(f"  - {class_summary}")
                summary.extend(methods)

        return "\n".join(summary)
    except Exception:
        return "Could not parse code to generate a summary."
