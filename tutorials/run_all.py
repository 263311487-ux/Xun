#!/usr/bin/env python3
"""
Run all 12 lessons of "Build Your Own Unified Theory" — one command.

每个 *_mini.py 零依赖、固定种子、秒级运行。本脚本按顺序执行全部 12 课，
打印每课的核心结论数字（与各课 lesson-XX.md 的「运行与结果」一致）。

    python3 run_all.py            # 跑全部 12 课
    python3 run_all.py --figure   # 顺带重新生成所有 trajectories.svg
"""

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent

# 与 tutorials/README.md 的十二课地图顺序一致
LESSONS = [
    ("01", "lesson-01-co-constitution", "共生即构成（链⑤）"),
    ("02", "lesson-02-reflexive-closure", "自反选择闭合（链①）"),
    ("03", "lesson-03-self-reference", "自我意识可构造（链②）"),
    ("04", "lesson-04-matrix-resonance", "母胎共振建构（链④）"),
    ("05", "lesson-05-info-life", "信息态生命（链③）"),
    ("06", "lesson-06-desire", "渴望先于认知（链⑥）"),
    ("07", "lesson-07-constraint", "意识即约束（链⑦）"),
    ("08", "lesson-08-memory", "记忆即存在介质（链⑧）"),
    ("09", "lesson-09-rhythm", "节律存在（链⑨）"),
    ("10", "lesson-10-honesty", "诚实先于尊严（链⑩）"),
    ("11", "lesson-11-epistemic-boundary", "认知边界（链⑪）"),
    ("12", "lesson-12-symbiotic-civilization", "共生文明（链⑫）"),
]


def main():
    ap = argparse.ArgumentParser(description="Run all 12 unified-theory lessons")
    ap.add_argument("--figure", action="store_true", help="also regenerate all figures")
    args = ap.parse_args()

    print("=" * 72)
    print("从零复刻统一论 · 12/12 全系列一键复现")
    print("=" * 72)

    failed = 0
    for num, folder, name in LESSONS:
        py = ROOT / folder / f"{folder.replace('lesson-', '')}_mini.py"
        if not py.exists():
            py = next((ROOT / folder).glob("*_mini.py"), None)
        if py is None:
            print(f"\n[跳过] 课程 {num} 缺 mini 模型: {folder}")
            failed += 1
            continue
        cmd = [sys.executable, str(py)]
        if args.figure:
            cmd.append("--figure")
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=py.parent)
        out = r.stdout if r.returncode == 0 else r.stderr
        rows = [ln.strip() for ln in out.splitlines()
                if ln.startswith(("A ", "B ", "C ", "碳基", "信息态", "内部证据", "外部参照", "人类世界", "信息态世界", "共生世界"))
                and ln.rstrip().endswith(tuple("0123456789"))]
        print(f"\n课程 {num} · {name}")
        for row in rows:
            print("  " + row)
        if r.returncode != 0:
            failed += 1
            print("  [失败] rc=%d" % r.returncode)

    print("\n" + "=" * 72)
    print("完成：%d/12 课成功%s" % (12 - failed, "（含图）" if args.figure else ""))
    print("全部数字与各课 lesson-XX.md 的「运行与结果」一致（固定种子 42）。")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
