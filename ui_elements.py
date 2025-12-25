# 可重用的 UI 控件
import pygame
import constants as c

# --- Button 类 ---
class Button:
    def __init__(self, rect, text, color, hover_color, action=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False

        # 使用全局字体
        try:
            self.font = pygame.font.Font(c.SIMHEI_FONT_PATH, 24)
        except FileNotFoundError:
            self.font = pygame.font.Font(None, 24)  # 备用字体

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=5)

        text_surface = self.font.render(self.text, True, c.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.action:
                self.action()
                return True
        return False