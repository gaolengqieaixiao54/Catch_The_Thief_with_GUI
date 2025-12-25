# GridMap 类
import random

class GridMap:
    def __init__(self, size, police_count, obstacle_density):
        self.size = size
        self.map = [['.' for _ in range(size)] for _ in range(size)]    #. 代表空地，# 代表障碍物
        self.thief_pos = None       # 单个元组 (r, c)
        self.police_positions = []  # 带 ID 的列表：[(id, (r,c)), ...
        self._initialize_map(police_count, obstacle_density)

        positions = self._place_entity('P', count=police_count)
        self.police_positions = [(i, pos) for i, pos in enumerate(positions)]

    def _is_valid(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    # 确保角色不会出生在墙里或彼此重叠
    def _place_entity(self, entity_char, count=1):
        positions = []
        while len(positions) < count:
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            if self.map[r][c] == '.':
                self.map[r][c] = entity_char
                positions.append((r, c))
        return positions

    def _initialize_map(self, police_count, obstacle_density):
        num_obstacles = int(self.size * self.size * obstacle_density)
        for _ in range(num_obstacles):
            r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            self.map[r][c] = '#'

        self.thief_pos = self._place_entity('T')[0]

    # A* 和 BFS 依赖算法
    def get_neighbors(self, pos):
        r, c = pos
        neighbors = []
        MOVES = [(0, 1), (0, -1), (1, 0), (-1, 0)]  #只允许上下左右移动，不允许斜对角移动
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if self._is_valid(nr, nc) and self.map[nr][nc] != '#':
                neighbors.append((nr, nc))
        return neighbors

    # 移动前再次确认目标点不是墙
    def update_entity_pos(self, old_pos, new_pos):
        if self._is_valid(new_pos[0], new_pos[1]) and self.map[new_pos[0]][new_pos[1]] == '#':
            return old_pos
        return new_pos

    # 确保警察间不相撞
    def get_neighbors_with_blocked(self, pos, blocked_positions):
        r, c = pos
        neighbors = []
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r+dr, c+dc
            if self._is_valid(nr, nc) and self.map[nr][nc] != '#' \
               and (nr, nc) not in blocked_positions:
                neighbors.append((nr, nc))
        return neighbors