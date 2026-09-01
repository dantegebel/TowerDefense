"""
Pantallas de Victoria y Derrota (Fin de Partida) para 'Reino en Asedio'.
"""

import math
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_UI_BG, COLOR_UI_BORDER,
    COLOR_UI_PANEL, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_ROYAL_RED,
    COLOR_WHITE, COLOR_STONE_LIGHT
)
from engine.audio import sound_manager

class GameOverScene:
    def __init__(self, victory, lives_left, max_lives, score, enemies_killed, level_data, on_next_level_cb, on_retry_cb, on_menu_cb):
        self.victory = victory
        self.lives_left = lives_left
        self.max_lives = max_lives
        self.score = score
        self.enemies_killed = enemies_killed
        self.level_data = level_data
        
        self.on_next_level = on_next_level_cb
        self.on_retry = on_retry_cb
        self.on_menu = on_menu_cb
        
        # Calcular estrellas
        if victory:
            life_ratio = lives_left / max(1, max_lives)
            if life_ratio >= 0.85:
                self.stars = 3
            elif life_ratio >= 0.40:
                self.stars = 2
            else:
                self.stars = 1
        else:
            self.stars = 0

        self.anim_time = 0.0
        self.font_title = pygame.font.SysFont("georgia", 38, bold=True)
        self.font_main = pygame.font.SysFont("georgia", 20, bold=True)
        self.font_small = pygame.font.SysFont("georgia", 15)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            
            # Botones en la pantalla
            btn_w, btn_h = 180, 48
            btn_y = SCREEN_HEIGHT // 2 + 155
            
            if self.victory and self.level_data["id"] < 3:
                # 3 Botones: Menú, Reintentar, Siguiente Nivel
                b1 = pygame.Rect(SCREEN_WIDTH // 2 - 290, btn_y, btn_w, btn_h)
                b2 = pygame.Rect(SCREEN_WIDTH // 2 - 90, btn_y, btn_w, btn_h)
                b3 = pygame.Rect(SCREEN_WIDTH // 2 + 110, btn_y, btn_w, btn_h)
                
                if b1.collidepoint(mx, my):
                    sound_manager.play("click")
                    self.on_menu()
                elif b2.collidepoint(mx, my):
                    sound_manager.play("horn")
                    self.on_retry()
                elif b3.collidepoint(mx, my):
                    sound_manager.play("horn")
                    self.on_next_level()
            else:
                # 2 Botones: Menú, Reintentar
                b1 = pygame.Rect(SCREEN_WIDTH // 2 - 200, btn_y, btn_w, btn_h)
                b2 = pygame.Rect(SCREEN_WIDTH // 2 + 20, btn_y, btn_w, btn_h)
                
                if b1.collidepoint(mx, my):
                    sound_manager.play("click")
                    self.on_menu()
                elif b2.collidepoint(mx, my):
                    sound_manager.play("horn")
                    self.on_retry()

    def update(self, dt):
        self.anim_time += dt

    def draw(self, surface):
        # Overlay oscuro
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 14, 215))
        surface.blit(overlay, (0, 0))

        # Panel Central
        pw, ph = 640, 440
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        p_rect = pygame.Rect(px, py, pw, ph)

        pygame.draw.rect(surface, (28, 24, 34), p_rect, border_radius=10)
        border_col = COLOR_GOLD if self.victory else COLOR_ROYAL_RED
        pygame.draw.rect(surface, border_col, p_rect, 2, border_radius=10)

        # Título
        bob = math.sin(self.anim_time * 3.0) * 3
        if self.victory:
            t_str = "👑  ¡VICTORIA REAL!  👑"
            t_col = COLOR_GOLD_LIGHT
        else:
            t_str = "💀  ¡EL REINO HA CAÍDO!  💀"
            t_col = COLOR_ROYAL_RED
            
        t_surf = self.font_title.render(t_str, True, t_col)
        surface.blit(t_surf, (px + pw // 2 - t_surf.get_width() // 2, py + 30 + int(bob)))

        # Estrellas de Victoria
        if self.victory:
            stars_str = "⭐" * self.stars + "☆" * (3 - self.stars)
            stars_surf = self.font_title.render(stars_str, True, COLOR_GOLD)
            surface.blit(stars_surf, (px + pw // 2 - stars_surf.get_width() // 2, py + 95))

        # Estadísticas
        stat_y = py + (160 if self.victory else 120)
        stats = [
            f"Nivel: {self.level_data['name']}",
            f"Vidas Restantes: {self.lives_left}/{self.max_lives}",
            f"Enemigos Derrotados: {self.enemies_killed}",
            f"Puntuación Final: {self.score} pts"
        ]

        for line in stats:
            s_surf = self.font_main.render(line, True, COLOR_WHITE)
            surface.blit(s_surf, (px + pw // 2 - s_surf.get_width() // 2, stat_y))
            stat_y += 34

        # Botones
        mx, my = pygame.mouse.get_pos()
        btn_w, btn_h = 180, 48
        btn_y = SCREEN_HEIGHT // 2 + 155

        if self.victory and self.level_data["id"] < 3:
            buttons = [
                (pygame.Rect(SCREEN_WIDTH // 2 - 290, btn_y, btn_w, btn_h), "🏰 Menú", (45, 40, 55)),
                (pygame.Rect(SCREEN_WIDTH // 2 - 90, btn_y, btn_w, btn_h), "🔄 Reintentar", (50, 70, 45)),
                (pygame.Rect(SCREEN_WIDTH // 2 + 110, btn_y, btn_w, btn_h), "⚔️ Siguiente", (65, 110, 50))
            ]
        else:
            buttons = [
                (pygame.Rect(SCREEN_WIDTH // 2 - 200, btn_y, btn_w, btn_h), "🏰 Menú", (45, 40, 55)),
                (pygame.Rect(SCREEN_WIDTH // 2 + 20, btn_y, btn_w, btn_h), "🔄 Reintentar", (50, 70, 45))
            ]

        for r, txt, base_bg in buttons:
            is_hover = r.collidepoint(mx, my)
            bg = (base_bg[0] + 20, base_bg[1] + 20, base_bg[2] + 20) if is_hover else base_bg
            pygame.draw.rect(surface, bg, r, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD if is_hover else COLOR_UI_BORDER, r, 1, border_radius=6)
            
            t = self.font_main.render(txt, True, COLOR_WHITE)
            surface.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))
