# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**Numina-Lean-Agent** 是一个基于 Claude Code 的形式化定理证明智能体系统，专门用于 Lean 4 定理证明。主要功能包括：
- 自动定理证明：使用 Claude AI 自动完成 Lean 4 数学定理的证明
- 多模式运行：支持单文件、批量文件和文件夹扫描运行
- 智能提示系统：提供不同难度级别的提示模板
- 子代理架构：支持协调器、蓝图代理、草图代理和证明代理等多代理协作
- 集成工具链：通过 MCP (Model Context Protocol) 与 Lean LSP 深度集成

**关键成就**：
- 证明了 Putnam 2025 竞赛的所有 12 个问题
- 完成了论文级别的 "Effective Brascamp-Lieb inequalities" 形式化
- 在 MiniF2F 基准测试上表现优异

## 系统架构

### 核心工作流程
1. **初始化**：加载任务配置和提示模板
2. **会话循环**：运行 Claude 代理，每轮检查证明进展
3. **验证**：使用 `lean_diagnostic_messages` 验证文件
4. **提交**：可选地创建 git 提交记录进展
5. **结果收集**：保存 JSON 格式的结果和 MCP 日志

### 目录结构
```
scripts/                    # 核心 Python 脚本
  run_claude.py            # CLI 入口（run/batch/from-folder 命令）
  runner.py                # 核心运行逻辑，Claude 会话管理
  task.py                  # 任务元数据和结果类型
  lean_checker.py          # Lean 文件验证工具
  statement_tracker.py     # 跟踪证明语句在多轮中的变化
  mcp_stats.py             # MCP 日志分析
  extract_sublemmas.py     # 子引理提取工具

leanproblems/              # Lean 4 项目，包含题目文件
  Minif2f/                 # MiniF2F 基准测试题目
  Putnam2025/              # Putnam 2025 竞赛题目（12个文件）
  Leanproblems/            # 项目模块
  lakefile.toml            # Lake 构建配置（mathlib v4.26.0）
  lean-toolchain           # Lean 版本配置 (v4.26.0)
  lake-manifest.json       # 依赖清单

prompts/                   # Prompt 模板系统
  prompt_complete_file.txt # 标准完成模式
  prompt_hard_mode.txt     # 困难模式（带提示）
  prompt_medium_mode.txt   # 中等难度模式
  docs/                    # 子代理模式文档
    prompts/               # 代理指令
      common.md           # 共享规则
      coordinator.md      # 协调器指令
      blueprint_agent.md  # 蓝图代理
      sketch_agent.md     # 草图代理
      proof_agent.md      # 证明代理
    technique/            # 系统设计文档

config/                    # 批量运行配置文件
  config_minif2f.yaml     # MiniF2F 评估配置

tutorial/                  # 安装和使用指南
  setup.md                # 环境设置指南
  usage.md                # 使用指南
  setup.sh                # 自动化设置脚本
  myproject/              # 示例项目
```

## 常用命令

### 构建 Lean 项目
```bash
cd leanproblems
lake update
lake exe cache get
lake build
```

### 运行模式
```bash
# 单文件运行
python -m scripts.run_claude run leanproblems/Minif2f/mathd_algebra_478.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5

# 批量运行（从配置文件）
python -m scripts.run_claude batch config/config_minif2f.yaml

# 运行文件夹内所有 .lean 文件
python -m scripts.run_claude from-folder leanproblems/Minif2f \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5

# 并行执行
python -m scripts.run_claude batch config/config_minif2f.yaml --parallel --max-workers 4
```

### MCP 配置
MCP 配置是目录作用域的，必须在目标工作目录添加：
```bash
# 从 Lean 项目目录添加
cd leanproblems
claude mcp add lean-lsp -- /absolute/path/to/lean-lsp-mcp/numina-lean-mcp.sh

# 验证连接
claude mcp list
```

## 配置系统

### YAML 配置文件格式
```yaml
defaults:
  task_type: file
  prompt_file: prompts/prompt_complete_file.txt
  cwd: .
  check_after_complete: true
  permission_mode: bypassPermissions
  result_dir: results/minif2f
  mcp_log_dir: mcp_logs/minif2f
  max_rounds: 2
  git_commit: false  # 可选：每轮自动创建 git 提交

tasks:
  - target_path: leanproblems/Minif2f/algebra_sqineq_2atp2bpge2ab.lean
    mcp_log_name: algebra_sqineq_2atp2bpge2ab
  - target_path: leanproblems/Minif2f/imo_1964_p1.lean
    mcp_log_name: imo_1964_p1
    max_rounds: 5  # 覆盖默认值
```

### 继承规则
- `defaults` 定义所有任务的默认值
- 每个任务继承 `defaults` 并可以覆盖任何参数
- 最终配置 = `defaults` + 任务特定配置（任务优先）

## 定理证明工作流程

### 核心约定
1. **无公理政策**：禁止使用 `axiom`，只允许 `sorry` 标记未完成部分
2. **验证要求**：每次修改后必须使用 `lean_diagnostic_messages` 验证
3. **工具优先级**：优先使用 `simp`、`native_decide`、`norm_cast` 等高效工具
4. **蓝图同步**：在子代理模式下，`BLUEPRINT.md` 是单一事实来源，必须立即更新

### 提示系统关键指令
- 使用 `lean_diagnostic_messages` 验证文件，错误表示 "severity 1"
- 优先使用 `simp`，然后 `simp?` 获取最小 simp 引理
- 使用 `native_decide` 处理计算结果
- 使用 `#eval` 评估表达式
- 使用 `norm_cast` 进行类型转换
- 使用 `apply?` 查找适用的引理
- 如果 `decide` 超时，不要增加 `maxHeartbeats`，而是使用数学推理和 Mathlib 引理编写符号证明

### 输出信号
Runner 通过这些信号控制会话循环：
- `END_REASON:COMPLETE` - 文件无 sorry 且编译无错误
- `END_REASON:LIMIT` - 达到轮次限制或仍有 sorry/错误

## 子代理架构模式

系统支持多代理协作模式：
1. **协调器 (Coordinator)**：整体协调，读取蓝图，分配任务
2. **蓝图代理 (Blueprint Agent)**：使用 Gemini/GPT 细化数学蓝图
3. **草图代理 (Sketch Agent)**：将非形式化语句形式化为 Lean 代码
4. **证明代理 (Proof Agent)**：证明具体的引理和定理

## Lean LSP 工具使用

### 关键工具
- `lean_file_outline` - 文件大纲（导入、声明）
- `lean_local_search` - 快速确认声明存在
- `lean_goal` - 查看证明状态
- `lean_diagnostic_messages` - 验证文件编译
- `lean_leandex` - 语义搜索定理
- `lean_loogle` - 按表达式搜索
- `lean_leanfinder` - 基于概念搜索
- `lean_state_search` - 基于证明状态搜索

### 使用原则
- 所有行号和列号都是从 1 开始索引的
- 在每次文件编辑前都要分析/搜索上下文
- 优先使用 `lean_diagnostic_messages` 而不是 `lake build` 进行验证

## 环境变量

```bash
# .env 配置示例
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=sk-...
export API_TIMEOUT_MS=600000
export ANTHROPIC_MODEL=deepseek-chat
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

## 重要文件

- [scripts/runner.py](scripts/runner.py) - 核心会话循环逻辑
- [scripts/task.py](scripts/task.py) - 任务元数据和结果类型
- [prompts/prompt_complete_file.txt](prompts/prompt_complete_file.txt) - 标准提示模板
- [tutorial/usage.md](tutorial/usage.md) - 详细使用指南
- [tutorial/setup.md](tutorial/setup.md) - 环境设置指南
