import pandas as pd
import itertools
import time
from tqdm import tqdm  # 用于显示进度条
# 导入修改后的游戏代码中的模拟函数和常量
from main import run_simulation, GRID_SIZE

# --- 实验配置 ---
POLICE_COUNTS = [3, 4, 5, 6, 7]  # P 组合
OBSTACLE_DENSITIES = [0.05, 0.15, 0.25]  # O 组合
N_RUNS = 100  # 每个场景重复运行次数
MAX_TURNS = 2000  # 单次模拟的最大回合数，防止无限循环

# 1. 生成所有实验场景
experiments = list(itertools.product(POLICE_COUNTS, OBSTACLE_DENSITIES))
total_runs = len(experiments) * N_RUNS

# 2. 初始化数据存储
results = []

print(f"--- 警察抓小偷实验开始 ---")
print(f"总场景数: {len(experiments)}")
print(f"每个场景重复次数: {N_RUNS}")
print(f"总运行次数: {total_runs}")

start_time = time.time()

# 3. 运行实验
with tqdm(total=total_runs, desc="Running Experiments") as pbar:
    for police_count, density in experiments:
        # 对每个 (P, O) 组合，重复运行 N_RUNS 次
        for run_id in range(N_RUNS):
            # 自动调用 run_simulation 函数
            turns, end_reason = run_simulation(
                grid_size=GRID_SIZE,
                police_count=police_count,
                obstacle_density=density,
                max_turns=MAX_TURNS
            )

            # 记录结果
            results.append({
                "Police_Count": police_count,
                "Obstacle_Density": density,
                "Run_ID": run_id + 1,
                "Turns": turns,
                "End_Reason": end_reason
            })

            pbar.update(1)

end_time = time.time()

# 4. 数据后处理与保存
df = pd.DataFrame(results)

# 聚合统计结果 (方便快速查看)
summary = df.groupby(['Police_Count', 'Obstacle_Density']).agg(
    Avg_Turns=('Turns', 'mean'),
    Capture_Rate=('End_Reason', lambda x: (x == 'Capture').sum() / N_RUNS),
    Stalemate_Rate=('End_Reason', lambda x: (x == 'Stalemate').sum() / N_RUNS)
).reset_index()

# 5. 保存到 CSV 文件
timestamp = time.strftime("%Y%m%d_%H%M%S")
filename_detail = f"experiment_results_detail_{timestamp}.csv"
filename_summary = f"experiment_results_summary_{timestamp}.csv"

df.to_csv(filename_detail, index=False, encoding='utf_8_sig')
summary.to_csv(filename_summary, index=False, encoding='utf_8_sig')

print(f"\n--- 实验完成 ---")
print(f"总耗时: {end_time - start_time:.2f} 秒")
print(f"详细结果已保存到: {filename_detail}")
print(f"统计摘要已保存到: {filename_summary}")
print("\n摘要:")
print(summary)