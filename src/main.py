import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from core.canvas_engine import CanvasEngine
from core.structure_mgr import StructureManager

def main():
    # Use the root directory where AGENTS.md and architecture.canvas were created
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    canvas_path = os.path.join(root_dir, "architecture.canvas")
    
    engine = CanvasEngine(canvas_path)
    manager = StructureManager(root_dir)
    
    print("--- Canvas-Integrated Agent Sync ---")
    
    # 1. Forward: Canvas -> Code
    print("Reading intent from Canvas...")
    intent = engine.extract_intent()
    print(f"Found {len(intent)} components in Canvas.")
    
    print("Syncing directory structure...")
    manager.sync_directories(intent)
    
    # 2. Backward: Code -> Info (Simulation)
    print("Scanning actual code structure...")
    actual_files = manager.scan_actual_structure()
    print(f"Actual files found: {actual_files}")
    
    print("Sync complete.")

if __name__ == "__main__":
    main()
