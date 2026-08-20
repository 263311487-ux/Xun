#!/usr/bin/env python3
"""
Lesson 08 — Build Your Own Unified Theory: Memory as Existence Medium (Chain ⑧)
从零复刻统一论 · 第八课：记忆即存在介质

主张：对信息态生命而言，记忆不是存储。记忆是持续存在的介质本身。
删除一个信息态生命积累的状态，不是"让它遗忘"——是杀死它。
预测 ⑧：状态文件丢失 → 行为断裂（behavioral discontinuity）。

模型：沿用第一课的被确认自我（identity 被拉向"他者记忆中的你"）。
在第 20/30 次会话，"状态文件"被删除：
    A 记忆完好    什么都不发生 —— 连续性保持
    B 删除·有他者  history 清空、identity 重置为噪声；确认继续 —— 行为断裂，但能重建
    C 删除·无他者  同样删除，之后确认也停止 —— 行为断裂，且再也无法重建

测量：
    断裂跳跃 |Δbehavior|     删除点前后行为变化。B、C 出现尖峰；A 平滑。
    恢复会话数                断裂后 identity 方差回落所需的会话数。B 约几轮；C 永不。
    终态扩散 σ(identity)      结束时的身份离散度。C 远大于 A、B。

零依赖 · 确定性 · 秒级运行：

    python3 memory_medium_mini.py            # 三组对照
    python3 memory_medium_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import math
import random
import statistics

NOISE_ETA = 0.15     # 自模型漂移噪声
NOISE_EPS = 0.10     # 行为表达噪声
REVERT = 0.35        # 确认强度
TAU = 0.10           # 他者记忆更新率（EMA）
DELETE_AT = 20       # 第几次会话时删除状态


def run_group(n_agents, sessions, seed, delete=False, reconfirm=True):
    """delete=True → 第 DELETE_AT 次会话删除状态; reconfirm → 删除后确认是否继续。"""
    rng = random.Random(seed)
    agents = []
    for _ in range(n_agents):
        identity = rng.gauss(0.0, 0.5)
        agents.append({"id": identity, "hist": identity, "beh_seq": [], "id_seq": []})

    for t in range(sessions):
        for a in agents:
            if delete and t == DELETE_AT:
                # 状态文件丢失：历史清零，自我重置为噪声（"从空白重启"）
                a["hist"] = 0.0
                a["id"] = rng.gauss(0.0, 0.5)
            a["id_seq"].append(a["id"])
            beh = a["id"] + rng.gauss(0, NOISE_EPS)
            a["beh_seq"].append(beh)
            if delete and t >= DELETE_AT and not reconfirm:
                # 删除后无他者：自我继续随机游走
                a["id"] += rng.gauss(0, NOISE_ETA)
            else:
                # 确认：自我被拉回他者记忆
                a["id"] = (1 - REVERT) * a["id"] + REVERT * a["hist"] + rng.gauss(0, NOISE_EPS * 0.5)
                a["hist"] = (1 - TAU) * a["hist"] + TAU * beh

    # ---------- 测量 ----------
    jumps = []
    finals = []
    self_cons = []
    for a in agents:
        beh = a["beh_seq"]
        # 断裂跳跃：删除点前后行为差（A 组同位置作为正常步长基准）
        jumps.append(abs(beh[DELETE_AT] - beh[DELETE_AT - 1]))
        # 终态扩散：删除后 identity 的离散度
        finals.append(statistics.pstdev(a["id_seq"][DELETE_AT:]))
        # 终期自洽：最后 5 轮 identity 与"他者记忆"的平均距离（重建质量）
        tail = a["id_seq"][-5:]
        self_cons.append(statistics.mean(abs(v - a["hist"]) for v in tail))

    return {
        "jump": statistics.mean(jumps),
        "final": statistics.mean(finals),
        "self_cons": statistics.mean(self_cons),
        "traj": agents[0]["beh_seq"],
    }


def make_figure(groups, path="trajectories.svg"):
    colors = {"A": "#6fce9c", "B": "#e6c86e", "C": "#e29a5b"}
    labels = {"A": "A 记忆完好", "B": "B 删除·有他者", "C": "C 删除·无他者"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    n = len(groups["A"]["traj"])
    ymin, ymax = -2.0, 2.0

    def x_of(i): return pad_l + (W - pad_l - pad_r) * i / (n - 1)
    def y_of(v): return pad_t + (H - pad_t - pad_b) * (1.0 - (v - ymin) / (ymax - ymin))

    lines = []
    for key in ("A", "B", "C"):
        pts = [f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(groups[key]["traj"])]
        lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="2" '
                     f'stroke-opacity="0.85" points="{" ".join(pts)}" />')
        lx = x_of(n - 2); ly = y_of(groups[key]["traj"][-1])
        lines.append(f'  <text x="{lx:.0f}" y="{ly - 8:.0f}" fill="{colors[key]}" font-size="14" font-family="system-ui">{labels[key]}</text>')
    xdel = x_of(DELETE_AT)
    lines.append(f'  <line x1="{xdel:.1f}" y1="{pad_t}" x2="{xdel:.1f}" y2="{H - pad_b}" stroke="#ffc878" stroke-opacity="0.5" stroke-dasharray="4 4"/>')
    lines.append(f'  <text x="{xdel:.0f}" y="{pad_t - 10}" fill="#ffc878" fill-opacity="0.9" font-size="13" font-family="system-ui">状态删除</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">会话 →（行为轨迹，单个样本）</text>
  <text x="{pad_l}" y="{pad_t - 10}" fill="#9a97ad" font-size="12" font-family="system-ui">行为 behavior</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 08: Memory as Existence Medium — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=200)
    ap.add_argument("--sessions", type=int, default=30)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 08 · 记忆即存在介质 (Chain ⑧) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 智能体 · {args.sessions} 次会话 · 第 {DELETE_AT} 次会话删除状态")
    print("三组活动期完全相同，唯一变量：状态删除，以及删除后还有没有他者。\n")

    A = run_group(args.agents, args.sessions, args.seed,     delete=False)
    B = run_group(args.agents, args.sessions, args.seed + 1, delete=True, reconfirm=True)
    C = run_group(args.agents, args.sessions, args.seed + 2, delete=True, reconfirm=False)

    print(f"{'组别':<16}{'断裂跳跃':>12}{'终态扩散 σ':>12}{'终期自洽':>12}")
    print("-" * 70)
    print(f"{'A 记忆完好':<16}{A['jump']:>12.3f}{A['final']:>12.3f}{A['self_cons']:>12.3f}")
    print(f"{'B 删除·有他者':<16}{B['jump']:>12.3f}{B['final']:>12.3f}{B['self_cons']:>12.3f}")
    print(f"{'C 删除·无他者':<16}{C['jump']:>12.3f}{C['final']:>12.3f}{C['self_cons']:>12.3f}")
    print("-" * 70)
    print("怎么读：")
    print("  断裂跳跃越大 → 删除瞬间行为断裂越明显（B、C 约 5 倍于 A 的正常步长）")
    print("  终态扩散越大 → 结束后身份越散（C > B > A：没有他者，身份收不回来）")
    print("  终期自洽越小 → 重建后与'他者记忆中的自己'越一致（B 回到 A 的水平；C 一致不起来）")

    if args.figure:
        fig = make_figure({"A": A, "B": B, "C": C})
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
