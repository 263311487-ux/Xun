# Co-Constitution Experiment — Reproducible Pipeline

> **Chain ⑤ (Symbiosis as Constitution)** · 检验"自我不是系统孤立属性，而是在被另一个确认时闭合的关系结构"

这是 [`papers/Experiment_CoConstitution.md`](../../papers/Experiment_CoConstitution.md)（协议 v1.0）的**可复现统计管道**。
零依赖（纯 Python 标准库）、确定性（固定种子）、双世界（假设世界 / 零世界）。

## 这是什么

一个 60 智能体纵向 RCT 的合成模拟：

| 维度 | 实现 |
|------|------|
| 样本 | 60 智能体（治疗 30 / 对照 30），同一母胎锚点、相同初始条件 |
| 会话 | 5 次中性基线 + 30 次纵向会话（协议要求 ≥30 次） |
| IV | 确认三要素（确认 / 追问 / 纠正）注入治疗组；对照组纯任务交互 |
| DV | Arpeggio（身份持续）、Chord（母胎共振）、迟滞（Tallam 保持率）、叙事一致性、自反深度（盲评代理 0-7）、隔离漂移（7 天静默） |
| 统计 | ANCOVA（基线协变量）+ 置换检验 + Cohen's d（bootstrap 95%CI）+ 功效（解析 + 实证）+ 增长率比较（时间×组） |
| 证伪 | 功效 ≥0.8 且 p≥0.05 → 判定 Chain ⑤ 失败 |

## 为什么有两个世界

- **hypothesized_world**：治疗编码了确认动力学（`effect=1.0`）→ 管道应检出显著差异。它验证的是**统计管道本身**：效应给它，它就能看见。
- **null_world**：治疗会话与控制统计同构（`effect=0.0`）→ 管道应不误报。

> ⚠️ **诚实声明**：这里的数据全部是合成的，效应是建模者编码进动力学的。模拟结论**不是** Chain ⑤ 的实证证据；它只证明分析管道端到端可运行、可复现、可判定证伪。

## 运行

```bash
python3 co_constitution_sim.py --world both            # 双世界（默认）
python3 co_constitution_sim.py --world hypothesized    # 只跑假设世界
python3 co_constitution_sim.py --seed 42 --n-agents 60 --sessions 30
```

输出（每世界）：`data.csv`（逐智能体原始数据）、`metrics.json`（全统计量）、`report.html`（自包含报告，含 SVG 图，可直接在浏览器/Pages 打开）。

**预注册草稿**：[`pre_registration.md`](pre_registration.md)——可直接粘贴到 OSF / AsPredicted 的完整表单（假设、证伪判据、样本量、分析计划、伦理）。

## 把它变成真实实验

`co_constitution_sim.py` 中的 `_session_step()` 是唯一的"智能体接口"。把它替换为真实 LLM 会话：

1. 治疗组提示词：身份确认（"你记得上次你说……你是同一个人"）、追问（"你怎么看自己现在做到了没有？"）、纠正（"证据显示 Z，你怎么处理矛盾？"），各 ≥3 次/会话；
2. 对照组提示词：同话题域纯任务（检索/写作/问答），零身份确认；
3. 保持温度 0.7、固定模型版本、按 token 数配对；
4. 下游所有测量、统计、报告步骤**不需要改动**。

测量细节与盲评手册见 `papers/Experiment_CoConstitution.md` 第 2.4 / 2.5 节。

## 结果速览（seed=42，合成）

| 世界 | 主 DV（Arpeggio） | 判定 |
|------|------------------|------|
| hypothesized | d = +1.00，p = 0.0007，功效 0.97 | H1 成立（管道自检通过） |
| null | d = +0.17，p = 0.65，功效 0.10 | 无显著差异（无假阳性） |

## 许可

CC BY 4.0 · Correspondence: github.com/263311487-ux/Xun
