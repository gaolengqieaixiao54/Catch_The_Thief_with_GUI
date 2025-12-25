import pygame

# 依次导入常量、UI 组件、地图逻辑、算法
import constants as c
from ui_elements import Button
from map import GridMap
from utils import (
    move_thief,
    find_cooperative_target,
    move_police_with_strategy,
    POLICE_ALGORITHMS
)

# --- Game 类 ---
class Game:
    def __init__(self, size, INITIAL_POLICE_COUNT):
        pygame.init()

        self.size = size

        # ===== 密度 =====
        self.density_options = c.DENSITY_OPTIONS
        self.current_density_index = c.DEFAULT_DENSITY_INDEX
        self.current_obstacle_density = self.density_options[self.current_density_index]
        self.map_data = None

        self.screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        pygame.display.set_caption(c.CAPTION)
        self.clock = pygame.time.Clock()

        # ===== FPS =====
        self.fps_options = c.FPS_OPTIONS
        self.current_fps_index = c.DEFAULT_FPS_INDEX
        self.fps = self.fps_options[self.current_fps_index]
        self.move_interval = 1000 / self.fps

        # ===== 警察算法选择 =====
        self.algorithm_list = list(POLICE_ALGORITHMS.keys())
        self.algorithm_index = 0
        self.police_algorithm = self.algorithm_list[self.algorithm_index]

        # ===== 字体 =====
        try:
            self.font_small = pygame.font.Font(c.SIMHEI_FONT_PATH, 22)
            self.font_medium = pygame.font.Font(c.SIMHEI_FONT_PATH, 26)
            self.font_large = pygame.font.Font(c.SIMHEI_FONT_PATH, 32)
            self.font_menu = self.font_large
            self.font_count = self.font_medium
        except FileNotFoundError:
            self.font_small = pygame.font.Font(None, 22)
            self.font_medium = pygame.font.Font(None, 26)
            self.font_large = pygame.font.Font(None, 32)
            self.font_menu = self.font_large
            self.font_count = self.font_medium

        # ===== 状态 =====
        self.running = True
        self.state = c.GAME_STATES["MENU"]
        self.turn = 0
        self.total_steps = 0
        self.game_over_reason = ""

        self.current_police_count = c.INITIAL_POLICE_COUNT
        self.move_timer = 0

        self.current_police_index = 0  # 追踪当前移动的警察编号
        self.sub_step_state = "POLICE"  # 当前子阶段：POLICE 或 THIEF

        self.max_history_size = 50
        self.history_states = []

        self.setup_menu()

    # ================== MENU 布局 ==================
    def setup_menu(self):
        center_x = c.SCREEN_WIDTH // 2
        button_w, button_h = 50, 40

        y_police = c.SCREEN_HEIGHT // 2 - 120
        y_density = c.SCREEN_HEIGHT // 2 - 40
        y_algo = c.SCREEN_HEIGHT // 2 + 40
        y_fps = c.SCREEN_HEIGHT // 2 + 120

        # ===== 警察数量按钮 =====
        self.btn_minus = Button((center_x - 100, y_police, button_w, button_h), "-", c.LIGHT_BLUE, c.GRAY, self.decrease_police)
        self.btn_plus = Button((center_x + 50, y_police, button_w, button_h), "+", c.LIGHT_BLUE, c.GRAY, self.increase_police)
        # ===== 障碍密度按钮 =====
        self.btn_density_prev = Button((center_x - 100, y_density, button_w, button_h), "<", c.LIGHT_BLUE, c.GRAY, self.decrease_density)
        self.btn_density_next = Button((center_x + 50, y_density, button_w, button_h), ">", c.LIGHT_BLUE, c.GRAY, self.increase_density)
        # ===== 算法选择按钮 =====
        self.btn_algo_prev = Button((center_x - 100, y_algo, button_w, button_h), "<", c.LIGHT_BLUE, c.GRAY, self.prev_algorithm)
        self.btn_algo_next = Button((center_x + 50, y_algo, button_w, button_h), ">", c.LIGHT_BLUE, c.GRAY, self.next_algorithm)
        # ===== FPS选择按钮 =====
        self.btn_fps_minus = Button((center_x - 100, y_fps, button_w, button_h), "-", c.LIGHT_BLUE, c.GRAY, self.decrease_fps)
        self.btn_fps_plus = Button((center_x + 50, y_fps, button_w, button_h), "+", c.LIGHT_BLUE, c.GRAY, self.increase_fps)
        # ===== 开始结束按钮 =====
        self.btn_start = Button((center_x - 100, c.SCREEN_HEIGHT // 2 + 180, 200, 50),
                                "开始游戏", c.BLUE, c.LIGHT_BLUE, self.start_game)
        self.btn_quit = Button((center_x - 100, c.SCREEN_HEIGHT // 2 + 180 + 60, 200, 50),
                               "退出游戏", c.RED, (255, 100, 100), self.quit_game)

    # ================== MENU 控制 ==================
    def increase_police(self):
        if self.current_police_count < c.MAX_POLICE:
            self.current_police_count += 1
    def decrease_police(self):
        if self.current_police_count > c.MIN_POLICE:
            self.current_police_count -= 1

    def increase_density(self):
        if self.current_density_index < len(self.density_options) - 1:
            self.current_density_index += 1
            self.current_obstacle_density = self.density_options[self.current_density_index]
    def decrease_density(self):
        if self.current_density_index > 0:
            self.current_density_index -= 1
            self.current_obstacle_density = self.density_options[self.current_density_index]

    def prev_algorithm(self):
        self.algorithm_index = (self.algorithm_index - 1) % len(self.algorithm_list)
        self.police_algorithm = self.algorithm_list[self.algorithm_index]
    def next_algorithm(self):
        self.algorithm_index = (self.algorithm_index + 1) % len(self.algorithm_list)
        self.police_algorithm = self.algorithm_list[self.algorithm_index]

    def increase_fps(self):
        if self.current_fps_index < len(self.fps_options) - 1:
            self.current_fps_index += 1
            self.fps = self.fps_options[self.current_fps_index]
            self.move_interval = 1000 / self.fps
    def decrease_fps(self):
        if self.current_fps_index > 0:
            self.current_fps_index -= 1
            self.fps = self.fps_options[self.current_fps_index]
            self.move_interval = 1000 / self.fps

    def start_game(self):
        # 初始化地图
        self.map_data = GridMap(
            self.size,
            self.current_police_count,
            self.current_obstacle_density
        )

        # 初始化游戏状态
        self.turn = 0
        self.total_steps = 0
        self.history_states.clear()
        self.game_over_reason = ""

        # 切换到运行状态
        self.state = c.GAME_STATES["RUNNING"]
    def quit_game(self):
        self.running = False

    # ================== MENU 绘制 ==================
    def draw_menu(self):
        cx = c.SCREEN_WIDTH // 2

        self.screen.blit(self.font_menu.render("警察抓小偷", True, c.WHITE),
                         self.font_menu.render("警察抓小偷", True, c.WHITE).get_rect(center=(cx, c.SCREEN_HEIGHT // 4)))

        def draw_item(label, value, y):
            self.screen.blit(self.font_medium.render(label, True, c.WHITE),
                             self.font_medium.render(label, True, c.WHITE).get_rect(center=(cx - 200, y)))
            self.screen.blit(self.font_medium.render(value, True, c.YELLOW),
                             self.font_medium.render(value, True, c.YELLOW).get_rect(center=(cx, y)))

        draw_item("警察数量", str(self.current_police_count), c.SCREEN_HEIGHT // 2 - 100)
        draw_item("障碍物密度", f"{self.current_obstacle_density:.2f}", c.SCREEN_HEIGHT // 2 - 20)
        draw_item("警察算法", self.police_algorithm, c.SCREEN_HEIGHT // 2 + 60)
        draw_item("FPS", str(self.fps), c.SCREEN_HEIGHT // 2 + 140)

        for btn in [
            self.btn_minus, self.btn_plus,
            self.btn_density_prev, self.btn_density_next,
            self.btn_algo_prev, self.btn_algo_next,
            self.btn_fps_minus, self.btn_fps_plus,
            self.btn_start, self.btn_quit
        ]:
            btn.draw(self.screen)

    # ================== RUNNING 导航栏 ==================
    def draw_top_bar(self):
        # 绘制背景
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, c.SCREEN_WIDTH, c.TOP_BAR_HEIGHT))
        # 底部装饰线
        pygame.draw.line(self.screen, c.GRAY, (0, c.TOP_BAR_HEIGHT - 1), (c.SCREEN_WIDTH, c.TOP_BAR_HEIGHT - 1), 1)

        padding = 20
        y_center = c.TOP_BAR_HEIGHT // 2

        # --- 左侧：核心进度 ---
        turn_surf = self.font_small.render(f"回合: {self.turn}", True, c.WHITE)
        self.screen.blit(turn_surf, (padding, y_center - turn_surf.get_height() // 2))

        # --- 中间：累积步数 ---
        step_surf = self.font_small.render(f"警察总步数: {self.total_steps}", True, c.LIGHT_BLUE)
        self.screen.blit(step_surf,
                         (c.SCREEN_WIDTH // 2 - step_surf.get_width() // 2, y_center - step_surf.get_height() // 2))

        # --- 右侧：运行状态 ---
        status_map = {
            c.GAME_STATES["RUNNING"]: ("进行中", c.GREEN),
            c.GAME_STATES["GAME_OVER"]: ("已结束", c.RED)
        }
        status_text, status_color = status_map.get(self.state, ("等待中", c.WHITE))

        state_surf = self.font_small.render(status_text, True, status_color)
        self.screen.blit(state_surf,
                         (c.SCREEN_WIDTH - state_surf.get_width() - padding, y_center - state_surf.get_height() // 2))
    def draw_bottom_bar(self):
        y_start = c.TOP_BAR_HEIGHT + c.GRID_SIZE * c.TILE_SIZE
        # 绘制背景
        pygame.draw.rect(self.screen, (20, 20, 20), (0, y_start, c.SCREEN_WIDTH, c.BOTTOM_BAR_HEIGHT))
        # 顶部装饰线
        pygame.draw.line(self.screen, c.GRAY, (0, y_start), (c.SCREEN_WIDTH, y_start), 1)

        padding = 20
        y_center = y_start + c.BOTTOM_BAR_HEIGHT // 2

        # --- 左侧：环境配置 ---
        config_text = f"配置: 警察x{len(self.map_data.police_positions)} | 密度:{self.current_obstacle_density:.2f}"
        config_surf = self.font_small.render(config_text, True, c.GRAY)
        self.screen.blit(config_surf, (padding, y_center - config_surf.get_height() // 2))

        # --- 右侧：当前算法 ---
        algo_text = f"AI算法: {self.police_algorithm}"
        algo_surf = self.font_small.render(algo_text, True, c.YELLOW)
        self.screen.blit(algo_surf, (c.SCREEN_WIDTH - algo_surf.get_width() - padding, y_center - algo_surf.get_height() // 2))

    # ================== 游戏逻辑 ==================
    def handle_turn(self):
        if not self.map_data or self.state != c.GAME_STATES["RUNNING"]:
            return

        # --- 1. 警察移动阶段 ---
        if self.sub_step_state == "POLICE":
            # 获取当前要移动的警察数据
            pid, cur_pos = self.map_data.police_positions[self.current_police_index]

            # 准备阻塞位置（其他警察的位置）
            blocked = {pos for i, (_, pos) in enumerate(self.map_data.police_positions) if
                       i != self.current_police_index}

            # 计算目标（依然使用协作逻辑，但只针对当前警察）
            police_targets = find_cooperative_target(self.map_data.thief_pos, self.map_data.police_positions,
                                                     self.map_data)
            target = police_targets.get(cur_pos, self.map_data.thief_pos)

            # 计算下一步
            next_pos = move_police_with_strategy(cur_pos, target, self.map_data, blocked, self.police_algorithm)

            # 执行移动
            if next_pos != cur_pos:
                self.map_data.police_positions[self.current_police_index] = (pid, next_pos)
                self.total_steps += 1

            # 检查抓捕
            if next_pos == self.map_data.thief_pos:
                self.state = c.GAME_STATES["GAME_OVER"]
                self.game_over_reason = f"警察 {pid} 完成抓捕"
                return

            # 轮向下一个警察或转入小偷回合
            self.current_police_index += 1
            if self.current_police_index >= len(self.map_data.police_positions):
                self.current_police_index = 0
                self.sub_step_state = "THIEF"

        # --- 2. 小偷移动阶段 ---
        elif self.sub_step_state == "THIEF":
            new_thief_pos = move_thief(self.map_data.thief_pos, self.map_data.police_positions, self.map_data)
            self.map_data.thief_pos = new_thief_pos

            # 检查小偷是否撞上警察
            if any(pos == self.map_data.thief_pos for _, pos in self.map_data.police_positions):
                self.state = c.GAME_STATES["GAME_OVER"]
                self.game_over_reason = "小偷无处可逃"
                return

            # 小偷动完后，才算一个完整回合结束，进行僵局检测
            self.turn += 1
            self.sub_step_state = "POLICE"
            self._check_stalemate()

    # ================== 僵局检测逻辑 ==================
    def _check_stalemate(self):
        current_state = self._get_current_state()
        if current_state in self.history_states:
            self.state = c.GAME_STATES["GAME_OVER"]
            self.game_over_reason = "进入循环僵局"
        else:
            self.history_states.append(current_state)
            if len(self.history_states) > self.max_history_size:
                self.history_states.pop(0)

    def _get_current_state(self):
        """格式化当前状态用于僵局检测"""
        police_pos_tuple = tuple(sorted([pos for _, pos in self.map_data.police_positions]))
        return (self.map_data.thief_pos, police_pos_tuple)

    # ================== 绘制地图 ==================
    def draw_grid(self):
        # 将内部循环变量名从 c 改为 col
        for row in range(c.GRID_SIZE):
            for col in range(c.GRID_SIZE):
                # 考虑顶部状态栏的偏移
                rect = pygame.Rect(
                    col * c.TILE_SIZE,
                    c.MAP_OFFSET_Y + row * c.TILE_SIZE,
                    c.TILE_SIZE,
                    c.TILE_SIZE
                )

                if self.map_data.map[row][col] == '#':
                    pygame.draw.rect(self.screen, c.BROWN, rect)
                else:
                    pygame.draw.rect(self.screen, c.GREEN, rect)

                # 绘制网格线
                pygame.draw.rect(self.screen, (50, 80, 50), rect, 1)

    def draw_entities(self):
        if not self.map_data:
            return

        # 绘制小偷 (红色圆圈)
        tr, tc = self.map_data.thief_pos
        center = (
            tc * c.TILE_SIZE + c.TILE_SIZE // 2,
            c.MAP_OFFSET_Y + tr * c.TILE_SIZE + c.TILE_SIZE // 2
        )
        pygame.draw.circle(self.screen, c.RED, center, c.TILE_SIZE // 2 - 4)

        # 绘制警察 (蓝色方块)
        for i, (pid, (pr, pc)) in enumerate(self.map_data.police_positions):
            rect = pygame.Rect(pc * c.TILE_SIZE + 4, c.MAP_OFFSET_Y + pr * c.TILE_SIZE + 4, c.TILE_SIZE - 8, c.TILE_SIZE - 8)

            # 如果是当前正在移动的警察，加粗边框或高亮
            if self.state == c.GAME_STATES[
                "RUNNING"] and self.sub_step_state == "POLICE" and i == self.current_police_index:
                pygame.draw.rect(self.screen, c.YELLOW, rect.inflate(4, 4), 2)  # 黄色高亮框

            pygame.draw.rect(self.screen, c.BLUE, rect)

            # 绘制警察编号
            id_text = self.font_small.render(str(pid), True, c.WHITE)
            self.screen.blit(id_text, id_text.get_rect(center=rect.center))

    # ================== 结束提示 ==================
    def display_game_over(self):
        # 1. 创建半透明遮罩层
        overlay = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # 最后一个参数 180 是透明度 (0-255)
        self.screen.blit(overlay, (0, 0))

        # 2. 准备绘制弹窗面板
        panel_width, panel_height = 320, 240
        panel_rect = pygame.Rect(
            (c.SCREEN_WIDTH - panel_width) // 2,
            (c.SCREEN_HEIGHT - panel_height) // 2,
            panel_width,
            panel_height
        )
        pygame.draw.rect(self.screen, (40, 40, 40), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, c.YELLOW, panel_rect, 2, border_radius=15)

        # 3. 渲染文字内容
        cx = c.SCREEN_WIDTH // 2
        start_y = panel_rect.top + 30

        results = [
            (self.game_over_reason, c.YELLOW, self.font_large),
            (f"总回合数: {self.turn}", c.WHITE, self.font_medium),
            (f"警察总步数: {self.total_steps}", c.WHITE, self.font_medium),
            (f"使用算法: {self.police_algorithm}", c.GRAY, self.font_small),
            ("", c.WHITE, self.font_small),  # 空行
            ("按 [ESC] 或 [空格] 返回菜单", c.LIGHT_BLUE, self.font_small)
        ]

        for text, color, font in results:
            if text == "":
                start_y += 10
                continue
            surf = font.render(text, True, color)
            rect = surf.get_rect(center=(cx, start_y))
            self.screen.blit(surf, rect)
            start_y += 35

    # ================== 游戏主循环 ==================
    def run(self):
        while self.running:
            dt = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # 菜单状态下的事件
                if self.state == c.GAME_STATES["MENU"]:
                    for btn in [
                        self.btn_minus, self.btn_plus,
                        self.btn_density_prev, self.btn_density_next,
                        self.btn_algo_prev, self.btn_algo_next,
                        self.btn_fps_minus, self.btn_fps_plus,
                        self.btn_start, self.btn_quit
                    ]:
                        btn.handle_event(event)

                # 游戏结束状态下的事件：按键返回菜单
                elif self.state == c.GAME_STATES["GAME_OVER"]:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
                            self.state = c.GAME_STATES["MENU"]

            self.screen.fill(c.BLACK)

            if self.state == c.GAME_STATES["MENU"]:
                self.draw_menu()

            elif self.state == c.GAME_STATES["RUNNING"]:
                self.move_timer += dt
                if self.move_timer >= self.move_interval:
                    self.handle_turn()
                    self.move_timer = 0

                self.draw_top_bar()
                self.draw_grid()
                self.draw_entities()
                self.draw_bottom_bar()

            elif self.state == c.GAME_STATES["GAME_OVER"]:
                # 游戏结束时，先画出最后的地图状态，再覆盖弹窗
                self.draw_top_bar()
                self.draw_grid()
                self.draw_entities()
                self.draw_bottom_bar()
                self.display_game_over()

            pygame.display.flip()

        pygame.quit()



if __name__ == '__main__':
    game = Game(c.GRID_SIZE, c.INITIAL_POLICE_COUNT)
    game.run()