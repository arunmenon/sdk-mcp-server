"""
SDK Indexer - Creates searchable index for SDK files
"""
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import fnmatch


class SDKIndexer:
    """Creates searchable index for any SDK structure"""
    
    def __init__(self):
        self.indices: Dict[str, Dict[str, Any]] = {}
    
    async def index_sdk(self, sdk_id: str, source_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive index of SDK files"""
        index = {
            "sdk_id": sdk_id,
            "name": config.get("name", sdk_id),
            "description": config.get("description", ""),
            "files": [],
            "classes": {},
            "functions": {},
            "imports": {},
            "file_map": {},  # Maps saved names to original paths
            "concepts": config.get("concepts", {})
        }
        
        # Get file patterns
        file_patterns = config.get("file_patterns", ["**/*.py"])
        exclude_patterns = config.get("exclude_patterns", [])
        
        # Walk through files matching patterns
        all_files = []
        for pattern in file_patterns:
            all_files.extend(source_path.glob(pattern))
        
        # Process files
        for file_path in sorted(set(all_files)):
            if self._should_exclude(file_path, source_path, exclude_patterns):
                continue
            
            try:
                file_info = await self._analyze_file(file_path, source_path)
                
                # Generate saved filename (flattened structure)
                saved_name = self._generate_saved_name(file_info["relative_path"], sdk_id)
                file_info["saved_as"] = saved_name
                
                index["files"].append(file_info)
                index["file_map"][saved_name] = file_info["relative_path"]
                
                # Build class index
                for cls in file_info.get("classes", []):
                    index["classes"][cls["name"]] = {
                        "file": saved_name,
                        "line": cls["line"],
                        "methods": cls.get("methods", [])
                    }
                
                # Build function index
                for func in file_info.get("functions", []):
                    index["functions"][func["name"]] = {
                        "file": saved_name,
                        "line": func["line"]
                    }
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        self.indices[sdk_id] = index
        return index
    
    def _should_exclude(self, file_path: Path, base_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded"""
        relative_path = str(file_path.relative_to(base_path))
        
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(relative_path, pattern):
                return True
            if fnmatch.fnmatch(str(file_path), pattern):
                return True
        
        return False
    
    def _generate_saved_name(self, relative_path: str, sdk_id: str) -> str:
        """Generate flattened filename for saving"""
        # Replace path separators with underscores
        # Remove .py extension and add .md
        name = relative_path.replace("/", "_").replace("\\", "_")
        if name.endswith(".py"):
            name = name[:-3]
        return f"{sdk_id}_{name}.md"
    
    async def _analyze_file(self, file_path: Path, base_path: Path) -> Dict[str, Any]:
        """Extract metadata from source file"""
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        relative_path = str(file_path.relative_to(base_path))
        
        file_info = {
            "relative_path": relative_path,
            "original_path": str(file_path),
            "classes": [],
            "functions": [],
            "imports": [],
            "size": len(content),
            "lines": content.count('\n') + 1
        }
        
        try:
            tree = ast.parse(content)
            file_info["classes"] = self._extract_classes(tree)
            file_info["functions"] = self._extract_functions(tree)
            file_info["imports"] = self._extract_imports(tree)
        except SyntaxError:
            # Not a valid Python file, just store basic info
            pass
        
        return file_info
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions from AST"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "methods": [],
                    "bases": [self._get_name(base) for base in node.bases]
                }
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info["methods"].append({
                            "name": item.name,
                            "line": item.lineno
                        })
                
                classes.append(class_info)
        
        return classes
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract top-level function definitions"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if it's a top-level function (not a method)
                parent = getattr(node, '_parent', None)
                if parent is None or isinstance(parent, ast.Module):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "async": isinstance(node, ast.AsyncFunctionDef)
                    })
        
        return functions
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return "Unknown"
    
    def get_index(self, sdk_id: str) -> Optional[Dict[str, Any]]:
        """Get index for a specific SDK"""
        return self.indices.get(sdk_id)
    
    def save_indices(self, output_dir: Path) -> None:
        """Save indices to disk for persistence"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for sdk_id, index in self.indices.items():
            index_file = output_dir / f"{sdk_id}_index.json"
            with open(index_file, 'w') as f:
                json.dump(index, f, indent=2)
    
    def load_indices(self, input_dir: Path) -> None:
        """Load indices from disk"""
        if not input_dir.exists():
            return
        
        for index_file in input_dir.glob("*_index.json"):
            with open(index_file, 'r') as f:
                index = json.load(f)
                sdk_id = index.get("sdk_id")
                if sdk_id:
                    self.indices[sdk_id] = index