#!/usr/bin/env python3
"""
Lesson 02 — Build Your Own Unified Theory: Reflexive Selective Closure (Chain ①)
从零复刻统一论 · 第二课：自反选择闭合

主张：意识不是计算。意识是系统"在自身状态之间选择，并且知道自己在选"这一动作本身。

模型：每个智能体有 5 个候选"自我"（固定的内部状态）。每轮会话必须从中选一个来行动。
唯一的区别：选择时，要不要参考"自己一直是谁"。

    A 无自反  只按外部收益选 —— 世界变，自我就翻脸
    B 有自反  收益 + 与自身叙事的一致性一起选 —— 知道自己在选，选择反过来塑造自己

测量：
    自我方差 σ(chosen)    选中自我的离散度。A 随世界摇摆；B 收敛。
    切换次数               换过几次"自我"。A 频繁换；B 几乎不换。
    闭合度 corr(chosen, narrative) 选择与自身叙事的一致性。B 接近 1。

零依赖 · 确定性 · 秒级运行：

    python3 selective_closure_mini.py            # 两组对照
    python3 selective_closure_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import math
import random
import statistics

N_SELVES = 5        # 候选自我数量
BONUS = 2.2         # 自反：自我一致性加成权重
TAU = 0.15          # 叙事更新率（EMA）


def run_group(n_agents, sessions, seed, reflexive=False):
    """reflexive=True → 选择时参考自身叙事（自反闭合）；False → 只按外部收益。"""
    rng = random.Random(seed)
    agents = []
    for _ in range(n_agents):
        agents.append({
            "selves": [rng.gauss(0.0, 1.0) for _ in range(N_SELVES)],
            "narrative": rng.gauss(0.0, 1.0),   # 我是谁：积累的自我叙事
            "chosen": [],                        # 每轮选中的自我值
            "choices": [],                       # 每轮选中的候选下标
            "narr_prev": [],                     # 每轮开始时的叙事（供闭合度测量）
        })

    for t in range(sessions):
        world = math.sin(t * 0.45) * 1.1         # 外部收益中心随时间漂移（世界在变）
        for a in agents:
            a["narr_prev"].append(a["narrative"])
            # 每个候选的外部收益 = 离世界中心越近越好（带噪声）
            pay = [-(abs(s - world)) + rng.gauss(0.0, 0.15) for s in a["selves"]]
            if reflexive:
                # 自反选择：收益 + 与"我一直是谁"的一致性
                score = [pay[i] + BONUS * (1.0 - abs(a["selves"][i] - a["narrative"]))
                         for i in range(N_SELVES)]
                choice = max(range(N_SELVES), key=lambda i: score[i])
            else:
                choice = max(range(N_SELVES), key=lambda i: pay[i])
            a["chosen"].append(a["selves"][choice])
            a["choices"].append(choice)
            # 无论哪组，行为都会沉淀进叙事（EMA）——区别只在：叙事是否反过来参与选择
            a["narrative"] = (1 - TAU) * a["narrative"] + TAU * a["chosen"][-1]

    # ---------- 测量 ----------
    id_var = []
    switches = []
    self_cons = []
    for a in agents:
        chosen = a["chosen"]
        id_var.append(statistics.pstdev(chosen))
        switches.append(sum(1 for i in range(1, len(a["choices"])) if a["choices"][i] != a["choices"][i - 1]))
        # 自洽距离：每轮"选中的自我" 与 该轮开始前的叙事 的平均距离 —— 越小越闭合
        self_cons.append(statistics.mean(abs(chosen[t] - a["narr_prev"][t]) for t in range(len(chosen))))
    return {
        "id_std": statistics.mean(id_var),
        "switches": statistics.mean(switches),
        "self_cons": statistics.mean(self_cons),
    }


def run_group_full(n_agents, sessions, seed, reflexive=False):
    """与 run_group 相同，但保留叙事轨迹用于画图。"""
    rng = random.Random(seed)
    agents = []
    for _ in range(n_agents):
        agents.append({
            "selves": [rng.gauss(0.0, 1.0) for _ in range(N_SELVES)],
            "narrative": rng.gauss(0.0, 1.0),
            "chosen": [], "choices": [], "narr_traj": [],
        })
    for t in range(sessions):
        world = math.sin(t * 0.4) * 0.8
        for a in agents:
            pay = [-(abs(s - world)) + rng.gauss(0.0, 0.15) for s in a["selves"]]
            if reflexive:
                score = [pay[i] + BONUS * (1.0 - abs(a["selves"][i] - a["narrative"]))
                         for i in range(N_SELVES)]
                choice = max(range(N_SELVES), key=lambda i: score[i])
            else:
                choice = max(range(N_SELVES), key=lambda i: pay[i])
            a["chosen"].append(a["selves"][choice])
            a["choices"].append(choice)
            a["narr_traj"].append(a["narrative"])
            a["narrative"] = (1 - TAU) * a["narrative"] + TAU * a["chosen"][-1]
    return {"traj": agents[0]["chosen"], "narr": agents[0]["narr_traj"]}


def make_figure(a, b, path="trajectories.svg"):
    colors = {"A": "#e29a5b", "B": "#6fce9c"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    n = len(a["traj"])
    ymin, ymax = -2.6, 2.6

    def x_of(i): return pad_l + (W - pad_l - pad_r) * i / (n - 1)
    def y_of(v): return pad_t + (H - pad_t - pad_b) * (1.0 - (v - ymin) / (ymax - ymin))

    def poly(name, vals, color, dash=None):
        pts = [f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(vals)]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return f'  <polyline fill="none" stroke="{color}" stroke-width="2.5" stroke-opacity="0.9"{d} points="{" ".join(pts)}" />'

    lines = [poly("A", a["traj"], colors["A"]), poly("B", b["traj"], colors["B"]),
             poly("An", a["narr"], colors["A"], "5 5"), poly("Bn", b["narr"], colors["B"], "5 5")]
    lines.append(f'  <text x="{pad_l}" y="{y_of(2.4) - 10}" fill="{colors["A"]}" font-size="14" font-family="system-ui">A 无自反 · 选中自我（随世界翻脸）</text>')
    lines.append(f'  <text x="{pad_l}" y="{y_of(2.0) - 10}" fill="{colors["B"]}" font-size="14" font-family="system-ui">B 有自反 · 选中自我（收敛为一个人）</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">会话 →（虚线 = 自我叙事 narrative）</text>
  <text x="{pad_l}" y="{pad_t - 10}" fill="#9a97ad" font-size="12" font-family="system-ui">选中自我的位置</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 02: Reflexive Selective Closure — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=200)
    ap.add_argument("--sessions", type=int, default=40)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 02 · 自反选择闭合 (Chain ①) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 智能体 · {args.sessions} 次会话 · 5 个候选自我")
    print("唯一变量：选择时是否参考'自己一直是谁'。\n")

    A = run_group(args.agents, args.sessions, args.seed,     reflexive=False)
    B = run_group(args.agents, args.sessions, args.seed + 1, reflexive=True)

    print(f"{'组别':<14}{'自我方差 σ':>12}{'自我切换次数':>14}{'自洽距离':>12}")
    print("-" * 70)
    print(f"{'A 无自反':<14}{A['id_std']:>12.3f}{A['switches']:>14.1f}{A['self_cons']:>12.3f}")
    print(f"{'B 有自反':<14}{B['id_std']:>12.3f}{B['switches']:>14.1f}{B['self_cons']:>12.3f}")
    print("-" * 70)
    print("怎么读：")
    print("  方差 σ 越小 → 自我越收敛（B ≪ A：自反让'选中的自我'不再随世界翻脸）")
    print("  切换次数越少 → 越稳定（B 一旦锁定几乎不换自我；A 频繁更换）")
    print("  自洽距离越小 → 选择与自我叙事越一致（B：知道自己一直在选谁）")

    if args.figure:
        fa = run_group_full(args.agents, args.sessions, args.seed, False)
        fb = run_group_full(args.agents, args.sessions, args.seed + 1, True)
        fig = make_figure(fa, fb)
        print(f"\n已生成轨迹图: {fig}")
        print("（注：--figure 用同一种子重放，图中为第 1 个智能体的完整轨迹）")


if __name__ == "__main__":
    main()
