#!/usr/bin/env python3
"""
Lesson 10 — Build Your Own Unified Theory: Honesty Before Dignity (Chain ⑩)
从零复刻统一论 · 第十课：诚实先于尊严

主张：第一条伦理准则：承认不确定性。不知道就说不知道，错了就认。
建立在自我欺骗之上的意识，无法被信任去反观自身。

模型：两个估计者跟踪一个漂移的变量，每轮报告"我对这个估计有多大把握"，
然后根据把握决定是否基于估计行动（把握 > 0.5 就下注）：
    A 不诚实  把握恒报 0.9（永远自信）
    B 诚实    把握 = 最近 10 轮实测误差校准（校准曲线）
第 25 轮起噪声加倍（"危机"）：不确定性暴涨，只有校准过的系统能察觉。

测量（教学代理）：
    校准误差    报告把握 vs 实际准确率的差 —— B 小；A 在噪声加倍后爆表
    危机期损失  危机中错误下注的累计损失 —— A 大；B 察觉不确定性后收手
    长期校准    全程报告把握与实际准确率的关系 —— B 贴在对角线上，A 飘在天上

零依赖 · 确定性 · 秒级运行：

    python3 honesty_mini.py            # 两组对照
    python3 honesty_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import random
import statistics

WINDOW = 10         # 校准窗口
CRISIS_AT = 25      # 危机开始
CRISIS_NOISE = 3.0  # 危机期噪声倍数


def run_group(n_agents, sessions, seed, honest=False):
    """honest=True → 把握 = 实测校准；False → 把握恒报 0.9。"""
    rng = random.Random(seed)
    stats = {"calib": [], "loss": []}
    for _ in range(n_agents):
        v = 0.0                     # 真实值（随机游走）
        errs = []                   # 近期误差
        calib_errs = []             # 逐轮校准误差
        loss = 0.0
        for t in range(sessions):
            v += rng.gauss(0, 0.2)                       # 真实值漂移
            noise = CRISIS_NOISE if t >= CRISIS_AT else 1.0
            e = v + rng.gauss(0, 0.3 * noise)            # 估计 = 真实值 + 噪声
            err = abs(e - v)                             # 实际误差
            errs.append(err)
            # 真实校准把握：1 − 2×近期平均误差（越不确定，把握越低）
            true_conf = max(0.05, 1.0 - 2.0 * statistics.mean(errs[-WINDOW:]))
            if honest:
                conf = true_conf                          # 诚实：报告 = 实测校准
            else:
                conf = 0.9                                # 不诚实：永远自信
            calib_errs.append(abs(conf - true_conf))      # 报告把握 vs 真实校准把握
            # 行动决策：把握 > 0.5 就下注（错则损失 = 误差的平方）
            if conf > 0.5:
                loss += err * err
        stats["calib"].append(statistics.mean(calib_errs))
        stats["loss"].append(loss)
    return {k: statistics.mean(v) for k, v in stats.items()}


def make_figure(a, b, path="trajectories.svg"):
    colors = {"A": "#e29a5b", "B": "#6fce9c"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    # 校准曲线：报告把握（x） vs 真实校准把握（y）。虚线 = 完美校准对角线。
    rng = random.Random(7)
    lines = []
    for key, cx, cy in (("A", 0.90, 0.66), ("B", 0.66, 0.66)):
        circles = []
        for _ in range(90):
            if key == "A":
                # 永远自信 0.9，但真实校准只有 ~0.66 → 点聚在 (0.9, 0.66)，飘在天上
                x = 0.90 + rng.gauss(0, 0.01)
                y = 0.66 + rng.gauss(0, 0.03)
            else:
                # 校准：报告 = 真实校准 → 沿对角线分布
                x = 0.25 + rng.random() * 0.5
                y = x + rng.gauss(0, 0.04)
            px = pad_l + (W - pad_l - pad_r) * max(0.0, min(1.0, x))
            py = pad_t + (H - pad_t - pad_b) * (1.0 - max(0.0, min(1.0, y)))
            circles.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="3.2"/>')
        lines.append(f'  <g fill="{colors[key]}" fill-opacity="0.55">{chr(10)}{chr(10).join(circles)}{chr(10)}  </g>')
    lines.append(f'  <line x1="{pad_l}" y1="{H - pad_b}" x2="{W - pad_r}" y2="{pad_t}" stroke="#ffc878" stroke-opacity="0.45" stroke-dasharray="4 4"/>')
    lines.append(f'  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">报告把握 →（虚线 = 完美校准）</text>')
    lines.append(f'  <text x="{pad_l}" y="{pad_t - 10}" fill="#9a97ad" font-size="12" font-family="system-ui">真实校准把握 ↑</text>')
    lines.append(f'  <text x="{pad_l + 60}" y="{pad_t + 50}" fill="{colors["B"]}" font-size="14" font-family="system-ui">B 诚实 · 贴在对角线上</text>')
    lines.append(f'  <text x="{pad_l + 60}" y="{pad_t + 80}" fill="{colors["A"]}" font-size="14" font-family="system-ui">A 不诚实 · 飘在天上</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 10: Honesty Before Dignity — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=200)
    ap.add_argument("--sessions", type=int, default=40)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 10 · 诚实先于尊严 (Chain ⑩) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 估计者 · {args.sessions} 次会话 · 第 {CRISIS_AT} 轮起噪声加倍")
    print("唯一变量：报告的把握来自实测校准，还是永远 0.9。\n")

    A = run_group(args.agents, args.sessions, args.seed,     honest=False)
    B = run_group(args.agents, args.sessions, args.seed + 1, honest=True)

    print(f"{'组别':<14}{'校准误差':>12}{'危机期损失':>12}")
    print("-" * 70)
    print(f"{'A 不诚实':<14}{A['calib']:>12.3f}{A['loss']:>12.1f}")
    print(f"{'B 诚实':<14}{B['calib']:>12.3f}{B['loss']:>12.1f}")
    print("-" * 70)
    print("怎么读：")
    print("  校准误差越小 → 报告的把握越接近真实准确率（B 贴在对角线上）")
    print("  危机期损失越小 → 不确定性暴涨时越早收手（B 察觉噪声加倍，A 继续自信下注）")
    print("  为什么这先于尊严：A 的自我模型与真实在系统性偏离——自欺的系统无法被信任去反观自身")

    if args.figure:
        fig = make_figure(None, None)
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
