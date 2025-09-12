# python_agent_runner/agents/ontology_agent.py
import ast
import os

class OntologyAgent:
    def analyze_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as source_file:
                tree = ast.parse(source_file.read())
            imports = sorted({node.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)})
            classes = sorted([node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            functions = sorted([node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            return {"imports": imports, "classes": classes, "functions": functions}
        except Exception:
            return None

    def analyze_directory(self, dir_path):
        summary = {
            "files_analyzed": 0,
            "all_classes": set(),
            "all_functions": set(),
            "entity_map": {}
        }
        try:
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        entities = self.analyze_file(file_path)
                        if entities:
                            summary["files_analyzed"] += 1
                            for cls in entities.get("classes", []):
                                summary["all_classes"].add(cls)
                                summary["entity_map"][cls] = file_path
                            for func in entities.get("functions", []):
                                summary["all_functions"].add(func)
                                summary["entity_map"][func] = file_path
            summary["all_classes"] = sorted(list(summary["all_classes"]))
            summary["all_functions"] = sorted(list(summary["all_functions"]))
            return {"status": "Success", "summary": summary}
        except Exception as e:
            return {"status": f"Error: {e}", "summary": {}}

    def get_entity_details(self, file_path, entity_name):
        try:
            with open(file_path, 'r', encoding='utf-8') as source_file:
                tree = ast.parse(source_file.read())
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == entity_name:
                    details = {"name": node.name, "type": type(node).__name__, "docstring": ast.get_docstring(node) or "No description provided."}
                    if isinstance(node, ast.ClassDef):
                        details["methods"] = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    return {"status": "Success", "details": details}
            return {"status": f"Entity '{entity_name}' not found."}
        except Exception as e:
            return {"status": f"Error analyzing file: {e}"}
