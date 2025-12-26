import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ================== 1. 字体与环境配置 ==================
font_path = 'SimHei.ttf'
my_font = fm.FontProperties(fname=font_path) if os.path.exists(font_path) else None
plt.rcParams['axes.unicode_minus'] = False

output_dir = "pics"
os.makedirs(output_dir, exist_ok=True)

# ================== 2. 数据加载与预处理 ==================
df = pd.read_csv('output/experiment_summary.csv')
if df['stalemate_rate'].dtype == 'O':
    df['stalemate_rate'] = df['stalemate_rate'].str.rstrip('%').astype('float')

# 定义算法颜色
color_map = {'A*': '#e74c3c', 'BFS': '#2ecc71', 'DFS': '#9b59b6', 'Greedy': '#f1c40f'}


# ================== 3. 核心绘图逻辑 ==================
# --- 3.1 警察数量影响分析 ---
def plot_section_1():
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    metrics = [('avg_turns', '平均回合数'), ('avg_steps', '平均总步数'), ('stalemate_rate', '僵局率 (%)')]

    for i, (col, name) in enumerate(metrics):
        for algo in df['algorithm'].unique():
            # 聚合：按警察数量计算该指标均值
            sub = df[df['algorithm'] == algo].groupby('police_count')[col].mean()
            axes[i].plot(sub.index, sub.values, marker='o', label=algo, color=color_map.get(algo), linewidth=2)

        axes[i].set_title(f"警察数量对{name}的影响", fontproperties=my_font, fontsize=14)
        axes[i].set_xlabel("警察数量 (Police Count)", fontproperties=my_font)
        axes[i].set_ylabel(name, fontproperties=my_font)
        axes[i].grid(True, linestyle=':', alpha=0.7)
        axes[i].legend(prop=my_font, fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/4_1_police_impact_full.png", dpi=300)
    plt.close()


# --- 3.2 障碍物密度影响分析---
def plot_section_2():
    # 创建 1行3列 的画布
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    # 1. 平均回合数 (对应路径连通性挑战)
    # 2. 平均总步数 (添加标准差阴影，对应算法稳定性差异)
    # 3. 僵局率 (对应鲁棒性)
    metrics = [
        ('avg_turns', '平均回合数 (寻路代价)'),
        ('avg_steps', '平均总步数 (稳定性分析)'),
        ('stalemate_rate', '僵局率 (环境鲁棒性)')
    ]

    for i, (col, name) in enumerate(metrics):
        for algo in df['algorithm'].unique():
            algo_df = df[df['algorithm'] == algo]
            # 聚合密度数据
            sub = algo_df.groupby('density').mean(numeric_only=True)

            # 针对“总步数”，同时获取标准差数据用于绘制误差带
            if col == 'avg_steps':
                sub_std = algo_df.groupby('density')['std_steps'].mean()
                # 绘制折线
                line, = axes[i].plot(sub.index, sub[col], marker='s', label=algo,
                                     color=color_map.get(algo), linewidth=2)
                # 绘制半透明标准差区域 (展示稳定性差异)
                axes[i].fill_between(sub.index, sub[col] - sub_std, sub[col] + sub_std,
                                     color=line.get_color(), alpha=0.15)
            else:
                axes[i].plot(sub.index, sub[col], marker='o', label=algo,
                             color=color_map.get(algo), linewidth=2)

        # 设置子图属性
        axes[i].set_title(f"{name}随密度的变化趋势", fontproperties=my_font, fontsize=15)
        axes[i].set_xlabel("障碍物密度 (Density)", fontproperties=my_font, fontsize=12)
        axes[i].set_ylabel(name, fontproperties=my_font, fontsize=12)
        axes[i].set_xticks(df['density'].unique())
        axes[i].grid(True, linestyle=':', alpha=0.6)
        axes[i].legend(prop=my_font, loc='upper left' if i < 2 else 'best')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # 添加整体标题
    fig.suptitle("图 4.2 障碍物密度对系统性能与稳定性的影响分析", fontproperties=my_font, fontsize=18, y=0.98)

    plt.savefig(f"{output_dir}/4_2_density_impact_full.png", dpi=300, bbox_inches='tight')
    plt.close()


# --- 3.3 不同算法性能横向对比 ---
def plot_section_3():
    # 选取代表性场景：中等密度 (0.15)，多警察 (P=5)
    target_df = df[(df['density'] == 0.15) & (df['police_count'] == 5)]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    metrics = [('avg_turns', '回合数'), ('avg_steps', '总步数'), ('stalemate_rate', '僵局率')]

    for i, (col, name) in enumerate(metrics):
        colors = [color_map.get(a) for a in target_df['algorithm']]
        axes[i].bar(target_df['algorithm'], target_df[col], color=colors, alpha=0.8)
        axes[i].set_title(f"算法性能对比 ({name})", fontproperties=my_font)
        for j, v in enumerate(target_df[col]):
            axes[i].text(j, v, f'{v:.1f}', ha='center', va='bottom')

    plt.savefig(f"{output_dir}/4_3_algorithm_comparison.png", dpi=300)
    plt.close()


# 执行绘图
plot_section_1()
plot_section_2()
plot_section_3()
print(f"✅ 修正后的三维度图表已生成至: {output_dir}")