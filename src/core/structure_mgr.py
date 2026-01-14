import os
from typing import List, Dict

class StructureManager:
    """
    Manages the directory structure and file skeletons based on Canvas intent.
    """
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def sync_directories(self, intent: List[Dict[str, str]]):
        """
        Creates directories and file skeletons based on the provided intent.
        """
        for component in intent:
            path = component.get("path")
            if not path or path.startswith('`'): # Skip placeholders
                continue
            
            full_path = os.path.join(self.root_dir, path)
            directory = os.path.dirname(full_path)
            
            # Create directory
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"Created directory: {directory}")
            
            # Create file skeleton if it doesn't exist
            if not os.path.exists(full_path):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(f'"""\n{component.get("name")}\n\nResponsibility: {component.get("responsibility")}\n"""\n\n')
                print(f"Created file: {full_path}")

    def scan_actual_structure(self) -> List[str]:
        """Scans the actual filesystem for source files."""
        files = []
        for root, _, filenames in os.walk(os.path.join(self.root_dir, "src")):
            for filename in filenames:
                if filename.endswith(".py"):
                    files.append(os.path.relpath(os.path.join(root, filename), self.root_dir))
        return files
