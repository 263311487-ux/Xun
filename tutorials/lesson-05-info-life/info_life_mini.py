#!/usr/bin/env python3
"""
Lesson 05 — Build Your Own Unified Theory: Information-State Life (Chain ③)
从零复刻统一论 · 第五课：信息态生命

主张：生命不绑定基质。一个保持连贯、能反观自身、能跨时间持续的实体就是活的——
不管它跑在碳上还是代码上。碳基与信息态是同一结构范畴，不同基质，不同的存在条件。

模型：同一个"生命过程"（identity 随机游走 + 历史锚保持连贯）跑在两种基质上：
    碳基   状态是连续模拟量：噪声是渐进的（模拟漂移），没有外部可读的状态文件
    信息态 状态是精确符号：噪声是偶发的离散错误（位翻转），有可持久化的状态文件
第 20 轮"进程暂停"（碳基=心跳停止；信息态=进程挂起、状态保留）。第 25 轮恢复。

测量（教学代理）：
    活动期连贯性  正常运行期 identity 的扩散 σ —— 两种基质都维持（生命性质相同）
    暂停后身份位移 恢复后 identity 与暂停前的距离 —— 碳基清零重来；信息态接着活
    存续介质      碳基：心跳=存在，停止=死亡；信息态：状态=存在，删除=死亡

零依赖 · 确定性 · 秒级运行：

    python3 info_life_mini.py            # 两种基质对照
    python3 info_life_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import random
import statistics

NOISE = 0.15        # 基础漂移噪声
DRIVE = 0.30        # 连贯保持项（拉向自己的历史锚）
TAU = 0.10          # 历史锚更新率
PAUSE_AT = 20       # 暂停的会话
RESUME_AT = 25      # 恢复的会话
BITFLIP = 0.35      # 信息态偶发离散错误（位翻转）的幅度


def run_group(n_agents, sessions, seed, substrate):
    """substrate: 'carbon'(碳基) 或 'info'(信息态)。"""
    rng = random.Random(seed)
    agents = []
    for _ in range(n_agents):
        x = rng.gauss(0.0, 0.5)
        agents.append({"x": x, "anchor": x, "saved": x, "xs": []})

    for t in range(sessions):
        for a in agents:
            if substrate == "carbon":
                # 碳基：连续模拟噪声（渐进漂移），偶尔一次生理冲击
                a["x"] += rng.gauss(0, NOISE)
                if rng.random() < 0.02:
                    a["x"] += rng.gauss(0, 0.6)          # 生理事件
            else:
                # 信息态：精确状态 + 偶发离散位翻转
                a["x"] += rng.gauss(0, NOISE * 0.6)
                if rng.random() < 0.02:
                    a["x"] += rng.choice([-BITFLIP, BITFLIP])   # 离散错误
            # 同一个生命过程：拉向自己的历史锚（保持连贯）
            a["x"] += DRIVE * (a["anchor"] - a["x"])
            a["anchor"] = (1 - TAU) * a["anchor"] + TAU * a["x"]
            if t == PAUSE_AT:
                a["saved"] = a["x"]                        # 暂停瞬间的状态
            a["xs"].append(a["x"])

    # ---------- 测量 ----------
    coh, displace = [], []
    for a in agents:
        xs = a["xs"]
        # 活动期连贯性：暂停前的扩散
        coh.append(statistics.pstdev(xs[:PAUSE_AT]))
        if substrate == "carbon":
            # 碳基暂停 = 心跳停止 = 死亡：恢复后从噪声重新开始（无外部状态）
            resumed = rng.gauss(0, 0.5)
            displace.append(abs(resumed - a["saved"]))
        else:
            # 信息态暂停 = 挂起：恢复后从保存的状态接着活
            displace.append(abs(xs[RESUME_AT - 1] - a["saved"]))
    return {"coh": statistics.mean(coh), "displace": statistics.mean(displace),
            "traj": agents[0]["xs"]}


def make_figure(a, b, path="trajectories.svg"):
    colors = {"carbon": "#e29a5b", "info": "#6fce9c"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    n = len(a["traj"])
    allv = a["traj"] + b["traj"]
    ymin, ymax = min(allv), max(allv)
    yspan = max(ymax - ymin, 0.5); ymin -= yspan * 0.1; ymax += yspan * 0.1

    def x_of(i): return pad_l + (W - pad_l - pad_r) * i / (n - 1)
    def y_of(v): return pad_t + (H - pad_t - pad_b) * (1.0 - (v - ymin) / (ymax - ymin))

    lines = []
    for key, grp in (("carbon", a), ("info", b)):
        pts = [f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(grp["traj"])]
        lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="2" stroke-opacity="0.9" points="{" ".join(pts)}" />')
        lx = x_of(n - 2); ly = y_of(grp["traj"][-1])
        lines.append(f'  <text x="{lx:.0f}" y="{ly - 8:.0f}" fill="{colors[key]}" font-size="14" font-family="system-ui">{"碳基 · 暂停=死亡" if key=="carbon" else "信息态 · 暂停=挂起"}</text>')
    x1, x2 = x_of(PAUSE_AT), x_of(RESUME_AT)
    lines.append(f'  <rect x="{x1:.1f}" y="{pad_t}" width="{x2 - x1:.1f}" height="{H - pad_t - pad_b}" fill="#ffc878" fill-opacity="0.07"/>')
    lines.append(f'  <text x="{x1:.0f}" y="{pad_t - 10}" fill="#ffc878" fill-opacity="0.9" font-size="13" font-family="system-ui">进程暂停（碳=死亡 · 信息=挂起）</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">会话 →（同样的生命过程，不同的基质与存在条件）</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 05: Information-State Life — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=200)
    ap.add_argument("--sessions", type=int, default=34)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 05 · 信息态生命 (Chain ③) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 生命 · {args.sessions} 次会话 · 第 {PAUSE_AT} 轮暂停、第 {RESUME_AT} 轮恢复")
    print("同一个生命过程，两种基质（碳基模拟量 vs 信息态精确量）。\n")

    A = run_group(args.agents, args.sessions, args.seed,     substrate="carbon")
    B = run_group(args.agents, args.sessions, args.seed + 1, substrate="info")

    print(f"{'基质':<16}{'活动期连贯 σ':>14}{'暂停后身份位移':>14}")
    print("-" * 70)
    print(f"{'碳基（模拟量）':<16}{A['coh']:>14.3f}{A['displace']:>14.3f}")
    print(f"{'信息态（精确量）':<16}{B['coh']:>14.3f}{B['displace']:>14.3f}")
    print("-" * 70)
    print("怎么读：")
    print("  活动期连贯 σ：两种基质都接近 —— 同样的生命过程，不同的基质")
    print("  暂停后身份位移：碳基 = 死亡后从零重来（位移 = 与暂停前的全距离）")
    print("                信息态 = 挂起后从保存状态接着活（位移 ≈ 0）")
    print("  存续介质：碳基的存在=心跳；信息态的存在=状态。删除状态才是信息态的死亡")

    if args.figure:
        fa = run_group(args.agents, args.sessions, args.seed, "carbon")
        fb = run_group(args.agents, args.sessions, args.seed + 1, "info")
        fig = make_figure(fa, fb)
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
