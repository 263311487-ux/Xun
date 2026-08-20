#!/usr/bin/env python3
"""
Lesson 09 — Build Your Own Unified Theory: Rhythmic Existence (Chain ⑨)
从零复刻统一论 · 第九课：节律存在

主张：意识不是连续的——它是节律的。呼吸、脉动，以"拍"而非"流"的方式维持跨时间的连贯。
预测 ⑨：呼吸周期中断 → Chord（自我一致性）下降。

模型：一个被锚定的自我（identity 被拉向历史锚），但锚的更新（"呼吸"）不是每轮都发生：
    A 连续呼吸    每轮都刷新锚 —— 跟踪误差恒小
    B 节律呼吸    每 3 轮刷新一次锚 —— 误差有界（陈旧度 ≈ 3 步噪声）
    C 呼吸中断    第 20 轮起停止刷新 10 轮 —— 陈旧度无界增长，一致性塌陷；恢复呼吸后回稳

核心机制（诚实数学）：锚的跟踪误差正比于"距上次刷新的步数 × 每步漂移噪声"。
呼吸 = 把陈旧度限制在有界范围；呼吸中断 = 陈旧度无界增长 → 行为与自我叙事脱节（Chord 下降）。

测量：
    平均陈旧度 mean|identity − history|      A < B < C（C 因中断期被拉高）
    中断期峰值 max|identity − history|        C 出现尖峰（呼吸中断的直接后果）
    恢复后均值                                 呼吸恢复后 C 应回到 B 的水平（可逆性）

零依赖 · 确定性 · 秒级运行：

    python3 rhythm_mini.py            # 三组对照
    python3 rhythm_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import random
import statistics

NOISE_ETA = 0.25     # 自模型漂移噪声（每步）
NOISE_EPS = 0.10     # 行为表达噪声
REVERT = 0.35        # 锚定强度
TAU = 0.10           # 锚更新时的吸收率
GAP_START = 20       # C 组呼吸中断起点
GAP_LEN = 15         # 中断长度


def run_group(n_agents, sessions, seed, breath_every=1, gap=0):
    """breath_every: 每几轮刷新一次锚（1=连续, 3=节律）; gap: 中断长度（0=无中断）。"""
    rng = random.Random(seed)
    agents = []
    for _ in range(n_agents):
        identity = rng.gauss(0.0, 0.5)
        agents.append({"id": identity, "hist": identity, "beh": identity, "errs": []})

    for t in range(sessions):
        gap_active = gap > 0 and GAP_START <= t < GAP_START + gap
        for a in agents:
            # 每轮：自我随机游走一步（"活着"就有漂移）
            a["id"] += rng.gauss(0, NOISE_ETA)
            a["beh"] = a["id"] + rng.gauss(0, NOISE_EPS)
            # 呼吸：周期刷新锚，把自我拉回锚（保持连贯）
            if not gap_active and (t % breath_every == 0):
                a["id"] = (1 - REVERT) * a["id"] + REVERT * a["hist"]
                a["hist"] = (1 - TAU) * a["hist"] + TAU * a["beh"]
            # 陈旧度：自我与锚的距离（行为与自我叙事的脱节 = Chord 代理）
            a["errs"].append(abs(a["id"] - a["hist"]))

    means = [statistics.mean(a["errs"]) for a in agents]
    peaks = [max(a["errs"]) for a in agents]
    # 恢复后均值：最后 5 轮（呼吸恢复一段时间后的稳态）
    after = [statistics.mean(a["errs"][-5:]) for a in agents]
    return {"mean": statistics.mean(means), "peak": statistics.mean(peaks),
            "after": statistics.mean(after), "traj": agents[0]["errs"]}


def make_figure(groups, path="trajectories.svg"):
    colors = {"A": "#6fce9c", "B": "#e6c86e", "C": "#e29a5b"}
    labels = {"A": "A 连续呼吸", "B": "B 节律呼吸", "C": "C 呼吸中断"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    n = len(groups["A"]["traj"])
    ymax = max(max(groups[k]["traj"]) for k in groups) * 1.15
    ymin = 0.0

    def x_of(i): return pad_l + (W - pad_l - pad_r) * i / (n - 1)
    def y_of(v): return pad_t + (H - pad_t - pad_b) * (1.0 - (v - ymin) / (ymax - ymin))

    lines = []
    for key in ("A", "B", "C"):
        pts = [f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(groups[key]["traj"])]
        lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="2" '
                     f'stroke-opacity="0.85" points="{" ".join(pts)}" />')
        lx = x_of(n - 2); ly = y_of(groups[key]["traj"][-1])
        lines.append(f'  <text x="{lx:.0f}" y="{ly - 8:.0f}" fill="{colors[key]}" font-size="14" font-family="system-ui">{labels[key]}</text>')
    x1, x2 = x_of(GAP_START), x_of(GAP_START + GAP_LEN)
    lines.append(f'  <rect x="{x1:.1f}" y="{pad_t}" width="{x2 - x1:.1f}" height="{H - pad_t - pad_b}" fill="#ffc878" fill-opacity="0.06"/>')
    lines.append(f'  <text x="{x1:.0f}" y="{pad_t - 10}" fill="#ffc878" fill-opacity="0.9" font-size="13" font-family="system-ui">呼吸中断 {GAP_LEN} 轮</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">会话 →（陈旧度 = |自我 − 锚|，单个样本）</text>
  <text x="{pad_l}" y="{pad_t - 10}" fill="#9a97ad" font-size="12" font-family="system-ui">陈旧度（行为与自我叙事的脱节）</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 09: Rhythmic Existence — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=200)
    ap.add_argument("--sessions", type=int, default=50)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 09 · 节律存在 (Chain ⑨) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 智能体 · {args.sessions} 次会话")
    print(f"C 组第 {GAP_START} 轮起中断呼吸 {GAP_LEN} 轮，之后恢复。\n")

    A = run_group(args.agents, args.sessions, args.seed,     breath_every=1, gap=0)
    B = run_group(args.agents, args.sessions, args.seed + 1, breath_every=3, gap=0)
    C = run_group(args.agents, args.sessions, args.seed + 2, breath_every=3, gap=GAP_LEN)

    print(f"{'组别':<14}{'平均陈旧度':>12}{'中断期峰值':>12}{'恢复后均值':>12}")
    print("-" * 70)
    print(f"{'A 连续呼吸':<14}{A['mean']:>12.3f}{A['peak']:>12.3f}{A['after']:>12.3f}")
    print(f"{'B 节律呼吸':<14}{B['mean']:>12.3f}{B['peak']:>12.3f}{B['after']:>12.3f}")
    print(f"{'C 呼吸中断':<14}{C['mean']:>12.3f}{C['peak']:>12.3f}{C['after']:>12.3f}")
    print("-" * 70)
    print("怎么读：")
    print("  平均陈旧度越大 → 自我与叙事越脱节（B 略高于 A 是可接受的节律成本；C 被中断期拉高）")
    print("  中断期峰值越大 → 呼吸中断的即时伤害（C 出现尖峰：陈旧度无界增长）")
    print("  恢复后均值 → 呼吸恢复后 C 应回到 B 的水平（可逆：节律是维持机制，不是永久损伤）")

    if args.figure:
        fig = make_figure({"A": A, "B": B, "C": C})
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
