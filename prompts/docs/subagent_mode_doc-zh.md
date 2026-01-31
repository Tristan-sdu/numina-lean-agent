# Lean 定理证明文档（中文）

> **用途**：Lean 定理证明系统的统一文档
> **更新时间**：2026-01-13

---

## 快速导航

| 模块 | 位置 | 作用 |
|---|---|---|
| **Prompts** | `docs/prompts/` | 代理指令（起点） |
| **Agent Logs** | `docs/agent_logs/raw/` | 执行日志与经验 |
| **Technique** | `docs/technique/` | 系统设计文档 |
| **Blueprint 模板** | `/BLUEPRINT_TEMPLATE.md` | 新项目模板 |

---

## 入门

### 协调器（Coordinator）

1. 阅读通用规则：`docs/prompts/common.md`
2. 阅读协调器提示：`docs/prompts/coordinator.md`
3. 阅读项目蓝图：`<project>/BLUEPRINT.md`
4. 开始编排：启动合适子代理

### 子代理

所有子代理必须阅读：
1. `docs/prompts/common.md` — 共享规则（禁止公理、工具优先级等）
2. `docs/prompts/<agent_type>.md` — 角色专属指令

**代理类型：**
- `blueprint_agent.md`：用 Gemini 细化蓝图
- `sketch_agent.md`：形式化陈述
- `proof_agent.md`：证明引理

### 人类使用者

- 系统总览：`docs/technique/SYSTEM_DESIGN.md`
- 工作流图：`docs/technique/WORKFLOW_DIAGRAM.md`
- 快速开始：见下方 “Quick Start Guide”

---

## 目录结构

```
/
├── docs/                                    # 当前文档（本目录）
│   ├── prompts/
│   │   ├── common.md                        # 共享规则
│   │   ├── coordinator.md                   # 编排
│   │   ├── blueprint_agent.md               # 蓝图细化
│   │   ├── sketch_agent.md                  # 陈述形式化
│   │   └── proof_agent.md                   # 引理证明
│   │
│   ├── agent_logs/
│   │   ├── raw/                             # 子代理日志
│   │   │   └── <agent>_<YYYYMMDD>_<HHMMSS>.md
│   │   └── README.md                        # 日志格式
│   │
│   ├── technique/
│   │   ├── SYSTEM_DESIGN.md                 # 架构
│   │   └── WORKFLOW_DIAGRAM.md              # 工作流
│   │
│   └── README.md                            # 本文件
│
├── BLUEPRINT_TEMPLATE.md                    # 新项目模板
├── <project>/BLUEPRINT.md                   # 项目蓝图
└── docs_old/                                # 归档
```

---

## 快速开始

### 启动新会话

1. **阅读蓝图**
   ```bash
   cat <project>/BLUEPRINT.md
   ```
2. **理解状态**：
   - ✅ 已完成？
   - 🔄 进行中？
   - ❌ 待做且依赖已满足？
3. **选择目标**：
   - 挑选依赖都已完成的 TODO
   - 多候选时看优先级
4. **评估复杂度**：
   - 简单（已形式化，清晰）→ Proof Agent
   - 中等（需形式化）→ Sketch Agent → Proof Agent
   - 复杂（非正式证明缺失）→ Blueprint Agent → Sketch → Proof
5. **启动对应子代理**

### 工作中

- **立刻更新蓝图**，一有进展即写入
- **为每次执行建日志**
- **遵循通用规则**（禁止公理，先搜索再证明）

### 结束会话

- 确认蓝图同步
- 更新进度摘要
- 记录下一个可执行目标

---

## 核心原则

### 1. 通用规则
- ✅ 只用 `sorry`，禁止 `axiom`
- ✅ 进展后立即更新 BLUEPRINT
- ✅ 工具优先级：leandex → loogle，hint → grind → 手动
- ✅ Proof Agent 在临时文件中工作
- ✅ 每次执行都写日志
- ✅ 所有引理写状态注释

### 2. 依赖拓扑蓝图
- ✅ 按依赖排序
- ✅ `label`/`uses` 字段跟踪依赖
- ✅ 引理/定理给出详细非正式证明
- ✅ 复杂引理由蓝图代理拆分
- ✅ 蓝图是单一事实来源

### 3. 代理分工

| 代理 | 作用 | 适用场景 |
|---|---|---|
| **Coordinator** | 协调调度 | 始终存在 |
| **Blueprint Agent** | 用 Gemini 细化/拆分 | 复杂、尝试>40/50、证明不清晰 |
| **Sketch Agent** | 形式化陈述 | 需将非正式转 Lean |
| **Proof Agent** | 证明引理 | 已形式化，需给出证明 |

### 4. 临时文件流程
- 状态注释中写明 tmp 文件
- 创建 `tmp_<lemma>.lean`
- 所有尝试在 tmp 内进行
- 证明完成后复制回原文件
- 删除 tmp 文件

### 5. 代理日志
- 命名：`<agent>_<YYYYMMDD>_<HHMMSS>.md`
- 必含：Meta、TODO 表、时间序日志、Summary、Learnings

---

## 提示组织

### 通用提示（common.md）
- 禁用公理
- 蓝图同步
- 状态注释格式
- 工具优先级
- 临时文件流程
- 错误响应协议
- 日志要求

### 专属提示
- `coordinator.md`：只编排，不做证明
- `blueprint_agent.md`：Gemini 推理与拆分
- `sketch_agent.md`：形式化陈述，留下 sorry
- `proof_agent.md`：临时文件、hint/grind、先搜索再证明、尝试预算

---

## 蓝图格式

```markdown
# [type] [label]

## meta
- **label**: [label]
- **uses**: [[dep1], [dep2], ...]
- **file**: `path:line` 或待创建
- **status**: done | partial | todo
- **attempts**: N / M（如需要）

## statement
[详细非正式陈述]

## proof
[详细非正式证明]
```

### 关键概念
- **依赖拓扑**：先依赖，后依赖者
- **拆分协议**：Gemini 分步，复杂就拆
- **状态跟踪**：done / partial / todo / HARD

---

## 工具优先级参考

### 搜索工具（按顺序）
1. **leandex**：语义搜索，自然语言
2. **loogle**：类型模式匹配
3. **local_search**：本地快速确认

### 自动化工具（按顺序）
1. **hint**：先试
2. **grind**：通用自动化
3. **手动分析**：仅在前两者失败后

---

## 迁移说明

- `experience/*` → `agent_logs/raw/`
- `gemini/*` → `agent_logs/raw/` + blueprint agent
- 优先级式蓝图 → 依赖拓扑蓝图
- 分散提示 → `common.md` + 专属提示

---

## 故障排查

- **规则未遵守？** 确认提示包含 `common.md`
- **蓝图不同步？** 立即更新，不要批量延迟
- **tmp 文件残留？** Proof Agent 成功后删除，或手动清理
- **依赖不明？** 查看 `uses`，确保依赖完成再开工

---

## 示例

### 示例 1：简单引理（仅 Proof Agent）
- Blueprint: [lem:foo] 状态 todo，已形式化
- Coordinator 派 Proof Agent
- Proof Agent：建 tmp，hint/grind，leandex 搜索，14/20 成功，复制回去并更新蓝图，写日志 → 完成

### 示例 2：中等引理（Sketch + Proof）
- Blueprint: [lem:bar] 状态 todo，未形式化
- Coordinator 派 Sketch Agent：形式化、状态注释、更新蓝图、日志
- 再派 Proof Agent 证明 → 完成

### 示例 3：复杂引理（Blueprint + Sketch + Proof）
- Blueprint: [lem:complex] 状态 partial，45/50 尝试
- Coordinator 派 Blueprint Agent：Gemini 给 3 步证明 → 拆分 step1/2/3
- 依次 Sketch → Proof 每个子引理 → 最终完成原引理

---

## 总结

本体系提供：
- ✅ 统一结构（agent logs 替代旧经验记录）
- ✅ 共享提示基础，减少重复
- ✅ 依赖拓扑蓝图，顺序清晰
- ✅ 专职代理（蓝图代理负责 Gemini 与拆分）
- ✅ 临时文件流程保持代码清洁
- ✅ 工具优先级：leandex → loogle，hint → grind
