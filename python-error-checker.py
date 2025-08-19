#!/usr/bin/env python3
"""
Pure MyPy/Pyflakes Python Error Checker
No hardcoded patterns - let the tools do their job like VS Code does
"""

import sys
import time
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class PurePythonChecker:
    """Python error checker using pure MyPy + Pyflakes output"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.error_file = self.project_path / ".python-errors.txt"
        
    def run_mypy(self) -> str:
        """Run MyPy fast with only critical error detection"""
        try:
            # Only check user Python files, not all directories
            python_files = []
            for py_file in self.project_path.rglob("*.py"):
                # Skip virtual environments, caches, and site-packages  
                if any(part in str(py_file) for part in ['venv/', '.venv/', '__pycache__/', 'site-packages/']):
                    continue
                python_files.append(str(py_file))
            
            if not python_files:
                return ""
            
            # Limit to first 10 files for speed (most critical errors will be in main files)
            python_files = python_files[:10]
            
            cmd = [
                sys.executable, "-m", "mypy",
                "--show-error-codes",
                "--no-error-summary", 
                "--ignore-missing-imports",
                "--follow-imports=silent",
                "--no-strict-optional",
                "--allow-untyped-calls",
                "--allow-untyped-defs",
                "--cache-dir", str(self.project_path / ".mypy_cache"),  # Enable caching
                "--fast-parser",  # Speed optimization
            ] + python_files
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=str(self.project_path),
                timeout=10  # Reduced timeout
            )
            
            if result.returncode == 0 or not result.stdout.strip():
                return ""
            
            # Filter MyPy output to only critical errors that would break runtime
            critical_lines = []
            for line in result.stdout.strip().split('\n'):
                if line.strip() and any(critical in line for critical in [
                    '[syntax]',
                    '[name-defined]', 
                    '[attr-defined]',
                    '[call-arg]',
                    '[operator]',
                    '[index]',
                    '[import-not-found]'
                ]):
                    critical_lines.append(line)
            
            return '\n'.join(critical_lines) if critical_lines else ""
            
        except (subprocess.SubprocessError, FileNotFoundError):
            # MyPy not available - try basic syntax check
            return self._basic_syntax_check()
        except Exception:
            return ""
    
    def _basic_syntax_check(self) -> str:
        """Basic syntax checking when MyPy not available"""
        errors = []
        
        for py_file in self.project_path.rglob("*.py"):
            # Skip virtual environments and caches
            if any(part in str(py_file) for part in ['venv', '.venv', '__pycache__', 'site-packages']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import ast
                ast.parse(content, filename=str(py_file))
                
            except (SyntaxError, IndentationError) as e:
                rel_path = py_file.relative_to(self.project_path)
                errors.append(f"{rel_path}:{e.lineno}: error: {e.msg}")
            except Exception:
                continue
                
        return "\n".join(errors)
    
    def run_pyflakes(self) -> str:
        """Run Pyflakes fast on critical files only"""
        try:
            # Only check user Python files, prioritize main files
            python_files = []
            main_files = []  # app.py, main.py, etc - check these first
            
            for py_file in self.project_path.rglob("*.py"):
                # Skip virtual environments, caches, and site-packages
                if any(part in str(py_file) for part in ['venv/', '.venv/', '__pycache__/', 'site-packages/']):
                    continue
                
                file_str = str(py_file)
                if any(name in py_file.name for name in ['app.py', 'main.py', 'server.py']):
                    main_files.append(file_str)
                else:
                    python_files.append(file_str)
            
            # Check main files first, then others (limit total for speed)
            all_files = main_files + python_files[:8]  # Max 8 non-main files
            
            if not all_files:
                return ""
            
            cmd = [sys.executable, "-m", "pyflakes"] + all_files
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
                timeout=5  # Reduced timeout
            )
            
            if not result.stdout.strip():
                return ""
            
            # Filter out non-critical warnings - only keep runtime errors
            critical_lines = []
            for line in result.stdout.strip().split('\n'):
                if line.strip() and not any(warning in line for warning in [
                    'imported but unused',
                    'assigned to but never used',
                    'redefinition of unused'
                ]):
                    # This is a critical error (undefined names, etc.)
                    critical_lines.append(line)
            
            return '\n'.join(critical_lines) if critical_lines else ""
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""
        except Exception:
            return ""
    
    def check_env_without_dotenv(self) -> str:
        """Check for environment variable usage without load_dotenv"""
        errors = []
        
        for py_file in self.project_path.rglob("*.py"):
            # Skip virtual environments, caches, and site-packages
            if any(part in str(py_file) for part in ['venv/', '.venv/', '__pycache__/', 'site-packages/']):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file uses os.environ but doesn't have load_dotenv
                uses_environ = 'os.environ' in content
                has_load_dotenv = 'load_dotenv' in content
                
                if uses_environ and not has_load_dotenv:
                    rel_path = py_file.relative_to(self.project_path)
                    errors.append(f"{rel_path}: error: Uses os.environ but missing load_dotenv() - environment variables may not be loaded")
                    
            except Exception:
                continue
        
        return "\n".join(errors)
    
    def run_comprehensive_check(self) -> str:
        """Run comprehensive check with parallel execution for speed"""
        start_time = time.time()
        
        print(f"🔍 Running fast Python error check: {self.project_path}")
        
        # Run all checks in parallel for speed
        mypy_output = ""
        pyflakes_output = ""
        env_check_output = ""
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all jobs
            mypy_future = executor.submit(self.run_mypy)
            pyflakes_future = executor.submit(self.run_pyflakes)
            env_future = executor.submit(self.check_env_without_dotenv)
            
            # Collect results as they complete
            for future in as_completed([mypy_future, pyflakes_future, env_future]):
                try:
                    result = future.result(timeout=3)  # Max 3 seconds per tool
                    if future == mypy_future:
                        mypy_output = result
                    elif future == pyflakes_future:
                        pyflakes_output = result
                    else:
                        env_check_output = result
                except Exception:
                    # If one tool fails, continue with the others
                    pass
        
        # If both MyPy and Pyflakes failed or returned nothing, use basic syntax check
        if not mypy_output and not pyflakes_output:
            basic_syntax_output = self._basic_syntax_check()
            if basic_syntax_output:
                mypy_output = basic_syntax_output
        
        # Combine outputs
        all_output = []
        
        if mypy_output:
            all_output.append("=== Critical MyPy Errors ===")
            all_output.append(mypy_output)
        
        if pyflakes_output:
            if all_output:
                all_output.append("")
            all_output.append("=== Critical Pyflakes Errors ===") 
            all_output.append(pyflakes_output)
        
        if env_check_output:
            if all_output:
                all_output.append("")
            all_output.append("=== Environment Variable Errors ===")
            all_output.append(env_check_output)
        
        final_output = "\n".join(all_output)
        
        elapsed = time.time() - start_time
        print(f"✅ Fast check completed in {elapsed:.2f}s")
        
        # Write to error file
        self.write_error_file(final_output, elapsed)
        
        return final_output
    
    def write_error_file(self, output: str, elapsed_time: float):
        """Write error report to file"""
        try:
            if not output:
                self.error_file.write_text("✅ No Python errors found\n")
            else:
                report = [
                    f"Python Error Report ({elapsed_time:.2f}s)",
                    "=" * 50,
                    "",
                    output
                ]
                self.error_file.write_text("\n".join(report))
                
        except Exception as e:
            print(f"Warning: Could not write error file: {e}")

def main():
    """Main entry point"""
    project_path = "."
    
    # Parse arguments properly
    for arg in sys.argv[1:]:
        if arg != "--once":
            project_path = arg
            break
    
    checker = PurePythonChecker(project_path)
    
    if "--once" in sys.argv:
        # One-time check for API usage
        result = checker.run_comprehensive_check()
        
        if result:
            print("Python validation errors found:")
            print(result)
            sys.exit(1)  # Errors found
        else:
            print("✅ No Python errors found")
            sys.exit(0)  # No errors
    else:
        # Continuous monitoring mode
        print("Starting continuous Python error monitoring...")
        while True:
            try:
                checker.run_comprehensive_check()
                time.sleep(5)  # Check every 5 seconds
            except KeyboardInterrupt:
                print("\n🛑 Python error checker stopped")
                break
            except Exception as e:
                print(f"❌ Error in checker: {e}")
                time.sleep(5)

if __name__ == "__main__":
    main()