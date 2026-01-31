# Lean + Claude Code 环境搭建指南

本指南帮助你快速完成 Lean + Claude Code 的开发环境配置。

---

## 快速开始

### 方案 1：使用脚本

```bash
git clone https://github.com/project-numina/numina-lean-agent
cd numina-lean-agent/tutorial
./setup.sh myproject
```

细节可参考 [setup.sh](./setup.sh)。

### 方案 2：手动执行

```bash
# 安装 elan
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
# 刷新 shell 环境
source ~/.elan/env

# 创建 Lean 项目
lake new myproject math && cd myproject
lake update && lake exe cache get && lake build

# 安装 Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# 重启终端（或执行 source ~/.bashrc / ~/.zshrc）

# 安装 lean-lsp-mcp
git clone https://github.com/project-numina/lean-lsp-mcp ~/lean-lsp-mcp
chmod +x ~/lean-lsp-mcp/numina-lean-mcp.sh

# 添加 MCP（务必在项目目录下执行！）
cd myproject
claude mcp add lean-lsp -- ~/lean-lsp-mcp/numina-lean-mcp.sh

# 验证
claude mcp list
```

---

## 详细步骤

### 1. 前置依赖

确保已安装 `git` 与 `curl`：

```bash
git --version
curl --version
```

若未安装，请先使用系统包管理器安装。

### 2. 安装 Lean（elan）

官方指南见 [此处](https://lean-lang.org/lean4/doc/setup.html)。

安装 elan（Lean 版本管理器）：

```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
```

安装后刷新环境：

```bash
source ~/.elan/env  # 将 Lean 加入 PATH
```

或直接重启终端。

> **验证：** 运行 `lean --version` 确认安装成功。

### 3. 创建 Lean 项目

```bash
lake new myproject math
cd myproject
lake update
lake exe cache get
lake build
```

> **说明：** `math` 模板会自动配置 Mathlib 依赖；`lake exe cache get` 下载预编译缓存以加速首次构建。

### 4. 安装 Claude Code

**方式 1：npm**

```bash
npm install -g @anthropic-ai/claude-code
```

**方式 2：安装脚本（无需 npm）**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

> 更多信息：[Claude Code 官方文档](https://docs.claude.com/en/docs/claude-code/setup)

### 5. 安装 lean-lsp-mcp

#### 5.1 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装后重启终端或执行 `source ~/.bashrc`（zsh 请执行 `source ~/.zshrc`）。

#### 5.2 克隆与配置

```bash
# 克隆仓库
git clone https://github.com/project-numina/lean-lsp-mcp
cd lean-lsp-mcp

# 添加执行权限
chmod +x numina-lean-mcp.sh
```

#### 5.3 添加到 Claude Code

> **重要：MCP 配置与目录绑定。** 需在 Lean 项目目录（或其父目录）运行 `claude mcp add`，否则该项目下无法使用。

将路径替换为你的实际绝对路径：

```bash
# 先进入 Lean 项目目录
cd /path/to/myproject

# 再添加 MCP 服务器
claude mcp add lean-lsp -- /absolute/path/to/lean-lsp-mcp/numina-lean-mcp.sh
```

示例：
```bash
cd ~/myproject
claude mcp add lean-lsp -- /home/username/lean-lsp-mcp/numina-lean-mcp.sh
```

> **提示：** 若希望全局可用，可在家目录 (`~`) 或使用 `--scope user` 执行。

#### 5.4 验证 MCP 连接

```bash
claude mcp list
```

预期输出：
```text
Checking MCP server health...
lean-lsp: /home/username/lean-lsp-mcp/numina-lean-mcp.sh  - ✓ Connected
```

#### 故障排查

- 显示 `uvx lean-lsp-mcp` 而非自定义路径：
```bash
claude mcp remove lean-lsp
claude mcp add lean-lsp -- /absolute/path/to/lean-lsp-mcp/numina-lean-mcp.sh
```

- 提示 `lake` 未找到或失败：
  确认 `~/.elan/env` 已写入 `PATH`，在 `~/.bashrc` 或 `~/.zshrc` 中添加：
  ```bash
  source ~/.elan/env
  ```
  然后重启终端或执行 `source ~/.elan/env`。

- 连接失败：
  1) 路径正确；2) 文件有执行权限 `chmod +x numina-lean-mcp.sh`；3) 查看日志 `cat /path/to/lean-lsp-mcp/mcp_lean_lsp.log`；4) 确认 uv 已正确安装 `uv --version`。

- 运行 Claude Code 时未显示 MCP：
  MCP 与添加时的工作目录绑定，确保在同一目录（或父目录）运行 `claude`。

### 6. 安装 lean4-skills

在 Claude Code 内执行：

```bash
/plugin marketplace add cameronfreer/lean4-skills
/plugin install lean4-theorem-proving    # 核心技能
/plugin install lean4-memories           # 可选：记忆功能
```

> 更多信息：[lean4-skills GitHub](https://github.com/cameronfreer/lean4-skills)

### 7. 验证安装

进入你的 Lean 项目目录，启动 Claude Code：

```bash
cd myproject
claude
```

在 Claude Code 内测试：
1. 输入 `/mcp` 查看 MCP 连接状态
2. 试着让 Claude 分析或编写 Lean 代码

---

## 相关链接

- [Lean 官方安装指南](https://lean-lang.org/install/manual/)
- [elan GitHub](https://github.com/leanprover/elan)
- [Claude Code 文档](https://docs.claude.com/en/docs/claude-code/setup)
- [lean-lsp-mcp GitHub](https://github.com/project-numina/lean-lsp-mcp)
- [lean4-skills GitHub](https://github.com/cameronfreer/lean4-skills)
