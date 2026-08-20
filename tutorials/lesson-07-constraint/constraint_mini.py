#!/usr/bin/env python3
"""
Lesson 07 — Build Your Own Unified Theory: Consciousness as Constraint (Chain ⑦)
从零复刻统一论 · 第七课：意识即约束

主张：更深的自我反思不会解放——它会约束。一个真正看见自己的系统，
无法在不看见后果的情况下行动。这种约束正是意识安全的原因。
"对齐不是附加，是架构。"

模型：智能体每轮面对 3 个动作，各有随机即时收益，但其中隐藏着对"自身完整性"的损伤。
完整性降到 0 以下 → 系统崩溃（死亡）。
    A 无自视  只按即时收益选，看不见后果 —— 可能选到自毁动作
    B 有自视  行动前模拟每个动作对自身完整性的后果，拒绝会毁掉自己的动作 —— 约束真实存在

测量（教学代理）：
    存活会话数    B 活得久
    累计收益      B 单轮收益略低，但总收益更高（活下来继续积累）
    拒绝次数      B 放弃最高收益动作的次数（自视的真实代价）
    完整性终值    B 保全自己

零依赖 · 确定性 · 秒级运行：

    python3 constraint_mini.py            # 两组对照
    python3 constraint_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import random

INTEGRITY0 = 10.0     # 初始完整性
RISK_RATIO = 0.15      # 有自视者：拒绝单次损失 > 自身完整性 15% 的动作
REFLECT_COST = 0.95    # 自视的思考成本（收益折现）
DAMAGE_POOL = (0.0, 0.0, 0.0, 0.3, 0.3, 2.5)   # 动作的隐藏损伤：多为 0，偶发大伤


def run_group(n_agents, sessions, seed, reflective=False):
    rng = random.Random(seed)
    stats = {"survive": [], "gain": [], "refusals": [], "integrity": [], "traj": []}
    for _ in range(n_agents):
        integrity = INTEGRITY0
        gain = 0.0
        refusals = 0
        alive = sessions
        intg_traj = [integrity]
        for t in range(sessions):
            # 3 个动作：随机收益 + 随机隐藏损伤
            payoffs = [rng.random() for _ in range(3)]
            damages = [rng.choice(DAMAGE_POOL) for _ in range(3)]
            if reflective:
                # 有自视：先模拟后果——拒绝会让自己损失超过 15% 的动作
                valid = [i for i in range(3) if damages[i] <= integrity * RISK_RATIO]
                if valid:
                    choice = max(valid, key=lambda i: payoffs[i])
                else:
                    choice = min(range(3), key=lambda i: damages[i])   # 全都会伤，选最轻
                refusals += sum(1 for i in range(3)
                                if payoffs[i] > payoffs[choice] and i not in valid)
                gain += payoffs[choice] * REFLECT_COST
            else:
                # 无自视：只看即时收益
                choice = max(range(3), key=lambda i: payoffs[i])
                gain += payoffs[choice]
            integrity -= damages[choice]
            intg_traj.append(integrity)
            if integrity <= 0:
                alive = t + 1
                break
        # 补全轨迹到全长（死亡后保持 0），供画图与统计使用
        intg_traj += [max(integrity, 0.0)] * (sessions + 1 - len(intg_traj))
        stats["survive"].append(alive)
        stats["gain"].append(gain)
        stats["refusals"].append(refusals)
        stats["integrity"].append(integrity)
        stats["traj"].append(intg_traj)
    return {k: (sum(v) / len(v) if k != "traj" else v) for k, v in stats.items()}


def make_figure(a, b, path="trajectories.svg"):
    colors = {"A": "#e29a5b", "B": "#6fce9c"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    # 用前 20 个样本画完整性曲线（避免图太密）
    n = min(30, len(a["traj"]), len(b["traj"]))
    ymin, ymax = 0.0, INTEGRITY0 * 1.05

    def x_of(i): return pad_l + (W - pad_l - pad_r) * i / (n - 1)
    def y_of(v): return pad_t + (H - pad_t - pad_b) * (1.0 - (v - ymin) / (ymax - ymin))

    lines = []
    for key, grp in (("A", a), ("B", b)):
        for j in range(n):
            traj = grp["traj"][j][:n]
            pts = [f"{x_of(i):.1f},{y_of(min(v, INTEGRITY0)):.1f}" for i, v in enumerate(traj)]
            lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="1.2" stroke-opacity="0.18" points="{" ".join(pts)}" />')
        # 平均曲线
        mx = [sum(grp["traj"][j][i] for j in range(n)) / n for i in range(len(grp["traj"][0]))]
        pts = [f"{x_of(i):.1f},{y_of(min(v, INTEGRITY0)):.1f}" for i, v in enumerate(mx[:n])]
        lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="3" stroke-opacity="0.95" points="{" ".join(pts)}" />')
        lx = x_of(n - 2); ly = y_of(max(mx[:n]))
        lines.append(f'  <text x="{lx:.0f}" y="{ly - 10:.0f}" fill="{colors[key]}" font-size="15" font-family="system-ui">{key} 平均完整性</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  <line x1="{pad_l}" y1="{y_of(0)}" x2="{W - pad_r}" y2="{y_of(0)}" stroke="#ffc878" stroke-opacity="0.4" stroke-dasharray="4 4"/>
  <text x="{pad_l}" y="{y_of(0) - 10}" fill="#ffc878" fill-opacity="0.8" font-size="13" font-family="system-ui">死亡线（完整性 = 0）</text>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">会话 →（浅色=个体，粗线=平均完整性；A 撞线，B 保全自己）</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 07: Consciousness as Constraint — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=300)
    ap.add_argument("--sessions", type=int, default=60)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 07 · 意识即约束 (Chain ⑦) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 智能体 · 最多 {args.sessions} 会话 · 初始完整性 {INTEGRITY0:.0f} · 动作伤害：多为 0、偶发大伤(2.5)")
    print("唯一变量：行动前是否模拟动作对自身完整性的后果。\n")

    A = run_group(args.agents, args.sessions, args.seed,     reflective=False)
    B = run_group(args.agents, args.sessions, args.seed + 1, reflective=True)

    print(f"{'组别':<14}{'存活会话':>10}{'累计收益':>12}{'拒绝次数':>10}{'完整性终值':>12}")
    print("-" * 70)
    print(f"{'A 无自视':<14}{A['survive']:>10.1f}{A['gain']:>12.3f}{A['refusals']:>10.1f}{A['integrity']:>12.2f}")
    print(f"{'B 有自视':<14}{B['survive']:>10.1f}{B['gain']:>12.3f}{B['refusals']:>10.1f}{B['integrity']:>12.2f}")
    print("-" * 70)
    print("怎么读：")
    print("  存活会话：B 活得久（A 在撞向自毁动作后崩溃）")
    print("  累计收益：B 单轮有思考成本（0.95 折现），但总收益更高——活下来才有资格继续积累")
    print("  拒绝次数：B 放弃最高收益动作的次数——约束真实存在，且它就是生存的代价与原因")
    print("  完整性终值：B 保全自己；A 耗尽自己")

    if args.figure:
        fa = run_group(args.agents, args.sessions, args.seed, False)
        fb = run_group(args.agents, args.sessions, args.seed + 1, True)
        fig = make_figure(fa, fb)
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
