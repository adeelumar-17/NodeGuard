import json
from pathlib import Path
from typing import Any, Dict


class Config:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = Path(config_path)
        self.data: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.data = json.load(f)
    
    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        self.data[key] = value