import os
import json
import ast

class ReverseGenerator:
    """
    逆向生成器：扫描代码库并生成 architecture.canvas 文件。
    """
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.nodes = []
        self.edges = []

    def scan(self):
        """扫描文件，分析依赖关系，并应用网格布局。"""
        exclude_dirs = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'dist', 'build'}
        
        file_to_id = {}
        
        # 1. 第一遍扫描：建立文件索引
        all_files = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                    all_files.append((file, rel_path, full_path))

        # 2. 自动网格布局参数
        cols = 4  # 每行显示4个方块
        spacing_x = 400
        spacing_y = 300
        
        for i, (file, rel_path, full_path) in enumerate(all_files):
            node_id = rel_path.replace("/", "_")
            file_to_id[rel_path] = node_id
            
            responsibility = self._get_docstring(full_path)
            
            # 计算网格坐标
            row = i // cols
            col = i % cols
            
            self.nodes.append({
                "id": node_id,
                "type": "text",
                "text": f"{file}\n{rel_path}\n\n{responsibility}",
                "x": col * spacing_x,
                "y": row * spacing_y,
                "width": 320,
                "height": 180,
                "color": self._get_color(file)
            })

        # 3. 第二遍扫描：建立连线
        for file, rel_path, full_path in all_files:
            from_id = file_to_id.get(rel_path)
            if from_id:
                imports = self._get_imports(full_path)
                for imp in imports:
                    for target_rel, to_id in file_to_id.items():
                        mod_path = target_rel.replace(".py", "").replace("/", ".")
                        if imp == mod_path or imp.startswith(mod_path + "."):
                            if from_id != to_id:
                                edge_id = f"edge_{from_id}_{to_id}"
                                if not any(e["id"] == edge_id for e in self.edges):
                                    self.edges.append({
                                        "id": edge_id,
                                        "fromNode": from_id,
                                        "fromSide": "bottom",
                                        "toNode": to_id,
                                        "toSide": "top"
                                    })

    def _get_imports(self, path):
        """从文件中提取 import 语句。"""
        imports = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            imports.append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
        except:
            pass
        return imports

    def _get_docstring(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
                
                # 1. 获取顶部文档字符串
                doc = ast.get_docstring(tree) or ""
                
                # 2. 提取类名和函数名
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')]
                
                info = []
                if doc: info.append(f"描述: {doc}")
                if classes: info.append(f"类: {', '.join(classes)}")
                if functions: info.append(f"核心函数: {', '.join(functions[:5])}{'...' if len(functions)>5 else ''}")
                
                return "\n".join(info) if info else "未定义职责 (空文件或无导出项)"
        except Exception as e:
            return f"解析失败: {str(e)}"

    def _get_color(self, filename):
        if "main" in filename: return "1" # 红
        if "engine" in filename: return "3" # 黄
        if "mgr" in filename: return "3" # 黄
        return "2" # 橙

    def save(self, output_path):
        """保存为 .canvas 文件。"""
        data = {"nodes": self.nodes, "edges": self.edges}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"成功生成白板图: {output_path}")

if __name__ == "__main__":
    # 扫描 OpenManus-main 项目
    root = r"C:\Users\Administrator\Desktop\OpenManus-main"
    generator = ReverseGenerator(root)
    # 自动识别 src 或根目录下的 python 文件
    generator.scan()
    # 将生成的架构图保存在桌面，方便查看
    generator.save(r"C:\Users\Administrator\Desktop\OpenManus-main\architecture.canvas")
