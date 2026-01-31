# CLAUDE.md（中文）

本文件用于在仓库中为 Claude Code（claude.ai/code）提供协作说明。

## 项目概述

**Numina-Lean-Agent** 是基于 Claude Code 的 Lean 4 形式化定理证明智能体系统，主要特性：
- 自动定理证明：使用 Claude AI 自动完成 Lean 4 数学定理证明
- 多模式运行：支持单文件、批量与文件夹扫描
- 智能提示：提供不同难度的提示模板
- 子代理架构：协调器、蓝图代理、草图代理、证明代理协同
- 工具链集成：通过 MCP 与 Lean LSP 深度集成

**关键成果：**
- 证明 Putnam 2025 竞赛全部 12 题
- 完成 “Effective Brascamp-Lieb inequalities” 的论文级形式化
- MiniF2F 基准表现优秀

## 系统架构

### 核心流程
1. 初始化：加载任务配置与提示模板
2. 会话循环：运行 Claude 代理，逐轮检查进度
3. 验证：使用 `lean_diagnostic_messages` 校验文件
4. 提交：可选每轮 git 提交记录
5. 结果收集：保存 JSON 结果与 MCP 日志

### 目录结构
```
scripts/                    # 核心 Python 脚本
  run_claude.py            # CLI 入口（run/batch/from-folder）
  runner.py                # 会话管理与执行逻辑
  task.py                  # 任务元数据与结果类型
  lean_checker.py          # Lean 文件验证工具
  statement_tracker.py     # 陈述变化跟踪
  mcp_stats.py             # MCP 日志分析
  extract_sublemmas.py     # 子引理提取

leanproblems/              # Lean 4 项目与题目
  Minif2f/                 # MiniF2F 基准
  Putnam2025/              # Putnam 2025 12 道题
  Leanproblems/            # 项目模块
  lakefile.toml            # Lake 构建配置（mathlib v4.26.0）
  lean-toolchain           # Lean 版本配置 (v4.26.0)
  lake-manifest.json       # 依赖清单

prompts/                   # Prompt 模板体系
  prompt_complete_file.txt # 标准完成模式
  prompt_hard_mode.txt     # 困难模式
  prompt_medium_mode.txt   # 中等模式
  docs/                    # 子代理模式文档
    prompts/               # 代理指令
      common.md            # 共享规则
      coordinator.md       # 协调器
      blueprint_agent.md   # 蓝图代理
      sketch_agent.md      # 草图代理
      proof_agent.md       # 证明代理
    technique/             # 设计文档

config/                    # 批量运行配置
  config_minif2f.yaml      # MiniF2F 配置

tutorial/                  # 安装与使用指南
  setup.md                 # 环境配置
  usage.md                 # 使用说明
  setup.sh                 # 自动安装脚本
  myproject/               # 示例项目
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
# 单文件
python -m scripts.run_claude run leanproblems/Minif2f/mathd_algebra_478.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5

# 批量（配置文件）
python -m scripts.run_claude batch config/config_minif2f.yaml

# 文件夹内所有 .lean
python -m scripts.run_claude from-folder leanproblems/Minif2f \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5

# 并行
python -m scripts.run_claude batch config/config_minif2f.yaml --parallel --max-workers 4
```

### MCP 配置
MCP 配置与工作目录绑定，需在目标目录添加：
```bash
cd leanproblems
claude mcp add lean-lsp -- /absolute/path/to/lean-lsp-mcp/numina-lean-mcp.sh
claude mcp list
```

## 配置系统

### YAML 示例
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
  git_commit: false

tasks:
  - target_path: leanproblems/Minif2f/algebra_sqineq_2atp2bpge2ab.lean
    mcp_log_name: algebra_sqineq_2atp2bpge2ab
  - target_path: leanproblems/Minif2f/imo_1964_p1.lean
    mcp_log_name: imo_1964_p1
    max_rounds: 5
```

### 继承规则
- `defaults` 定义默认值
- 任务可覆盖任意字段
- 最终配置 = `defaults` + 任务覆盖

## 工作流程与约定

1. **无公理政策**：禁止 `axiom`，允许最小粒度 `sorry`
2. **验证**：每次修改后用 `lean_diagnostic_messages`
3. **工具优先级**：优先 `simp`、`native_decide`、`norm_cast`
4. **蓝图同步**：在子代理模式下 `BLUEPRINT.md` 为单一事实来源

### 提示关键指令
- 使用 `lean_diagnostic_messages` 验证
- 优先 `simp`，再 `simp?`
- 使用 `native_decide` 处理计算
- `#eval` 评估表达式
- `norm_cast` 做类型转换
- `apply?` 查找引理
- 若 `decide` 超时，不增加 `maxHeartbeats`，改写符号证明

### 结束信号
- `END_REASON:COMPLETE`：无 sorry 且编译通过
- `END_REASON:LIMIT`：达轮次或仍有错误/sorry

## 子代理模式
- **Coordinator**：总体协调、选目标
- **Blueprint Agent**：用 Gemini 细化蓝图
- **Sketch Agent**：形式化陈述
- **Proof Agent**：完成证明

## Lean LSP 工具
- `lean_file_outline`、`lean_local_search`、`lean_goal`、`lean_diagnostic_messages`、`lean_leandex`、`lean_loogle`、`lean_leanfinder`、`lean_state_search`
- 行列号从 1 开始
- 每次编辑前先分析/搜索
- 验证优先用 `lean_diagnostic_messages`，避免 `lake build`

## 环境变量示例
```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=sk-...
export API_TIMEOUT_MS=600000
export ANTHROPIC_MODEL=deepseek-chat
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

## 重要文件
- scripts/runner.py — 核心会话循环
- scripts/task.py — 任务元数据与结果
- prompts/prompt_complete_file.txt — 标准提示模板
- tutorial/usage.md — 使用指南
- tutorial/setup.md — 环境指南
