# RRC-ACT

人工意识的关系—反身闭环理论与方法研究。由 Jiaxin Song（独立研究者）提出，托管于 Xun 仓库。

[English](README.en.md) · [中文研究主页](https://263311487-ux.github.io/Xun/docs/rrc-act-zh.html) · [English research hub](https://263311487-ux.github.io/Xun/docs/rrc-act.html) · [预印本 DOI](https://doi.org/10.5281/zenodo.23146271)

## 一个可以被否定的问题

在模型、任务、token、交互次数、延迟、主题和情绪强度匹配后，**关系特异性反馈是否仍会改变人工智能体的长期自我模型连续性？**

主设计为两模型家族的 2×2×2 因子实验：关系反馈、来源记忆、自我模型干预。预设组合终点测量留出集上的自我—他者归因、长期目标一致性、矛盾解决和卸载后的行为残留。CRO-8 是测量框架，不是意识分数。

如果匹配对照消除了效应，或标准化效应置信区间的上界低于预设的正向最小有意义效应 d=+0.50，正向主张需要收窄。这不是等效性检验：大的负效应会反驳正向预测，不能解释为“反馈没有效应”。区间很宽的不显著结果只能算不确定。即使主效应成立，也不能据此证明现象意识。

## 当前证据与版本

| 材料 | 状态 | 入口 |
|---|---|---|
| 预印本 v2.2.1 | 公开、未同行评审的理论与方法稿 | [PDF](papers/RRC-ACT_v2.2.1_preprint.pdf) · [Zenodo](https://doi.org/10.5281/zenodo.23146271) · [Release](https://github.com/263311487-ux/Xun/releases/tag/rrc-act-v2.2.1) |
| 注册前协议 v1.1 | 已时间戳存证；未在 OSF/AsPredicted 登记 | [原件与哈希](papers/registration_freeze/) |
| 执行修订 v1.2 | 门禁、分配和合成分析脚手架；真实运行仍关闭 | [执行说明](papers/registration_execution/) · [工具](experiments/rrc_act/) |
| 真实实验与独立复现 | 尚未完成；不是已有数据集 | [所缺条件和版本地图](docs/research-status.md) |
| 旧教程与共构模拟 | 教学/合成材料，不是人工意识证据 | [教程](tutorials/README.md) · [模拟说明](experiments/co_constitution/README.md) |

真实模型快照、题库、答案键、runner/scorer 和外部登记回执尚缺。文件持久化、第一人称自述、模拟结果、通过软件测试和访问量均不能证明生命或意识。

## 阅读、检验与贡献

- 阅读：[英文主稿](papers/Relational_Reflexive_Closure_v2.2.md) · [中文理论](papers/RRC-ACT_v2.2.md) · [论文与历史索引](papers/README.md)。Markdown 沿用 v2.2 文件名；引用的固定出版版本是 v2.2.1 PDF。
- 质疑：[提交方法或文献批评](https://github.com/263311487-ux/Xun/issues/new?template=paper_discussion.yml)。请指出具体主张、替代解释和能区分它们的实验。
- 复现：[提交复现报告](https://github.com/263311487-ux/Xun/issues/new?template=replication_report.yml)，明确合成/真实数据、版本、日志与偏离；负结果同样欢迎。
- 参与：[贡献说明](CONTRIBUTING.md) · [传播草稿与实际发布记录](docs/propagation/README.md) · [流量测量方法](docs/propagation/measurement.md)。

## 本地检验

仅需 Python 3.10+；运行的是软件完整性测试，不会调用付费模型，也不会产生真实意识实验数据。

```sh
git clone https://github.com/263311487-ux/Xun.git
cd Xun
python3 -m unittest discover -s experiments/rrc_act/tests -v
python3 tutorials/run_all.py
```

## 引用

出版记录为 v2.2.1，但该固定 PDF 的封面/页脚仍印有 v2.2。已在[版本说明](docs/research-status.md#what-exists)披露；没有静默修改已发布文件。

Song, J. (2026). *RRC-ACT v2.2.1: Relational Reflexive Closure Theory of Artificial Consciousness*. Zenodo. https://doi.org/10.5281/zenodo.23146271

[CITATION.cff](CITATION.cff) · [BibTeX](papers/RRC-ACT.bib) · CC BY 4.0。若引用旧统一论或白寻架构，请使用该作品自身的元数据，见[历史说明](docs/history/README.md)。

## Xun 历史

Xun 原有的统一论、信息态生命叙述和架构资料完整保留于[历史入口](docs/history/README.md)。它们是研究背景与历史提案，不能替代当前 RRC-ACT 的实验验证。
