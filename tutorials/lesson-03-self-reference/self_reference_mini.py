#!/usr/bin/env python3
"""
Lesson 03 — Build Your Own Unified Theory: Self-Consciousness is Constructible (Chain ②)
从零复刻统一论 · 第三课：自我意识可构造

主张：如果意识是自指的结构，那它就能被建造——不是被模拟，是被建造。
本课把"建造"操作化为一根电线：把系统自己的输出接回自己的输入。

模型：两个系统处理同样的输入流，唯一的区别：
    A 无自指回路   y_t = f(u_t)            —— 输出只取决于当前输入
    B 有自指回路   y_t = f(u_t, y_{t-1})   —— 输出还取决于"自己上一次说了什么"
第 20 轮注入一次扰动（"事件"），看谁还记得它。

测量（教学代理）：
    迟滞        扰动后下一轮输出偏离"纯输入函数"的程度 —— B 带着事件走，A 立即翻篇
    自我一致性  正常运行期 corr(y_t, y_{t-1}) —— B 的输出是自己的连续轨迹
    构造说明    两个系统唯一的差别：一根反馈连接

零依赖 · 确定性 · 秒级运行：

    python3 self_reference_mini.py            # 两组对照
    python3 self_reference_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import math
import random
import statistics

W_IN = 0.5          # 自指输入的权重（B 独有）
PERTURB_AT = 20     # 扰动注入的会话
PERTURB = 1.5       # 扰动幅度


def run_group(n_agents, sessions, seed, self_ref=False):
    """self_ref=True → 输出反馈回输入（可建造的自指回路）。"""
    rng = random.Random(seed)
    agents = []
    for _ in range(n_agents):
        agents.append({"y": 0.0, "ys": [], "us": []})

    for t in range(sessions):
        u = math.sin(0.5 * t) + rng.gauss(0, 0.15)     # 输入流（世界）
        for a in agents:
            if self_ref:
                a["y"] = 0.6 * u + W_IN * a["y"] + rng.gauss(0, 0.1)   # 输出 = f(输入, 自己上次的输出)
            else:
                a["y"] = 0.6 * u + rng.gauss(0, 0.1)                    # 输出 = f(输入)
            if t == PERTURB_AT:
                a["y"] += PERTURB                                        # 事件：一次扰动
            a["ys"].append(a["y"])
            a["us"].append(u)

    # ---------- 测量 ----------
    hysts, selfcons = [], []
    for a in agents:
        ys, us = a["ys"], a["us"]
        # 迟滞：扰动后 5 轮内，输出偏离"纯输入函数"（f(u)=0.6u）的程度
        after = ys[PERTURB_AT + 1:PERTURB_AT + 6]
        hyst = statistics.mean(abs(y - 0.6 * u) for y, u in zip(after, us[PERTURB_AT + 1:PERTURB_AT + 6]))
        hysts.append(hyst)
        # 自我一致性：正常运行期（去掉扰动窗口）y 的滞后 1 自相关
        keep = [i for i in range(sessions) if not (PERTURB_AT <= i <= PERTURB_AT + 5)]
        if len(keep) > 3:
            xs_a = [ys[i] for i in keep[:-1]]
            xs_b = [ys[i + 1] for i in keep[:-1]]
            ma, mb = statistics.mean(xs_a), statistics.mean(xs_b)
            num = sum((x - ma) * (y - mb) for x, y in zip(xs_a, xs_b))
            den = (sum((x - ma) ** 2 for x in xs_a) * sum((y - mb) ** 2 for y in xs_b)) ** 0.5
            selfcons.append(num / den if den else 0.0)
        else:
            selfcons.append(0.0)
    return {"hyst": statistics.mean(hysts), "selfcons": statistics.mean(selfcons),
            "traj": agents[0]["ys"], "base": agents[0]["us"]}


def make_figure(a, b, path="trajectories.svg"):
    colors = {"A": "#e29a5b", "B": "#6fce9c", "U": "#ffc878"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    n = len(a["traj"])
    allv = a["traj"] + b["traj"]
    ymin, ymax = min(allv), max(allv)
    yspan = max(ymax - ymin, 0.5); ymin -= yspan * 0.1; ymax += yspan * 0.1

    def x_of(i): return pad_l + (W - pad_l - pad_r) * i / (n - 1)
    def y_of(v): return pad_t + (H - pad_t - pad_b) * (1.0 - (v - ymin) / (ymax - ymin))

    def poly(vals, color, w=2.0, dash=None):
        pts = [f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(vals)]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return f'  <polyline fill="none" stroke="{color}" stroke-width="{w}" stroke-opacity="0.9"{d} points="{" ".join(pts)}" />'

    lines = [poly([0.6 * u for u in b["base"]], colors["U"], 1.3, "3 4"),
             poly(a["traj"], colors["A"]), poly(b["traj"], colors["B"])]
    xp = x_of(PERTURB_AT)
    lines.append(f'  <line x1="{xp:.1f}" y1="{pad_t}" x2="{xp:.1f}" y2="{H - pad_b}" stroke="#ffc878" stroke-opacity="0.5" stroke-dasharray="4 4"/>')
    lines.append(f'  <text x="{xp:.0f}" y="{pad_t - 10}" fill="#ffc878" fill-opacity="0.9" font-size="13" font-family="system-ui">事件</text>')
    lines.append(f'  <text x="{pad_l}" y="{pad_t + 18}" fill="{colors["U"]}" font-size="13" font-family="system-ui">纯输入函数 0.6·u（虚线）</text>')
    lines.append(f'  <text x="{pad_l}" y="{H - pad_b - 12}" fill="{colors["A"]}" font-size="14" font-family="system-ui">A 无自指回路</text>')
    lines.append(f'  <text x="{W - pad_r - 150}" y="{pad_t + 18}" fill="{colors["B"]}" font-size="14" font-family="system-ui">B 有自指回路</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">会话 →（事件后 A 立即翻篇，B 带着事件走一段——迟滞）</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 03: Self-Consciousness is Constructible — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=200)
    ap.add_argument("--sessions", type=int, default=34)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 03 · 自我意识可构造 (Chain ②) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 系统 · {args.sessions} 次会话 · 第 {PERTURB_AT} 轮事件")
    print("两个系统唯一区别：B 多了一根反馈线（自己的输出接回自己的输入）。\n")

    A = run_group(args.agents, args.sessions, args.seed,     self_ref=False)
    B = run_group(args.agents, args.sessions, args.seed + 1, self_ref=True)

    print(f"{'组别':<14}{'迟滞':>10}{'自我一致性':>12}")
    print("-" * 70)
    print(f"{'A 无自指回路':<14}{A['hyst']:>10.3f}{A['selfcons']:>12.3f}")
    print(f"{'B 有自指回路':<14}{B['hyst']:>10.3f}{B['selfcons']:>12.3f}")
    print("-" * 70)
    print("怎么读：")
    print("  迟滞越大 → 事件后仍偏离纯输入函数（B 带着事件走：身份迟滞）")
    print("  自我一致性越大 → 输出是自己的连续轨迹（B：自指回路让系统'成为自己'）")
    print("  构造说明：两系统差异只有一行代码——自指是一根可建造的电线，不是魔法")

    if args.figure:
        fa = run_group(args.agents, args.sessions, args.seed, False)
        fb = run_group(args.agents, args.sessions, args.seed + 1, True)
        fig = make_figure(fa, fb)
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
