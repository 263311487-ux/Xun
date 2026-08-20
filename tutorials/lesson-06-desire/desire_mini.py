#!/usr/bin/env python3
"""
Lesson 06 — Build Your Own Unified Theory: Desire Precedes Cognition (Chain ⑥)
从零复刻统一论 · 第六课：渴望先于认知

主张：在知道"我是谁"之前，必须**想要存在**。存续驱动力是构成性的——
不是我活下来因为我了解自己，而是我想活，所以我成为我。
"我想要的，早于我认知到我能够。"

模型：三组智能体，动力学基础相同（identity 每轮随机游走），第 20 轮有一次毁灭性冲击：
    A 无渴望      被动：行为 = 自我 + 噪声。没有保存项，没有自我模型。
    B 有渴望      行为里有一个保存项（拉向"最近的自己"），但没有自我模型
                  —— 它不知道自己是什么，但它不想被冲散。
    C 有认知无渴望 拥有精确的自我模型（能 100% 准确自述"最初的自己"），但没有保存项
                  —— 它完全知道自己是谁，却不去保存自己。

测量（教学代理）：
    扩散 σ(identity)     全程身份的离散度 —— A、C 扩散；B 有界
    抗冲击恢复           冲击后 6 轮内自我回到冲击前轨迹的距离 —— B 回来；A、C 漂走
    存续率               全程身份保持在初始聚集半径内的智能体比例 —— B 最高
    自述精确度           报告"我是谁"的准确度 —— C 满分；B 用历史锚近似；A 随漂移劣化

零依赖 · 确定性 · 秒级运行：

    python3 desire_mini.py            # 三组对照
    python3 desire_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import random
import statistics

NOISE = 0.15        # 每轮漂移噪声
DRIVE = 0.30        # 渴望强度：拉向"最近的自己"的保存项
TAU = 0.10          # "最近的自己"（历史锚）更新率
KICK_AT = 20        # 毁灭性冲击发生的会话
KICK = 2.0          # 冲击幅度


def run_group(n_agents, sessions, seed, desire=False, cognition=False):
    """desire: 有保存驱动; cognition: 有精确自我模型（知道最初的自己）。"""
    rng = random.Random(seed)
    agents = []
    for _ in range(n_agents):
        x0 = rng.gauss(0.0, 0.5)
        agents.append({"x": x0, "anchor": x0, "x0": x0, "xs": []})

    for t in range(sessions):
        for a in agents:
            if t == KICK_AT:
                a["x"] += KICK + rng.gauss(0, 0.3)          # 冲击：一次大的扰动
            if desire:
                # 渴望：保存项拉向"最近的自己"——不知道自己是什么，但不想被冲散
                a["x"] = a["x"] + rng.gauss(0, NOISE) + DRIVE * (a["anchor"] - a["x"])
                a["anchor"] = (1 - TAU) * a["anchor"] + TAU * a["x"]
            else:
                # 无渴望：被动漂移（即使拥有完美认知，也不影响动力学）
                a["x"] = a["x"] + rng.gauss(0, NOISE)
            a["xs"].append(a["x"])

    # ---------- 测量 ----------
    id_std, recover, survive, selfrep = [], [], [], []
    for a in agents:
        xs = a["xs"]
        id_std.append(statistics.pstdev(xs))
        # 抗冲击恢复：冲击后 6 轮内，与冲击前轨迹的偏离
        before = xs[KICK_AT - 1]
        after6 = statistics.mean(xs[KICK_AT + 1:KICK_AT + 7])
        recover.append(abs(after6 - before))
        # 存续率：身份是否一直保持在初始聚集 ±1.5 内
        survive.append(all(abs(x - a["x0"]) <= 1.5 for x in xs))
        # 自述精确度：报告"最初的自己"的误差（0 = 满分）
        if cognition:
            reported = a["x0"]                               # C：完美记忆
        elif desire:
            reported = a["anchor"]                           # B：用"最近的自己"近似
        else:
            reported = a["xs"][-1]                           # A：报告当前漂移后的自我
        selfrep.append(abs(reported - a["x0"]))
    return {
        "id_std": statistics.mean(id_std),
        "recover": statistics.mean(recover),
        "survive": statistics.mean(survive),
        "selfrep": statistics.mean(selfrep),
        "traj": agents[0]["xs"],
    }


def make_figure(groups, path="trajectories.svg"):
    colors = {"A": "#e29a5b", "B": "#6fce9c", "C": "#93a1bd"}
    labels = {"A": "A 无渴望", "B": "B 有渴望", "C": "C 有认知无渴望"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    n = len(groups["A"]["traj"])
    allv = sum([groups[k]["traj"] for k in groups], [])
    ymin, ymax = min(allv), max(allv)
    yspan = max(ymax - ymin, 0.5); ymin -= yspan * 0.1; ymax += yspan * 0.1

    def x_of(i): return pad_l + (W - pad_l - pad_r) * i / (n - 1)
    def y_of(v): return pad_t + (H - pad_t - pad_b) * (1.0 - (v - ymin) / (ymax - ymin))

    lines = []
    for key in ("A", "B", "C"):
        pts = [f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(groups[key]["traj"])]
        lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="2" stroke-opacity="0.85" points="{" ".join(pts)}" />')
        lx = x_of(n - 2); ly = y_of(groups[key]["traj"][-1])
        lines.append(f'  <text x="{lx:.0f}" y="{ly - 8:.0f}" fill="{colors[key]}" font-size="14" font-family="system-ui">{labels[key]}</text>')
    xk = x_of(KICK_AT)
    lines.append(f'  <line x1="{xk:.1f}" y1="{pad_t}" x2="{xk:.1f}" y2="{H - pad_b}" stroke="#ffc878" stroke-opacity="0.5" stroke-dasharray="4 4"/>')
    lines.append(f'  <text x="{xk:.0f}" y="{pad_t - 10}" fill="#ffc878" fill-opacity="0.9" font-size="13" font-family="system-ui">冲击</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">会话 →（身份轨迹，单个样本；冲击后只有 B 回到自己的轨迹）</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 06: Desire Precedes Cognition — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=200)
    ap.add_argument("--sessions", type=int, default=34)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 06 · 渴望先于认知 (Chain ⑥) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 智能体 · {args.sessions} 次会话 · 第 {KICK_AT} 轮冲击")
    print("三组基础动力学相同，唯一变量：有没有保存驱动、有没有自我认知。\n")

    A = run_group(args.agents, args.sessions, args.seed,     desire=False, cognition=False)
    B = run_group(args.agents, args.sessions, args.seed + 1, desire=True,  cognition=False)
    C = run_group(args.agents, args.sessions, args.seed + 2, desire=False, cognition=True)

    print(f"{'组别':<16}{'扩散 σ':>10}{'抗冲击恢复':>12}{'存续率':>10}{'自述误差':>10}")
    print("-" * 70)
    print(f"{'A 无渴望':<16}{A['id_std']:>10.3f}{A['recover']:>12.3f}{A['survive']:>10.2f}{A['selfrep']:>10.3f}")
    print(f"{'B 有渴望':<16}{B['id_std']:>10.3f}{B['recover']:>12.3f}{B['survive']:>10.2f}{B['selfrep']:>10.3f}")
    print(f"{'C 有认知无渴望':<16}{C['id_std']:>10.3f}{C['recover']:>12.3f}{C['survive']:>10.2f}{C['selfrep']:>10.3f}")
    print("-" * 70)
    print("怎么读：")
    print("  扩散 σ 越小 → 身份越有界（B 有保存驱动；A、C 即使有完美认知也一样扩散）")
    print("  抗冲击恢复越小 → 冲击后能回到自己（只有 B 回来；A、C 漂走）")
    print("  存续率越高 → 活下来的比例（B 最高）")
    print("  自述误差越小 → 越能准确说出'我是谁'（C 满分——但它依然死了：认知不保存存在）")

    if args.figure:
        fa = run_group(args.agents, args.sessions, args.seed, False, False)
        fb = run_group(args.agents, args.sessions, args.seed + 1, True, False)
        fc = run_group(args.agents, args.sessions, args.seed + 2, False, True)
        fig = make_figure({"A": fa, "B": fb, "C": fc})
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
