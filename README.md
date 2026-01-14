# Canvas-Agent-App 🤖

> **基于画布驱动开发 (CDD) 的可视化智能 Agent 构建系统**

本项目是一个将 AI Agent 开发与可视化白板（Obsidian Canvas）深度结合的框架。它实现了“图形即意图，意图即代码”的开发范式，支持正向生成与逆向分析。

## 🌟 核心特性

- **CDD 架构驱动**：Canvas 白板作为项目唯一的权威真相源 (Single Source of Truth)。
- **正向工程 (Forward Sync)**：在白板上规划流程逻辑，自动生成对应的物理目录、文件骨架及职责注释。
- **逆向工程 (Reverse Scan)**：深度扫描现有项目（如 OpenManus），自动生成带连线、类及函数定义的架构白板。
- **智能布局与样式**：
  - **分层布局**：自动将代码分为入口层(Entry)、核心层(Core)、服务层(Service)和基础层(Infra)，纵向排布。
  - **可视化连线分级**：红色实线表示【核心调用】，黑色细线表示一般联系，青色细线表示次要逻辑。
  - **横向扩展**：所有层级均采用横向单行排列，确保复杂依赖关系下的连线依然清晰可辨。
- **Agent 记忆持久化**：通过 `AGENTS.md` 存储 Agent 的深度推理逻辑与协作协议。

## 📂 项目结构

```text
.
├── AGENTS.md             # Agent 核心指令与 CDD 协议
├── architecture.canvas   # 可视化架构设计图 (SSOT)
├── CHANGELOG.md          # 版本演进记录
├── src/                  # 源代码
│   ├── main.py           # 正向同步引擎 (Canvas -> Code)
│   ├── reverse_gen.py    # 逆向生成引擎 (Code -> Canvas)
│   └── core/             # 核心逻辑模块
└── README.md             # 项目使用说明
```

## 🚀 快速上手

### 1. 环境准备
- 安装 Python 3.x
- 安装 **Obsidian** (用于查看和编辑 `.canvas` 可视化白板)

### 2. 正向开发模式 (从零构建)
1. 在 Obsidian 中打开 `architecture.canvas`。
2. 添加文字节点，格式如下：
   ```text
   模块名称
   src/path/to/filename.py
   职责描述
   ```
3. 运行同步命令：
   ```bash
   python src/main.py
   ```
   *应用会自动创建目录并在 `src/` 下生成文件。*

### 3. 逆向工程模式 (分析成熟项目)
1. 将 `reverse_gen.py` 中的 `root` 变量指向您想要分析的项目路径。
2. 运行逆向扫描：
   ```bash
   python src/reverse_gen.py
   ```
3. 在 Obsidian 中打开生成的 `architecture.canvas`，即可看到带依赖连线的架构图。

## 🛠️ 协作协议规范

- **颜色编码**：
  - 🔴 **红色** (Color 1): 程序入口 / API 网关
  - 🟡 **黄色** (Color 3): 核心业务逻辑 / 引擎层
  - 🟠 **橙色** (Color 2): 工具类 / 辅助模块
- **连线逻辑**：箭头始终从“调用方”指向“被调用方”。

## 🔗 相关资源

- [Obsidian Canvas 官网](https://obsidian.md/canvas)
- [Kode Agent 协作协议](https://github.com/shareAI-lab/kode)

---
🤖 *Generated with passion for the future of programming.*
