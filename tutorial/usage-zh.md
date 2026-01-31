# run_claude 使用指南（中文）

`run_claude` 是在 Lean 定理证明任务上运行 Claude 的命令行工具。

## 命令概览

```bash
python -m scripts.run_claude <command> [options]
```

> **性能提示（推荐）：** 在 Lean 项目目录先执行一次构建，以避免首次 MCP/LSP 启动缓慢：
>
> ```bash
> lake update
> lake exe cache get
> lake build
> ```
>
> 若跳过，首次启动可能因依赖编译/索引而变慢。

> **MCP 设置（lean-lsp-mcp，必需）：** MCP 配置与目录绑定。若运行时使用 `--cwd /path/to/project`，必须在同一目录（或父目录）执行过 `claude mcp add`：
>
> 若未显式指定 `--cwd`，生效目录即你运行命令的当前目录 `.`，也需在该目录（或父目录）添加 MCP。
>
> ```bash
> cd /path/to/project
> claude mcp add lean-lsp -- /absolute/path/to/numina-lean-mcp.sh
> ```
>
> 验证：
>
> ```bash
> claude mcp list
> ```

支持三类命令：
- `run`：运行单个任务
- `batch`：从配置文件批量运行
- `from-folder`：扫描文件夹内的 `.lean` 并逐个运行

---

## 命令

### 1. `run` — 单任务

```bash
python -m scripts.run_claude run <target> [options]
```

**参数：**

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `target` | str | 必填 | 目标路径（文件或文件夹） |
| `--task-type` | str | `auto` | 任务类型：`file` / `folder` / `auto` |
| `--prompt` | str | - | 直接提供提示词 |
| `--prompt-file` | str | - | 从文件读取提示词（与 `--prompt` 互斥） |
| `--cwd` | str | `.` | Claude 工作目录（默认当前目录） |
| `--max-rounds` | int | `20` | 最大轮数（继续次数上限） |
| `--check` | bool | `True` | 完成后是否检查 Lean 文件 |
| `--sleep` | float | `1.0` | 轮次间休眠（秒） |
| `--result-dir` | str | - | 结果输出目录（JSON） |
| `--mcp-log-name` | str | - | MCP 日志名 |
| `--permission-mode` | str | `bypassPermissions` | 权限模式 |
| `--json-output` | bool | `False` | 是否使用 JSON 输出格式 |

> 提示：`--cwd` 与 MCP 目录绑定，参考前述 MCP 设置。

**示例：**

```bash
# 单文件
python -m scripts.run_claude run /path/to/file.lean --prompt-file prompt.txt

# 文件夹
python -m scripts.run_claude run /path/to/folder --task-type folder --prompt "..."
```

---

### 2. `batch` — 批量任务

```bash
python -m scripts.run_claude batch <config_file> [options]
```

**参数：**

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `config_file` | str | 必填 | 配置文件路径（YAML/JSON） |
| `--parallel` | bool | `False` | 是否并行运行 |
| `--max-workers` | int | `1` | 并行工作线程数 |

**示例：**

```bash
# 顺序执行
python -m scripts.run_claude batch config/config_minif2f.yaml

# 并行执行
python -m scripts.run_claude batch config/config_minif2f.yaml --parallel --max-workers 4
```

---

### 3. `from-folder` — 按文件夹生成任务

扫描文件夹内所有 `.lean`，每个文件生成一个任务。

```bash
python -m scripts.run_claude from-folder <folder> [options]
```

**参数：**

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `folder` | str | 必填 | 含 `.lean` 文件的目录 |
| `--prompt` | str | - | 直接提示词 |
| `--prompt-file` | str | - | 提示词文件 |
| `--cwd` | str | `.` | Claude 工作目录 |
| `--max-rounds` | int | `20` | 最大轮数 |
| `--check` | bool | `True` | 是否完成后检查 |
| `--sleep` | float | `1.0` | 轮次间休眠 |
| `--result-dir` | str | - | 结果目录 |
| `--permission-mode` | str | `bypassPermissions` | 权限模式 |
| `--parallel` | bool | `False` | 是否并行 |
| `--max-workers` | int | `1` | 并行线程数 |

**示例：**

```bash
# 顺序
python -m scripts.run_claude from-folder leanproblems/Minif2f --prompt-file config/prompt_complete_file.txt

# 并行
python -m scripts.run_claude from-folder leanproblems/Minif2f \
  --prompt-file config/prompt_complete_file.txt \
  --parallel --max-workers 4
```

---

## 配置文件格式（YAML/JSON）

配置包含 `defaults` 与 `tasks` 两部分。

### 参数列表（可用于 defaults/tasks）

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `task_type` | str | - | `file` / `folder` |
| `target_path` | str | - | 目标路径 |
| `prompt` | str | - | 直接提示词 |
| `prompt_file` | str | - | 提示词文件 |
| `cwd` | str | - | 工作目录 |
| `max_rounds` | int | `20` | 最大轮数 |
| `check_after_complete` | bool | `True` | 完成后是否检查 |
| `allow_sorry` | bool | `False` | 是否允许 sorry |
| `sleep_between_rounds` | float | `1.0` | 轮次间休眠 |
| `result_dir` | str | - | 结果目录 |
| `mcp_log_dir` | str | - | MCP 日志目录 |
| `mcp_log_name` | str | - | MCP 日志名 |
| `permission_mode` | str | `bypassPermissions` | 权限模式 |
| `output_format` | str | - | 输出格式（`json` / `None`） |
| `track_statements` | bool | `True` | 是否跟踪陈述变化 |
| `on_statement_change` | str | `warn` | 处理方式：`error` / `warn` |
| `git_commit` | bool | `False` | 是否每轮自动 git commit |

---

## defaults 继承规则

`defaults` 为任务提供默认值，任务可覆盖任何字段：

```
最终配置 = defaults + task（任务优先）
```

**示例：**
```yaml
defaults:
  task_type: file
  prompt_file: config/prompt_complete_file.txt
  max_rounds: 2

tasks:
  - target_path: file1.lean   # 继承 max_rounds=2
  - target_path: file2.lean
    max_rounds: 5              # 覆盖为 5
```

---

## MiniF2F 示例

### 配置文件 `config/config_minif2f.yaml`

```yaml
defaults:
  task_type: file
  prompt_file: config/prompt_complete_file.txt
  cwd: .
  check_after_complete: true
  permission_mode: bypassPermissions
  result_dir: results/minif2f
  mcp_log_dir: mcp_logs/minif2f
  max_rounds: 2

tasks:
  - target_path: leanproblems/Minif2f/algebra_sqineq_2atp2bpge2ab.lean
    mcp_log_name: algebra_sqineq_2atp2bpge2ab
  - target_path: leanproblems/Minif2f/amc12a_2021_p7.lean
    mcp_log_name: amc12a_2021_p7
  - target_path: leanproblems/Minif2f/mathd_algebra_478.lean
    mcp_log_name: mathd_algebra_478
  - target_path: leanproblems/Minif2f/mathd_numbertheory_284.lean
    mcp_log_name: mathd_numbertheory_284
  - target_path: leanproblems/Minif2f/imo_1964_p1.lean
    mcp_log_name: imo_1964_p1
    max_rounds: 5  # 难度较高，提升轮数
```

### 运行命令

**方式 1：batch（推荐精细控制）**
```bash
python -m scripts.run_claude batch config/config_minif2f.yaml
```

**方式 2：from-folder（简单批量）**
```bash
python -m scripts.run_claude from-folder leanproblems/Minif2f \
  --prompt-file config/prompt_complete_file.txt \
  --max-rounds 5 \
  --result-dir results/minif2f
```

**并行执行：**
```bash
# batch 并行
python -m scripts.run_claude batch config/config_minif2f.yaml --parallel --max-workers 4

# from-folder 并行
python -m scripts.run_claude from-folder leanproblems/Minif2f \
  --prompt-file config/prompt_complete_file.txt \
  --parallel --max-workers 4
```

---

## Git 自动提交功能

在配置中设置 `git_commit: true` 后，每轮运行结束会自动创建一次 git 提交，便于：
- 跟踪 Claude 的修改过程
- 失败时快速回滚
- 调试与审阅每轮改动

工作机制：
- 每轮结束对目标目录执行 `git add -A && git commit`
- 文件夹任务在目标目录提交；文件任务在父目录提交
- 提交信息包含轮次号

示例：
```yaml
defaults:
  task_type: file
  prompt_file: config/prompt_complete_file.txt
  git_commit: true
  max_rounds: 5

tasks:
  - target_path: leanproblems/Minif2f/imo_1964_p1.lean
```

> 注：该功能仅通过配置文件（batch 命令）启用，CLI 的 `run` / `from-folder` 未提供开关。

---

## 输出

### 结果目录

设置 `result_dir` 时，每个任务会生成 JSON，包含：任务 ID、成功状态、结束原因、轮次、耗时、行数变化、MCP 工具调用统计等。

### MCP 日志

设置 `mcp_log_dir` 与 `mcp_log_name` 时，会在指定目录保存 MCP 服务日志。

### 控制台输出

执行完毕后展示：任务状态（SUCCESS/FAILED）、结束原因（COMPLETE/LIMIT/ERROR）、行数变化、批量统计等。
