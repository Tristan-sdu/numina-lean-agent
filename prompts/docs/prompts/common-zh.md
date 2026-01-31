# 通用代理规则（中文）

> **目的**：Lean 定理证明系统中所有代理共享的规则

---

## 1. 禁用公理

**绝不用 `axiom`，需要时使用 `sorry`。**

- `axiom` 破坏可信度；`sorry` 显式标记空缺且可编译。
- 留下的 `sorry` 必须是**最小卡点**，其余步骤要完成。
- 退出前用 `lean_diagnostic_messages`，确保无 severity-1 错误。

示例：
```lean
-- 好的做法
theorem foo : P := by
  have h1 : A := by simp
  have h2 : B := sorry  -- 仅卡在此处
  exact combine h1 h2
```

---

## 2. 蓝图同步

**BLUEPRINT.md 是唯一真源，任何进展必须立即更新，不得延迟或批量。**

- 完成/失败/状态变更/尝试数变化都要即时写入。
- 结束会话前再次核对蓝图与实际一致。

---

## 3. 状态注释格式

每个 lemma/theorem 必须有状态注释：
```lean
/- (by claude)
State: done | partial | todo | HARD
Priority: 1-5
Attempts: N / M
tmp file: <path_or_empty>
-/
lemma name : statement := by
  ...
```
- State：✅ done / 🔄 partial / ❌ todo / HARD（预算耗尽）
- Priority：1 高 → 5 低
- Attempts：当前 / 预算（20–50）
- tmp file：Proof Agent 工作的临时文件路径

---

## 4. 临时文件流程（Proof Agent）

1. 先在原文件状态注释写明 tmp 文件
2. 在同目录创建 `tmp_<lemma>.lean`，import 原文件
3. 所有尝试在 tmp 内进行
4. 成功后复制回原文件、更新状态、删除 tmp

---

## 5. 工具优先级

### 搜索（按顺序）
1. **leandex**：语义 / 自然语言
2. **loogle**：类型模式匹配
3. **local_search**：本地快速确认

若 mathlib 未找到：拆成小步自己证，构造辅助引理。

### 自动化（首选）
1. **hint**（先）
2. **grind**（次）
3. 手动分析（再）

常用战术：`hint`/`grind`/`omega`/`linarith`/`aesop`/`simp`/`rfl`/`ring`/`norm_cast`。

---

## 6. 错误处理流程

1. 先试 `hint`；若提示 🎉，直接用。
2. 再试 `grind`。
3. 若仍失败：读报错 → 查 goal → leandex/loogle 搜索 → 选战术。

---

## 7. 代理日志（强制）

每次执行必须写日志到 `docs/agent_logs/raw/`，命名：`<agent>_<YYYYMMDD>_<HHMMSS>.md`。

必含：
1. Meta（类型、时间、目标、文件）
2. TODO 表（状态更新）
3. 时间序日志（追加）
4. Summary（结果、尝试、关键方法/引理）
5. Learnings（编号列表）

---

## 8. 上下文控制

- 使用临时文件与子代理隔离上下文。
- 返回协调器的信息简洁；细节写日志。

---

## 9. 注释需简洁

- 代码中避免长注释；每块 1–2 行即可。
- 详细说明写蓝图或日志。

---

## 禁止事项速查

- 不用 `axiom`
- 不跳过蓝图更新
- 不在原文件大量堆注释
- 不用 `lake build` 做单文件验证（用 `lean_diagnostic_messages`）
