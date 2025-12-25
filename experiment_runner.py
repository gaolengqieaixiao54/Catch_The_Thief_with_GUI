import os
import pandas as pd
import sys  # <--- 必须导入 sys 模块
from tqdm import tqdm
from main import Game
import constants as c
from utils import POLICE_ALGORITHMS

# ================== 实验配置 ==================
POLICE_COUNTS = list(range(2, 8))
DENSITIES = [0.05, 0.15, 0.25]
ALGORITHMS = list(POLICE_ALGORITHMS.keys())

TRIALS_PER_GROUP = 20
MAX_TURNS_SAFETY = 1000

OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def run_experiment():
    all_results = []
    total_groups = len(POLICE_COUNTS) * len(DENSITIES) * len(ALGORITHMS)

    print(f"开始自动化实验任务...")

    # 使用 sys.stdout 配合 dynamic_ncols=True 可以更好地在 IDE 中刷新
    pbar_total = tqdm(total=total_groups, desc="总进度", position=0, leave=True, file=sys.stdout, dynamic_ncols=True)

    for count in POLICE_COUNTS:
        for density in DENSITIES:
            for algo in ALGORITHMS:
                group_desc = f"P={count}|D={density:.2f}|{algo}"
                group_data = []

                # 每一组的 20 次实验不新开进度条，而是更新主进度条的后缀
                for trial in range(TRIALS_PER_GROUP):
                    # 动态更新条右侧的文字
                    pbar_total.set_postfix_str(f"当前: {group_desc} | 轮次: {trial + 1}/{TRIALS_PER_GROUP}")

                    # 传入 headless=True 确保不弹窗
                    game = Game(c.GRID_SIZE, count, headless=True)
                    game.start_game(
                        algo_override=algo,
                        density_override=density,
                        count_override=count
                    )

                    while game.state == c.GAME_STATES["RUNNING"] and game.turn < MAX_TURNS_SAFETY:
                        game.handle_turn()

                    reason = game.game_over_reason if game.turn < MAX_TURNS_SAFETY else "Timeout"
                    res = {
                        "police_count": count,
                        "density": density,
                        "algorithm": algo,
                        "trial_id": trial + 1,
                        "total_turns": game.turn,
                        "total_steps": game.total_steps,
                        "game_over_reason": reason
                    }
                    all_results.append(res)
                    group_data.append(res)

                # 保存每组详情
                group_df = pd.DataFrame(group_data)
                safe_algo_name = algo.replace("*", "Star")
                filename = f"detail_P{count}_D{density}_{safe_algo_name}.csv"
                group_df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)

                # 完成一组，进度条加 1
                pbar_total.update(1)

    pbar_total.close()
    print("\n\n所有实验逻辑运行完毕，正在生成汇总报表...")

    # --- 数据汇总逻辑 ---
    full_df = pd.DataFrame(all_results)
    full_df.to_csv(os.path.join(OUTPUT_DIR, "all_trials_raw.csv"), index=False)

    summary = full_df.groupby(["police_count", "density", "algorithm"]).agg({
        "total_turns": ["mean", "std"],
        "total_steps": ["mean", "std"]
    }).reset_index()

    summary.columns = [
        "police_count", "density", "algorithm",
        "avg_turns", "std_turns", "avg_steps", "std_steps"
    ]

    summary.to_csv(os.path.join(OUTPUT_DIR, "experiment_summary.csv"), index=False)
    print(f"✅ 实验成功！报表位置: {os.path.join(OUTPUT_DIR, 'experiment_summary.csv')}")


if __name__ == "__main__":
    run_experiment()