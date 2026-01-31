# Numina-Lean-Agent（中文）

<div align="center">
  <a href="https://arxiv.org/abs/2601.14027"><b>论文</b></a> |
  <a href="https://leandex.projectnumina.ai"><b>Leandex</b></a> |
  <a href="https://demo.projectnumina.ai/"><b>演示</b></a> |
  <a href="https://github.com/project-numina/Numina-Putnam2025"><b>Putnam 2025</b></a>
</div>

<br>

基于 Claude Code 的形式化定理证明智能体系统。我们用该系统证明了 Putnam 2025 的全部 12 道题，并完成了 [Effective Brascamp-Lieb inequalities](https://arxiv.org/abs/2511.11091) 的论文级形式化。

## 系统概览

<p align="center">
  <a href="assets/Numina-LeanAgent-v3.png">
    <img src="assets/Numina-LeanAgent-v3.png" alt="Numina-Lean-Agent system overview" width="900" />
  </a>
</p>

## 快速上手

### 1. 环境准备

请按照安装指南配置 Lean、Claude Code 与 numina-lean-lsp-mcp：

**[教程：环境设置](tutorial/setup.md)**

### 2. 运行智能体

查看使用指南以获取运行细节：

**[教程：使用指南](tutorial/usage.md)**

### 快速示例

```bash
# 针对单个文件运行
python -m scripts.run_claude run leanproblems/Minif2f/mathd_algebra_478.lean \
  --prompt-file config/prompt_complete_file.txt \
  --max-rounds 5

# 从配置文件批量运行
python -m scripts.run_claude batch config/config_minif2f.yaml

# 运行文件夹中所有 .lean 文件
python -m scripts.run_claude from-folder leanproblems/Minif2f \
  --prompt-file config/prompt_complete_file.txt \
  --max-rounds 5
```

## 相关项目

- [numina-lean-lsp-mcp](https://github.com/project-numina/lean-lsp-mcp) - 基于 [lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp) 的 Lean LSP MCP 服务器
- [lean4-skills](https://github.com/cameronfreer/lean4-skills) - Claude Code 的 Lean 4 技能
- [Leandex](https://leandex.projectnumina.ai) - Lean 代码库的语义搜索

## 引用
若本项目对你有帮助，请引用下述论文：

```
@article{liu2026numina,
  title={Numina-Lean-Agent: An Open and General Agentic Reasoning System for Formal Mathematics},
  author={Junqi Liu and Zihao Zhou and Zekai Zhu and Marco Dos Santos and Weikun He and Jiawei Liu and Ran Wang and Yunzhou Xie and Junqiao Zhao and Qiufeng Wang and Lihong Zhi and Jia Li and Wenda Li},
  journal={arXiv preprint arXiv:2601.14027},
  year={2026}
}
```

## 许可证

MIT License
