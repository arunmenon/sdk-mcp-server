"""
SDK Search Engine - Unified search across SDKs
"""
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class SDKSearchEngine:
    """Unified search across all SDKs"""
    
    def __init__(self, indexer):
        self.indexer = indexer
        self.data_dir = Path("data")
    
    def search_code(self, sdk_id: str, query: str, **options) -> Dict[str, List[str]]:
        """Search within specific SDK"""
        index = self.indexer.get_index(sdk_id)
        if not index:
            return {}
        
        results = {}
        case_sensitive = options.get("case_sensitive", False)
        max_results_per_file = options.get("max_results_per_file", 10)
        regex = options.get("regex", False)
        
        # Prepare search pattern
        if regex:
            try:
                pattern = re.compile(query, re.IGNORECASE if not case_sensitive else 0)
            except re.error:
                return {"error": ["Invalid regex pattern"]}
        else:
            pattern = query.lower() if not case_sensitive else query
        
        # Search through files
        sdk_data_dir = self.data_dir / sdk_id
        if not sdk_data_dir.exists():
            return {}
        
        for file_info in index.get("files", []):
            saved_name = file_info.get("saved_as")
            if not saved_name:
                continue
            
            file_path = sdk_data_dir / saved_name
            if not file_path.exists():
                continue
            
            matches = self._search_file(file_path, pattern, regex, case_sensitive, max_results_per_file)
            if matches:
                results[saved_name] = matches
        
        return results
    
    def _search_file(self, file_path: Path, pattern, is_regex: bool, case_sensitive: bool, max_results: int) -> List[str]:
        """Search within a single file"""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if self._line_matches(line, pattern, is_regex, case_sensitive):
                        matches.append(f"Line {line_num}: {line.strip()}")
                        if len(matches) >= max_results:
                            break
        except Exception as e:
            return [f"Error reading file: {e}"]
        
        return matches
    
    def _line_matches(self, line: str, pattern, is_regex: bool, case_sensitive: bool) -> bool:
        """Check if line matches pattern"""
        if is_regex:
            return bool(pattern.search(line))
        else:
            search_line = line if case_sensitive else line.lower()
            return pattern in search_line
    
    def search_all_sdks(self, query: str, **options) -> Dict[str, Dict[str, List[str]]]:
        """Search across all indexed SDKs"""
        all_results = {}
        
        for sdk_id in self.indexer.indices:
            results = self.search_code(sdk_id, query, **options)
            if results and results != {}:
                all_results[sdk_id] = results
        
        return all_results
    
    def find_class(self, sdk_id: str, class_name: str) -> Optional[Dict[str, Any]]:
        """Find class definition in SDK"""
        index = self.indexer.get_index(sdk_id)
        if not index:
            return None
        
        classes = index.get("classes", {})
        return classes.get(class_name)
    
    def find_function(self, sdk_id: str, function_name: str) -> Optional[Dict[str, Any]]:
        """Find function definition in SDK"""
        index = self.indexer.get_index(sdk_id)
        if not index:
            return None
        
        functions = index.get("functions", {})
        return functions.get(function_name)
    
    def get_class_source(self, sdk_id: str, class_name: str) -> Optional[str]:
        """Extract complete class source code"""
        class_info = self.find_class(sdk_id, class_name)
        if not class_info:
            return None
        
        file_name = class_info.get("file")
        if not file_name:
            return None
        
        file_path = self.data_dir / sdk_id / file_name
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            # Extract class definition from content
            return self._extract_class_from_content(content, class_name, class_info.get("line", 1))
        except Exception as e:
            return f"Error reading class source: {e}"
    
    def _extract_class_from_content(self, content: str, class_name: str, start_line: int) -> str:
        """Extract class definition from file content"""
        lines = content.split('\n')
        
        # Find the class definition line
        class_start = None
        for i, line in enumerate(lines):
            if f"class {class_name}" in line:
                class_start = i
                break
        
        if class_start is None:
            return f"Class {class_name} not found in file"
        
        # Extract class body by tracking indentation
        result_lines = [lines[class_start]]
        base_indent = len(lines[class_start]) - len(lines[class_start].lstrip())
        
        for i in range(class_start + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                result_lines.append(line)
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent and line.strip():
                # End of class
                break
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def find_examples(self, sdk_id: str, topic: str) -> Dict[str, List[str]]:
        """Find usage examples for a topic"""
        # Search for common patterns related to the topic
        patterns = [
            f"def.*{topic}",  # Function definitions
            f"class.*{topic}",  # Class definitions  
            f"{topic}\\s*\\(",  # Function calls
            f"@{topic}",  # Decorators
            f"self\\.{topic}",  # Method calls
        ]
        
        all_results = {}
        for pattern in patterns:
            results = self.search_code(sdk_id, pattern, regex=True, max_results_per_file=5)
            for file, matches in results.items():
                if file not in all_results:
                    all_results[file] = []
                all_results[file].extend(matches)
        
        return all_results
    
    def compare_implementations(self, concept: str, sdk_ids: List[str]) -> Dict[str, Any]:
        """Compare how different SDKs implement similar concepts"""
        comparisons = {}
        
        for sdk_id in sdk_ids:
            if sdk_id not in self.indexer.indices:
                continue
            
            # Look for the concept in classes and functions
            sdk_info = {
                "sdk_name": self.indexer.indices[sdk_id].get("name", sdk_id),
                "classes": {},
                "functions": {},
                "examples": {}
            }
            
            # Search for classes
            index = self.indexer.get_index(sdk_id)
            if index:
                # Check configured concepts
                concepts = index.get("concepts", {})
                if concept in concepts:
                    # Use configured concept mappings
                    for variant in concepts[concept]:
                        class_info = self.find_class(sdk_id, variant)
                        if class_info:
                            sdk_info["classes"][variant] = class_info
                        func_info = self.find_function(sdk_id, variant)
                        if func_info:
                            sdk_info["functions"][variant] = func_info
                else:
                    # Search for the concept directly
                    class_info = self.find_class(sdk_id, concept)
                    if class_info:
                        sdk_info["classes"][concept] = class_info
                    func_info = self.find_function(sdk_id, concept)
                    if func_info:
                        sdk_info["functions"][concept] = func_info
            
            # Find examples
            sdk_info["examples"] = self.find_examples(sdk_id, concept)
            
            if sdk_info["classes"] or sdk_info["functions"] or sdk_info["examples"]:
                comparisons[sdk_id] = sdk_info
        
        return comparisons