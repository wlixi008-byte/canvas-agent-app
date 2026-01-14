import json
import os
from typing import List, Dict, Any

class CanvasEngine:
    """
    Core engine for parsing and generating Obsidian Canvas (.canvas) files.
    """
    def __init__(self, canvas_path: str):
        self.canvas_path = canvas_path

    def read_canvas(self) -> Dict[str, Any]:
        """Reads the canvas JSON file."""
        print(f"DEBUG: Reading canvas from {self.canvas_path}")
        if not os.path.exists(self.canvas_path):
            print(f"DEBUG: Canvas file not found at {self.canvas_path}")
            return {"nodes": [], "edges": []}
        with open(self.canvas_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"DEBUG: File content length: {len(content)}")
            return json.loads(content)

    def write_canvas(self, data: Dict[str, Any]):
        """Writes data to the canvas JSON file."""
        with open(self.canvas_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def extract_intent(self) -> List[Dict[str, str]]:
        """
        Extracts structural intent from canvas nodes.
        Returns a list of components with their name, path, and responsibility.
        """
        data = self.read_canvas()
        intent = []
        for node in data.get("nodes", []):
            text = node.get("text", "")
            print(f"DEBUG: Processing node text: {repr(text)}") # Debug line
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) >= 2:
                name = lines[0]
                path = lines[1]
                responsibility = "\n".join(lines[2:])
                intent.append({
                    "name": name,
                    "path": path,
                    "responsibility": responsibility,
                    "color": node.get("color")
                })
        return intent
