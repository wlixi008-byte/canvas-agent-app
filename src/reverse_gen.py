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
        """扫描文件，分析依赖关系，并应用业务逻辑分层排列。"""
        exclude_dirs = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'dist', 'build'}
        
        file_to_id = {}
        all_files = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                    all_files.append((file, rel_path, full_path))

        # 1. 业务逻辑分层分类
        layers = {
            "entry": [],      # 入口层 (红)
            "core": [],       # 核心中枢 (黄)
            "service": [],    # 业务服务 (黄)
            "infra": [],      # 基础设施/工具 (橙)
            "other": []       # 其他
        }

        for file_info in all_files:
            file, rel_path, _ = file_info
            if "main" in file or "app.py" in file:
                layers["entry"].append(file_info)
            elif "core" in rel_path or "engine" in rel_path:
                layers["core"].append(file_info)
            elif "service" in rel_path or "logic" in rel_path:
                layers["service"].append(file_info)
            elif "utils" in rel_path or "infra" in rel_path or "client" in rel_path:
                layers["infra"].append(file_info)
            else:
                layers["other"].append(file_info)

        # 2. 纵向分层排列 (Y轴代表架构深度)
        layer_order = ["entry", "core", "service", "infra", "other"]
        spacing_x = 450
        spacing_y = 400
        
        current_y = 0
        for layer_name in layer_order:
            files_in_layer = layers[layer_name]
            if not files_in_layer:
                continue
                
            # 所有层级（包括 OTHER）均保持单行横向排列，以保证连线清晰
            for x_idx, (file, rel_path, full_path) in enumerate(files_in_layer):
                node_id = rel_path.replace("/", "_")
                file_to_id[rel_path] = node_id
                responsibility = self._get_docstring(full_path)
                
                self.nodes.append({
                    "id": node_id,
                    "type": "text",
                    "text": f"【{layer_name.upper()}】\n{file}\n{rel_path}\n\n{responsibility}",
                    "x": x_idx * spacing_x,
                    "y": current_y,
                    "width": 350,
                    "height": 220,
                    "color": self._get_color_by_layer(layer_name)
                })
            current_y += spacing_y

        # 3. 建立连线 (添加降噪逻辑)
        for file, rel_path, full_path in all_files:
            from_id = file_to_id.get(rel_path)
            if from_id:
                # 获取当前文件所属层级
                from_layer = next((l for l, fs in layers.items() if any(f[1] == rel_path for f in fs)), "other")
                
                imports = self._get_imports(full_path)
                for imp in imports:
                    for target_rel, to_id in file_to_id.items():
                        mod_path = target_rel.replace(".py", "").replace("/", ".")
                        if imp == mod_path or imp.startswith(mod_path + "."):
                            if from_id != to_id:
                                # 【取消降噪】：显示所有连线，无论层级
                                to_layer = next((l for l, fs in layers.items() if any(f[1] == target_rel for f in fs)), "other")
                                
                                edge_id = f"edge_{from_id}_{to_id}"
                                if not any(e["id"] == edge_id for e in self.edges):
                                    # 根据层级决定连线样式 (Obsidian Canvas JSON 不直接支持粗细，
                                    # 但可以通过 label 和连线方向模拟重要性，或在 text 中记录。
                                    # 针对当前应用，我们使用 label 来标注强度，并根据重要性调整 color)
                                    
                                    style_label = ""
                                    edge_color = "0" # 默认
                                    
                                    if from_layer in ["entry", "core"] and to_layer in ["core", "service"]:
                                        style_label = "【核心调用】"
                                        edge_color = "1" # 红色线表示核心
                                    elif to_layer == "other":
                                        style_label = "--- 次要 ---"
                                        edge_color = "5" # 青色虚线感
                                    
                                    self.edges.append({
                                        "id": edge_id,
                                        "fromNode": from_id,
                                        "fromSide": "bottom",
                                        "toNode": to_id,
                                        "toSide": "top",
                                        "label": style_label,
                                        "color": edge_color
                                    })

    def _get_color_by_layer(self, layer_name):
        colors = {
            "entry": "1",    # 红
            "core": "3",     # 黄
            "service": "3",  # 黄
            "infra": "2",    # 橙
            "other": "5"     # 青
        }
        return colors.get(layer_name, "0")

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
