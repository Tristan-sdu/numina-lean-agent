# 系统工作流图（中文）

> Lean 定理证明系统的可视化流程

---

## 关键规则（摘要）

| 规则 | 执行 |
|---|---|
| **必须用子代理** | 协调器绝不直接做证明 |
| **Sorry 协议** | 代码需可编译，`sorry` 仅放最小卡点 |
| **禁止 Axiom** | 永不使用 `axiom`，只用 `sorry` |
| **蓝图同步** | 一有进展立即更新 BLUEPRINT |
| **Gemini 优先** | Proof Agent 在 0 阶段必须先咨询 Gemini |

---

## 高层流程

```
会话开始 → 读 BLUEPRINT → 选目标 → 检查依赖 → 评估复杂度 → 选子代理
简单→Proof / 中等→Sketch→Proof / 复杂→Blueprint→Sketch→Proof
```

---

## 代理编排模式

- **简单**：Coordinator → Proof Agent（tmp 文件、强制尝试预算、Gemini 检查点）→ 更新蓝图
- **中等**：Coordinator → Sketch Agent（形式化+状态注释+蓝图 file:line）→ Proof Agent → 更新蓝图
- **复杂**：Coordinator → Blueprint Agent（Gemini、拆分、更新依赖）→ 各子引理按依赖顺序 Sketch → Proof → 更新蓝图

---

## Proof Agent 详细流程

1. 在原文件状态注释写明 tmp 文件
2. 创建 `tmp_<lemma>.lean`
3. **Checkpoint 0**：先问 Gemini 获取策略/引理
4. 尝试循环（预算 20-50，含 5 类方法；在 2/4/8/16/32 处再次问 Gemini）
5. 每轮可用 `lean_multi_attempt` 等；每 10 次更新状态注释与蓝图
6. 成功：复制回原文件，删 tmp，状态 done；预算耗尽：标记 HARD

---

## 五类方法（每类建议 ≥10 次）

1. **库搜索**：leandex（多措辞）→ loogle（类型模式）→ local_search
2. **直接战术**：先 hint → grind，再 omega/linarith/ring/simp/aesop 等
3. **结构手法**：归纳、分情况、反证/对偶
4. **Term 模式**：`exact fun x => ...`、构造 exists/record、直接套引理
5. **分解**：`have` / `suffices` / 提炼辅助引理

---

## Gemini 检查点

- 0（写代码前）、2、4、8、16、32 次尝试：都必须咨询 Gemini，获取策略/分解/库提示/优化建议。

---

## 数据流

- BLUEPRINT.md：单一事实源，记录状态/依赖/尝试
- Coordinator 读蓝图，按依赖拓扑选目标，调用子代理
- Blueprint/Sketch/Proof 代理按职责更新文件与蓝图；所有日志写入 `docs/agent_logs/raw/`

---

## 状态机

```
todo → partial → done
        │
        └─ budget 用尽 → todo | HARD → 可能交给 Blueprint Agent 拆分
```

状态注释示例：
```
/- (by claude)
State: todo | partial | done
Priority: 1-5
Attempts: N / M
tmp file: <path>
-/
lemma name : statement := by ...
```

---

## 依赖与蓝图格式

- 依赖拓扑排序：先依赖，后依赖者
- 蓝图条目：`label`、`uses`、`file:line`、`status`、`attempts`、statement、proof
- 拆分后需更新依赖图与排序
