# 核心算法
import heapq
from collections import deque

# ================== 基础启发函数：曼哈顿距离 ==================
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ================== 核心算法：A*==================
def a_star_next_step(game_map, start, goal, blocked_positions):
    pq = [(0, start)]
    g_score = {start: 0}
    came_from = {}

    while pq:
        _, current = heapq.heappop(pq)

        if current == goal:
            while current in came_from and came_from[current] != start:
                current = came_from[current]
            return current

        for neighbor in game_map.get_neighbors_with_blocked(
                current,
                blocked_positions - {goal}  # ⭐ 允许进入目标格
        ):
            new_g = g_score[current] + 1
            if neighbor not in g_score or new_g < g_score[neighbor]:
                g_score[neighbor] = new_g
                f = new_g + heuristic(neighbor, goal)
                heapq.heappush(pq, (f, neighbor))
                came_from[neighbor] = current

    return start

# ================== 核心算法：BFS ==================
def bfs_next_step(game_map, start, goal, blocked_positions):
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for neighbor in game_map.get_neighbors_with_blocked(current, blocked_positions):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    if goal not in came_from:
        return start

    cur = goal
    while came_from[cur] != start and came_from[cur] is not None:
        cur = came_from[cur]
    return cur

# ================== 核心算法：DFS ==================
def dfs_next_step(game_map, start, goal, blocked_positions):
    stack = [start]
    came_from = {start: None}

    while stack:
        current = stack.pop()

        if current == goal:
            break

        for neighbor in game_map.get_neighbors_with_blocked(current, blocked_positions):
            if neighbor not in came_from:
                came_from[neighbor] = current
                stack.append(neighbor)

    if goal not in came_from:
        return start

    cur = goal
    while came_from[cur] != start and came_from[cur] is not None:
        cur = came_from[cur]
    return cur

# ================== 核心算法：GREEDY ==================
def greedy_next_step(game_map, start, goal, blocked_positions):
    pq = [(heuristic(start, goal), start)]
    came_from = {start: None}

    while pq:
        _, current = heapq.heappop(pq)

        if current == goal:
            break

        for neighbor in game_map.get_neighbors_with_blocked(current, blocked_positions):
            if neighbor not in came_from:
                came_from[neighbor] = current
                heapq.heappush(pq, (heuristic(neighbor, goal), neighbor))

    if goal not in came_from:
        return start

    cur = goal
    while came_from[cur] != start and came_from[cur] is not None:
        cur = came_from[cur]
    return cur

# ================== 核心算法：团队协作逻辑  ==================
def find_cooperative_target(thief_pos, police_positions, game_map):
    """
    返回：{(r,c): target_pos}
    """
    police_targets = {}

    # 只取坐标
    pure_positions = [pos for _, pos in police_positions]

    # 冲刺判定（固定判定距离为 3）
    if any(heuristic(p, thief_pos) <= 3 for p in pure_positions):
        return {p: thief_pos for p in pure_positions}

    # 围堵模式
    tr, tc = thief_pos
    chase_area = []

    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
        nr, nc = tr + dr, tc + dc
        if game_map._is_valid(nr, nc) and game_map.map[nr][nc] != '#':
            chase_area.append((nr, nc))

    if not chase_area:
        return {p: thief_pos for p in pure_positions}

    remaining_targets = set(chase_area)

    sorted_police = sorted(
        pure_positions,
        key=lambda p: heuristic(p, thief_pos)
    )

    for p in sorted_police:
        best_target = None
        min_dist = float('inf')

        for target in remaining_targets:
            dist = get_a_star_distance(game_map, p, target)
            if dist is not None and dist < min_dist:
                min_dist = dist
                best_target = target

        police_targets[p] = best_target if best_target else thief_pos
        if best_target:
            remaining_targets.remove(best_target)

    return police_targets

# ================== 辅助函数：快速获取 A* 路径长度  ==================
def get_a_star_distance(game_map, start, goal):
    """
    运行 A* 并返回从起点到目标的实际路径长度 (g_score)。
    """
    pq = [(0, start)]  # (f_score, pos)
    g_score = {start: 0}

    while pq:
        _, current = heapq.heappop(pq)

        if current == goal:
            return g_score[current]

        for neighbor in game_map.get_neighbors(current):
            new_g_score = g_score[current] + 1

            if neighbor not in g_score or new_g_score < g_score[neighbor]:
                g_score[neighbor] = new_g_score
                f_score = new_g_score + heuristic(neighbor, goal)
                heapq.heappush(pq, (f_score, neighbor))

    return None  # 无法到达

# ================== 警察协作移动逻辑 ==================
POLICE_ALGORITHMS = {
    "A*": a_star_next_step,
    "BFS": bfs_next_step,
    "DFS": dfs_next_step,
    "Greedy": greedy_next_step,
}

# 策略选择接口
def move_police_with_strategy(
    police_pos,
    target_pos,
    game_map,
    blocked_positions,
    algorithm_name
):
    algo_func = POLICE_ALGORITHMS.get(algorithm_name, a_star_next_step)
    return algo_func(game_map, police_pos, target_pos, blocked_positions)

def cooperative_police_move(
        police_positions,  # [(pid, (r,c)), ...]
        thief_pos,
        game_map,
        algorithm_name
):
    new_positions = []

    # 只取坐标
    pure_positions = [pos for _, pos in police_positions]
    blocked_positions = set(pure_positions)

    police_targets = find_cooperative_target(
        thief_pos,
        police_positions,
        game_map
    )

    for pid, police_pos in police_positions:
        blocked_positions.remove(police_pos)

        target = police_targets.get(police_pos, thief_pos)
        next_pos = move_police_with_strategy(
            police_pos,
            target,
            game_map,
            blocked_positions,
            algorithm_name
        )

        blocked_positions.add(next_pos)
        new_positions.append((pid, next_pos))

    return new_positions

# ================== 小偷逃跑逻辑：最大化最小距离策略 ==================
def move_thief(thief_pos, police_positions, game_map):
    r, c = thief_pos
    police_cells = {p for _, p in police_positions}
    candidates = [
        pos for pos in game_map.get_neighbors(thief_pos) + [thief_pos]
        if pos not in police_cells
    ]

    best_pos = thief_pos
    best_score = -1

    for next_pos in candidates:
        # 只取警察的位置 (r,c)
        distances = [
            heuristic(next_pos, p_pos)
            for _, p_pos in police_positions
        ]
        score = min(distances)  # 计算小偷离最近的警察有多远

        if score > best_score:
            best_score = score
            best_pos = next_pos

    return best_pos