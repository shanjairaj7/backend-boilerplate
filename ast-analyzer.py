#!/usr/bin/env python3
"""
Advanced AST Code Analyzer for FastAPI/React Projects
Provides structural analysis to help models understand and fix code issues
"""

import ast
import json
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional, Union

class CodeAnalyzer:
    """Advanced AST-based code analyzer for structural understanding"""
    
    def __init__(self, project_path: str, target: str = "backend"):
        self.project_path = Path(project_path)
        self.target = target  # "backend" or "frontend"
        self.reset_state()
    
    def reset_state(self):
        """Reset analysis state"""
        self.routes = []
        self.imports = []
        self.env_vars_used = []
        self.db_usage = []
        self.errors = []
        self.functions = []
        self.classes = []
        self.issues = []
        self.file_analysis = {}
        
    def analyze_project(self, focus: str = "all") -> dict:
        """
        Analyze project structure and return detailed results
        
        Args:
            focus: "routes", "imports", "env", "database", "structure", "all"
            
        Returns:
            Dictionary with analysis results and actionable insights
        """
        
        print(f"🔍 AST Analysis: {self.target} project at {self.project_path}")
        print(f"🎯 Focus: {focus}")
        
        if not self.project_path.exists():
            return {"error": f"Path not found: {self.project_path}"}
        
        # Find relevant files based on target
        if self.target == "backend":
            files = self._find_python_files()
        elif self.target == "frontend":
            files = self._find_frontend_files()
        else:
            return {"error": f"Unsupported target: {self.target}"}
        
        print(f"📁 Found {len(files)} files to analyze")
        
        # Analyze each file
        for file_path in files:
            self._analyze_file(file_path, focus)
        
        # Generate comprehensive report
        results = self._generate_report(focus)
        
        # Add actionable insights
        results["insights"] = self._generate_insights(focus)
        results["recommendations"] = self._generate_recommendations()
        
        return results
    
    def _find_python_files(self) -> List[Path]:
        """Find Python files for backend analysis"""
        files = []
        for pattern in ["*.py"]:
            files.extend(self.project_path.rglob(pattern))
        
        # Filter out unwanted directories
        return [f for f in files if not any(part in str(f) for part in [
            '__pycache__', '.venv', 'venv', 'node_modules', '.git'
        ])]
    
    def _find_frontend_files(self) -> List[Path]:
        """Find frontend files for React/TypeScript analysis"""
        files = []
        for pattern in ["*.tsx", "*.ts", "*.jsx", "*.js"]:
            files.extend(self.project_path.rglob(pattern))
        
        # Filter out unwanted directories
        return [f for f in files if not any(part in str(f) for part in [
            'node_modules', '.git', 'dist', 'build', '.next'
        ])]
    
    def _analyze_file(self, file_path: Path, focus: str):
        """Analyze a single file using AST"""
        if self.target == "backend":
            self._analyze_python_file(file_path, focus)
        elif self.target == "frontend":
            self._analyze_frontend_file(file_path, focus)
    
    def _analyze_python_file(self, file_path: Path, focus: str):
        """Analyze Python file with AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            file_info = {
                'path': str(file_path.relative_to(self.project_path)),
                'size': len(content),
                'lines': len(content.split('\\n')),
                'routes': [],
                'imports': [],
                'functions': [],
                'classes': [],
                'env_usage': [],
                'db_usage': [],
                'issues': []
            }
            
            # Walk through all AST nodes
            for node in ast.walk(tree):
                self._analyze_python_node(node, file_path, file_info, focus)
            
            self.file_analysis[str(file_path)] = file_info
            
        except SyntaxError as e:
            error_info = {
                'type': 'syntax_error',
                'file': str(file_path.relative_to(self.project_path)),
                'line': e.lineno,
                'message': e.msg,
                'severity': 'critical'
            }
            self.errors.append(error_info)
            file_info['issues'].append(error_info)
            
        except Exception as e:
            error_info = {
                'type': 'analysis_error', 
                'file': str(file_path.relative_to(self.project_path)),
                'message': str(e),
                'severity': 'warning'
            }
            self.errors.append(error_info)
    
    def _analyze_python_node(self, node, file_path: Path, file_info: dict, focus: str):
        """Analyze individual Python AST nodes"""
        
        # Route analysis (FastAPI specific)
        if focus in ["routes", "all"] and isinstance(node, ast.FunctionDef):
            route_info = self._extract_route_info(node, file_path)
            if route_info:
                self.routes.append(route_info)
                file_info['routes'].append(route_info)
        
        # Import analysis
        if focus in ["imports", "all"]:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info = {'type': 'import', 'module': alias.name, 'file': str(file_path)}
                    self.imports.append(import_info)
                    file_info['imports'].append(import_info)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    import_info = {'type': 'from_import', 'module': module, 'name': alias.name, 'file': str(file_path)}
                    self.imports.append(import_info)
                    file_info['imports'].append(import_info)
        
        # Environment variable analysis
        if focus in ["env", "all"]:
            env_usage = self._detect_env_usage(node, file_path)
            if env_usage:
                self.env_vars_used.append(env_usage)
                file_info['env_usage'].append(env_usage)
        
        # Database usage analysis
        if focus in ["database", "all"]:
            db_usage = self._detect_db_usage(node, file_path)
            if db_usage:
                self.db_usage.append(db_usage)
                file_info['db_usage'].append(db_usage)
        
        # Function analysis
        if focus in ["structure", "all"] and isinstance(node, ast.FunctionDef):
            func_info = {
                'name': node.name,
                'args': [arg.arg for arg in node.args.args],
                'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node)),
                'is_async': isinstance(node, ast.AsyncFunctionDef),
                'decorators': len(node.decorator_list),
                'file': str(file_path)
            }
            self.functions.append(func_info)
            file_info['functions'].append(func_info)
        
        # Class analysis
        if focus in ["structure", "all"] and isinstance(node, ast.ClassDef):
            class_info = {
                'name': node.name,
                'methods': [],
                'file': str(file_path)
            }
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_info['methods'].append(item.name)
            self.classes.append(class_info)
            file_info['classes'].append(class_info)
    
    def _extract_route_info(self, func_node, file_path):
        """Extract FastAPI route information"""
        route_info = None
        
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    path = None
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value
                    
                    route_info = {
                        'method': decorator.func.attr.upper(),
                        'path': path,
                        'function': func_node.name,
                        'has_return': any(isinstance(node, ast.Return) for node in ast.walk(func_node)),
                        'params': [arg.arg for arg in func_node.args.args],
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': func_node.lineno
                    }
                    break
        
        return route_info
    
    def _detect_env_usage(self, node, file_path):
        """Detect environment variable usage"""
        # os.environ['VAR'] pattern
        if isinstance(node, ast.Subscript):
            if (isinstance(node.value, ast.Attribute) and 
                isinstance(node.value.value, ast.Name) and 
                node.value.value.id == 'os' and 
                node.value.attr == 'environ'):
                if isinstance(node.slice, ast.Constant):
                    return {
                        'variable': node.slice.value,
                        'type': 'direct_access',
                        'file': str(file_path.relative_to(self.project_path))
                    }
        
        # os.environ.get('VAR') pattern
        if isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Attribute) and 
                isinstance(node.func.value, ast.Attribute) and 
                isinstance(node.func.value.value, ast.Name) and 
                node.func.value.value.id == 'os' and 
                node.func.value.attr == 'environ' and 
                node.func.attr == 'get'):
                if node.args and isinstance(node.args[0], ast.Constant):
                    return {
                        'variable': node.args[0].value,
                        'type': 'get_method',
                        'file': str(file_path.relative_to(self.project_path))
                    }
        
        return None
    
    def _detect_db_usage(self, node, file_path):
        """Detect database usage patterns"""
        if isinstance(node, ast.Name):
            if node.id.lower() in ['db', 'database', 'session', 'engine', 'connection']:
                return {
                    'variable': node.id,
                    'context': type(node.ctx).__name__,
                    'file': str(file_path.relative_to(self.project_path))
                }
        return None
    
    def _analyze_frontend_file(self, file_path: Path, focus: str):
        """Analyze frontend TypeScript/JavaScript files (basic implementation)"""
        # This would need a TypeScript/JavaScript AST parser
        # For now, we'll do basic text analysis
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                'path': str(file_path.relative_to(self.project_path)),
                'size': len(content),
                'lines': len(content.split('\\n')),
                'is_component': 'export default' in content or 'export const' in content,
                'has_hooks': any(hook in content for hook in ['useState', 'useEffect', 'useContext']),
                'imports': self._extract_frontend_imports(content),
                'issues': []
            }
            
            self.file_analysis[str(file_path)] = file_info
            
        except Exception as e:
            self.errors.append({
                'type': 'frontend_analysis_error',
                'file': str(file_path.relative_to(self.project_path)),
                'message': str(e)
            })
    
    def _extract_frontend_imports(self, content: str) -> List[dict]:
        """Extract import statements from frontend files (basic regex-based)"""
        import re
        imports = []
        
        # Match import statements
        import_pattern = r"import\\s+(?:{[^}]+}|[^\\s]+)\\s+from\\s+['\"]([^'\"]+)['\"]"
        matches = re.findall(import_pattern, content)
        
        for match in matches:
            imports.append({'module': match, 'type': 'es6_import'})
        
        return imports
    
    def _generate_report(self, focus: str) -> dict:
        """Generate comprehensive analysis report"""
        return {
            'target': self.target,
            'focus': focus,
            'summary': {
                'files_analyzed': len(self.file_analysis),
                'total_routes': len(self.routes),
                'total_functions': len(self.functions),
                'total_classes': len(self.classes),
                'total_imports': len(self.imports),
                'env_vars_used': len(self.env_vars_used),
                'db_usage_count': len(self.db_usage),
                'errors_found': len(self.errors)
            },
            'routes': self.routes,
            'functions': self.functions,
            'classes': self.classes,
            'imports': self.imports,
            'env_vars': self.env_vars_used,
            'database_usage': self.db_usage,
            'errors': self.errors,
            'files': self.file_analysis
        }
    
    def _generate_insights(self, focus: str) -> List[str]:
        """Generate actionable insights from analysis"""
        insights = []
        
        # Route insights
        if focus in ["routes", "all"]:
            broken_routes = [r for r in self.routes if not r['has_return']]
            if broken_routes:
                insights.append(f"⚠️ Found {len(broken_routes)} routes without return statements")
            
            if not any(r['path'] in ['/health', '/ping'] for r in self.routes):
                insights.append("📋 Consider adding a health check endpoint (/health)")
        
        # Environment insights
        if focus in ["env", "all"]:
            if self.env_vars_used and not any('load_dotenv' in str(imp) for imp in self.imports):
                insights.append("🌍 Environment variables used but load_dotenv not imported")
        
        # Database insights
        if focus in ["database", "all"]:
            if self.db_usage and not any(any(db in str(imp) for db in ['sqlalchemy', 'sqlite', 'mongo']) for imp in self.imports):
                insights.append("🗄️ Database usage detected but no database library imports found")
        
        # Structure insights
        if focus in ["structure", "all"]:
            undecorated_functions = []
            for func in self.functions:
                if func['name'].endswith('_endpoint') and func['decorators'] == 0:
                    undecorated_functions.append(func['name'])
            
            if undecorated_functions:
                insights.append(f"🔧 Functions that might need route decorators: {', '.join(undecorated_functions)}")
        
        return insights
    
    def _generate_recommendations(self) -> List[dict]:
        """Generate specific fix recommendations"""
        recommendations = []
        
        for error in self.errors:
            if error['type'] == 'syntax_error':
                recommendations.append({
                    'type': 'fix_syntax',
                    'priority': 'critical',
                    'file': error['file'],
                    'line': error.get('line'),
                    'description': f"Fix syntax error: {error['message']}",
                    'action': 'Read the file and fix the syntax issue'
                })
        
        # Route without return recommendations
        broken_routes = [r for r in self.routes if not r['has_return']]
        for route in broken_routes:
            recommendations.append({
                'type': 'add_return',
                'priority': 'high',
                'file': route['file'],
                'function': route['function'],
                'description': f"Add return statement to {route['method']} {route['path']}",
                'action': f"Update {route['function']} to return appropriate response"
            })
        
        # Environment variable recommendations
        if self.env_vars_used and not any('load_dotenv' in str(imp) for imp in self.imports):
            recommendations.append({
                'type': 'add_dotenv',
                'priority': 'medium',
                'description': "Add dotenv import and load_dotenv() call",
                'action': "Add 'from dotenv import load_dotenv' and call load_dotenv() before using environment variables"
            })
        
        return recommendations

def main():
    """Main entry point for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python ast-analyzer.py <project_path> [target] [focus]")
        print("  target: backend|frontend (default: backend)")
        print("  focus: routes|imports|env|database|structure|all (default: all)")
        sys.exit(1)
    
    project_path = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "backend"
    focus = sys.argv[3] if len(sys.argv) > 3 else "all"
    
    analyzer = CodeAnalyzer(project_path, target)
    results = analyzer.analyze_project(focus)
    
    # Pretty print results
    print("\\n" + "="*80)
    print("📊 AST ANALYSIS RESULTS")
    print("="*80)
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    main()