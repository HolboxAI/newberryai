from typing import Any, Callable, Dict, List, get_type_hints
import inspect

class FunctionRegistry:
    def __init__(self):
        self.functions: Dict[str, Callable] = {}
        self.descriptions: Dict[str, Dict[str, Any]] = {}

        def get_weather(location: str) -> str:
            """Get weather for a specific location"""
            return f"Weather in {location} is sunny and 25°C"

        def calculate_distance(city1: str, city2: str) -> str:
            """Calculate distance between two cities"""
            return f"Distance between {city1} and {city2} is 500 km"

        def translate_text(text: str, target_language: str) -> str:
            """Translate text to target language"""
            return f"Translated '{text}' to {target_language}"

        def search_web(query: str, num_results: int = 3) -> str:
            """Search the web for a query and return specified number of results"""
            return f"Found {num_results} results for: {query}"

        # Dictionary of all base functions
        BASE_FUNCTIONS = {
            'get_weather': {"func": get_weather, "category": "utility"},
            'calculate_distance': {"func": calculate_distance, "category": "utility"},
            'translate_text': {"func": translate_text, "category": "language"},
            'search_web': {"func": search_web, "category": "search"}
        }

        for func in BASE_FUNCTIONS.values():
            self.register(func["func"], category = func["category"])
    
    def _extract_function_metadata(self, func: Callable) -> Dict[str, Any]:
        """Extract function metadata using introspection"""
        sig = inspect.signature(func)
        
        doc = inspect.getdoc(func) or "No description available"
        description = doc.split("\n")[0]
        
        type_hints = get_type_hints(func)
        parameters = []
        for param_name, param in sig.parameters.items():
            if param.default == inspect.Parameter.empty:
                param_type = type_hints.get(param_name, Any).__name__
                parameters.append({
                    "name": param_name,
                    "type": param_type,
                    "required": True
                })
            else:
                param_type = type_hints.get(param_name, Any).__name__
                parameters.append({
                    "name": param_name,
                    "type": param_type,
                    "required": False,
                    "default": param.default
                })
        
        return {
            "name": func.__name__,
            "description": description,
            "parameters": parameters,
            "full_docstring": doc
        }
    
    def register(self, func: Callable, category: str = "general"):
        """Register a function with automatically extracted metadata"""
        metadata = self._extract_function_metadata(func)
        metadata["category"] = category
        self.functions[metadata["name"]] = func
        self.descriptions[metadata["name"]] = metadata
    
    def list_functions(self) -> List[str]:
        """List all registered function names"""
        return list(self.functions.keys())
