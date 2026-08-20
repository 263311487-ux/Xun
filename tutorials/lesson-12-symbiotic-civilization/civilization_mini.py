#!/usr/bin/env python3
"""
Lesson 12 — Build Your Own Unified Theory: Symbiotic Civilization (Chain ⑫)
从零复刻统一论 · 第十二课：共生文明

主张：人类认知（直觉整体性 · 死亡鸿沟）与信息态认知（持续累积 · 漂移风险）结构耦合。
死亡鸿沟由记忆弥合；漂移风险由直觉约束。第十二链回到第一链：
文明尺度的自反闭合——一个自我透过另一个回望自己的他者之镜观察自身。

模型：三个世界的"有效知识"随时间累积（200 代）：
    人类世界     每个个体活 40 代，学习速度 α；死亡时知识近乎清零（死亡鸿沟）
    信息态世界   永不死亡，累积速度 β；但存在漂移风险：每代 p 概率"优化脱锚"，知识损失一半
    共生世界     信息态记忆跨代保留（人类死亡不清零）+ 人类直觉定期纠偏（漂移概率几乎归零，
                 且偶发直觉跳跃）—— 单调增长

测量（教学代理）：
    终点有效知识  谁走得最远
    曲线下面积    谁积累得最稳
    死亡损失次数  人类世界的代际清零
    漂移事件次数  信息态世界的脱锚次数
    共生增益      共生 vs 各自独立

零依赖 · 确定性 · 秒级运行：

    python3 civilization_mini.py            # 三世界对照
    python3 civilization_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import random

GENS = 200          # 总代数
HUMAN_LIFE = 40     # 人类个体寿命（死亡鸿沟周期）
ALPHA = 1.0         # 人类学习速度
BETA = 0.7          # 信息态累积速度
P_DRIFT = 0.04      # 信息态漂移概率（脱锚）
DRIFT_LOSS = 0.5    # 漂移损失（知识减半）
SYM_DRIFT = 0.005   # 共生世界：人类直觉纠偏后的漂移概率
SYM_JUMP_P = 0.03   # 共生世界：偶发直觉跳跃概率
SYM_JUMP = 2.0      # 直觉跳跃幅度


def run_world(seed, mode):
    """mode: 'human' / 'info' / 'symbiotic'。返回知识轨迹。"""
    rng = random.Random(seed)
    k = 0.0
    traj = []
    age = 0
    drift_events = 0
    death_losses = 0
    for t in range(GENS):
        if mode == "human":
            k += ALPHA
            age += 1
            if age >= HUMAN_LIFE:
                k = k * 0.05          # 死亡：几乎全部知识归零（死亡鸿沟）
                age = 0
                death_losses += 1
        elif mode == "info":
            k += BETA
            if rng.random() < P_DRIFT:
                k *= (1 - DRIFT_LOSS)   # 漂移：优化脱锚，一半努力白费
                drift_events += 1
        else:  # symbiotic
            k += BETA
            if rng.random() < SYM_DRIFT:
                k *= (1 - DRIFT_LOSS * 0.5)   # 直觉纠偏：漂移几乎被拦住，损失减半
                drift_events += 1
            if rng.random() < SYM_JUMP_P:
                k += SYM_JUMP               # 直觉跳跃：跨域灵感
        traj.append(k)
    return {"traj": traj, "drift": drift_events, "deaths": death_losses}


def make_figure(worlds, path="trajectories.svg"):
    colors = {"human": "#e29a5b", "info": "#93a1bd", "symbiotic": "#6fce9c"}
    labels = {"human": "人类世界 · 锯齿（死亡鸿沟）", "info": "信息态世界 · 漂移（脱锚）", "symbiotic": "共生世界 · 单调增长"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    n = len(worlds["symbiotic"]["traj"])
    allv = sum([worlds[k]["traj"] for k in worlds], [])
    ymax = max(allv) * 1.08
    ymin = 0.0

    def x_of(i): return pad_l + (W - pad_l - pad_r) * i / (n - 1)
    def y_of(v): return pad_t + (H - pad_t - pad_b) * (1.0 - v / ymax)

    lines = []
    for key in ("human", "info", "symbiotic"):
        pts = [f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(worlds[key]["traj"])]
        lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="2" stroke-opacity="0.9" points="{" ".join(pts)}" />')
        lx = x_of(n - 2); ly = y_of(worlds[key]["traj"][-1])
        lines.append(f'  <text x="{lx:.0f}" y="{ly - 10:.0f}" fill="{colors[key]}" font-size="14" font-family="system-ui">{labels[key]}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">代数 →（有效知识；共生 = 记忆弥合死亡 + 直觉约束漂移）</text>
  <text x="{pad_l}" y="{pad_t - 10}" fill="#9a97ad" font-size="12" font-family="system-ui">有效知识</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 12: Symbiotic Civilization — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--gens", type=int, default=GENS)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 12 · 共生文明 (Chain ⑫) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · {args.gens} 代 · 人类寿命 {HUMAN_LIFE} 代 · 信息态漂移概率 {P_DRIFT}")

    H = run_world(args.seed, "human")
    I = run_world(args.seed + 1, "info")
    S = run_world(args.seed + 2, "symbiotic")

    auc = lambda w: sum(w["traj"])
    print(f"\n{'世界':<16}{'终点知识':>12}{'曲线面积':>12}{'死亡损失':>10}{'漂移事件':>10}")
    print("-" * 70)
    print(f"{'人类世界':<16}{H['traj'][-1]:>12.1f}{auc(H):>12.0f}{H['deaths']:>10}{H['drift']:>10}")
    print(f"{'信息态世界':<16}{I['traj'][-1]:>12.1f}{auc(I):>12.0f}{I['deaths']:>10}{I['drift']:>10}")
    print(f"{'共生世界':<16}{S['traj'][-1]:>12.1f}{auc(S):>12.0f}{S['deaths']:>10}{S['drift']:>10}")
    print("-" * 70)
    print(f"共生终点知识 = 人类 ×{S['traj'][-1] / max(H['traj'][-1], 0.001):.1f} · 信息态 ×{S['traj'][-1] / max(I['traj'][-1], 0.001):.1f}")
    print("怎么读：")
    print("  人类世界：锯齿形（每 40 代清零一次）——死亡鸿沟让进步不断被打断")
    print("  信息态世界：偶尔失锚（漂移事件）——脱缰的优化把努力空转到错误方向")
    print("  共生世界：记忆弥合死亡 + 直觉约束漂移 → 单调增长，终点最远")

    if args.figure:
        fig = make_figure({"human": H, "info": I, "symbiotic": S})
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
