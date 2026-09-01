"""
Escena del Menú Principal, Selección de Niveles y Guía de Juego para 'Reino en Asedio'.
"""

import math
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_UI_BG, COLOR_UI_BORDER,
    COLOR_UI_PANEL, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_ROYAL_RED,
    COLOR_ROYAL_BLUE, COLOR_WHITE, COLOR_BLACK, COLOR_GRASS_BASE,
    COLOR_STONE_LIGHT, COLOR_STONE_MID, COLOR_STONE_DARK
)
from engine.audio import sound_manager
from maps.levels import LEVELS

class MenuScene:
    def __init__(self, on_start_level_callback, progress_data):
        self.on_start_level = on_start_level_callback
        self.progress_data = progress_data # {"level_1": {"stars": 3, "score": 1200}, ...}
        self.show_guide = False
        self.anim_time = 0.0

        self.font_title = pygame.font.SysFont("georgia", 44, bold=True)
        self.font_subtitle = pygame.font.SysFont("georgia", 22, italic=True)
        self.font_main = pygame.font.SysFont("georgia", 18, bold=True)
        self.font_small = pygame.font.SysFont("georgia", 14)
        
        sound_manager.start_music()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Si la guía está abierta, cerrar con click
            if self.show_guide:
                self.show_guide = False
                sound_manager.play("click")
                return

            # Botón de Sonido (Esquina superior derecha)
            if SCREEN_WIDTH - 60 <= mx <= SCREEN_WIDTH - 15 and 15 <= my <= 55:
                sound_manager.toggle_sound()
                sound_manager.play("click")
                return

            # Botón de Cómo Jugar (Abajo en el centro)
            guide_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 65, 200, 42)
            if guide_rect.collidepoint(mx, my):
                self.show_guide = True
                sound_manager.play("click")
                return

            # Selección de Niveles (3 Tarjetas)
            card_w, card_h = 320, 360
            spacing = 40
            start_x = (SCREEN_WIDTH - (card_w * 3 + spacing * 2)) // 2
            card_y = 190

            for i, level in enumerate(LEVELS):
                cx = start_x + i * (card_w + spacing)
                btn_rect = pygame.Rect(cx + 30, card_y + card_h - 60, card_w - 60, 44)
                if btn_rect.collidepoint(mx, my):
                    sound_manager.play("horn")
                    self.on_start_level(level)
                    return

    def update(self, dt):
        self.anim_time += dt

    def draw(self, surface):
        # 1. Fondo Medieval con degradado y diseño elegante
        surface.fill((16, 14, 22))
        
        # Rayos de luz / ambientación sutil
        for i in range(12):
            angle = self.anim_time * 0.1 + i * (math.pi / 6)
            lx = SCREEN_WIDTH // 2 + math.cos(angle) * 800
            ly = SCREEN_HEIGHT // 2 + math.sin(angle) * 800
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(s, (235, 185, 52, 10), (SCREEN_WIDTH // 2, 80), (lx, ly), 40)
            surface.blit(s, (0, 0))

        # 2. Título Principal y Corona
        bob = math.sin(self.anim_time * 2.5) * 4
        title_surf = self.font_title.render("⚔️  REINO EN ASEDIO  ⚔️", True, COLOR_GOLD_LIGHT)
        title_shadow = self.font_title.render("⚔️  REINO EN ASEDIO  ⚔️", True, (0, 0, 0))
        surface.blit(title_shadow, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2 + 2, 45 + int(bob) + 2))
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 45 + int(bob)))

        sub_surf = self.font_subtitle.render("Defensa Estratégica de Torres Medievales", True, COLOR_WHITE)
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 110))

        # 3. Botón de Sonido
        snd_bg = pygame.Rect(SCREEN_WIDTH - 60, 15, 45, 40)
        pygame.draw.rect(surface, COLOR_UI_PANEL, snd_bg, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, snd_bg, 1, border_radius=6)
        snd_icon = "🔊" if sound_manager.enabled else "🔇"
        snd_txt = self.font_main.render(snd_icon, True, COLOR_WHITE)
        surface.blit(snd_txt, (snd_bg.centerx - snd_txt.get_width() // 2, snd_bg.centery - snd_txt.get_height() // 2))

        # 4. Tarjetas de Nivel
        card_w, card_h = 320, 360
        spacing = 40
        start_x = (SCREEN_WIDTH - (card_w * 3 + spacing * 2)) // 2
        card_y = 175
        mx, my = pygame.mouse.get_pos()

        for i, level in enumerate(LEVELS):
            cx = start_x + i * (card_w + spacing)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)
            is_hover = card_rect.collidepoint(mx, my)

            # Fondo de la tarjeta
            bg_col = (35, 32, 44) if not is_hover else (45, 40, 58)
            pygame.draw.rect(surface, bg_col, card_rect, border_radius=8)
            border_col = COLOR_GOLD_LIGHT if is_hover else COLOR_UI_BORDER
            pygame.draw.rect(surface, border_col, card_rect, 2 if is_hover else 1, border_radius=8)

            # Encabezado del nivel
            num_surf = self.font_small.render(f"NIVEL {level['id']}", True, COLOR_GOLD)
            surface.blit(num_surf, (cx + 20, card_y + 16))

            diff_col = (90, 210, 110) if level['difficulty'] == "Fácil" else ((240, 190, 60) if level['difficulty'] == "Media" else COLOR_ROYAL_RED)
            diff_surf = self.font_small.render(level['difficulty'], True, diff_col)
            surface.blit(diff_surf, (cx + card_w - diff_surf.get_width() - 20, card_y + 16))

            name_surf = self.font_main.render(level['name'], True, COLOR_WHITE)
            surface.blit(name_surf, (cx + 20, card_y + 44))

            # Descripción
            desc_lines = [level['desc'][:32], level['desc'][32:64], level['desc'][64:]]
            for l_idx, line in enumerate(desc_lines):
                if line.strip():
                    l_surf = self.font_small.render(line.strip(), True, (180, 180, 190))
                    surface.blit(l_surf, (cx + 20, card_y + 85 + l_idx * 18))

            # Estrellas y Puntuación guardada
            lvl_key = f"level_{level['id']}"
            saved = self.progress_data.get(lvl_key, {"stars": 0, "score": 0})
            stars_str = "⭐" * saved["stars"] + "☆" * (3 - saved["stars"])
            stars_surf = self.font_main.render(stars_str, True, COLOR_GOLD)
            surface.blit(stars_surf, (cx + card_w // 2 - stars_surf.get_width() // 2, card_y + 180))

            score_txt = self.font_small.render(f"Récord: {saved['score']} pts", True, COLOR_STONE_LIGHT)
            surface.blit(score_txt, (cx + card_w // 2 - score_txt.get_width() // 2, card_y + 215))

            # Botón Jugar
            btn_rect = pygame.Rect(cx + 30, card_y + card_h - 60, card_w - 60, 44)
            btn_hover = btn_rect.collidepoint(mx, my)
            pygame.draw.rect(surface, (65, 120, 50) if btn_hover else (45, 90, 38), btn_rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, btn_rect, 1, border_radius=6)
            
            play_txt = self.font_main.render("⚔️  BATALLA", True, COLOR_WHITE)
            surface.blit(play_txt, (btn_rect.centerx - play_txt.get_width() // 2, btn_rect.centery - play_txt.get_height() // 2))

        # 5. Botón de Cómo Jugar
        guide_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 65, 200, 42)
        g_hover = guide_rect.collidepoint(mx, my)
        pygame.draw.rect(surface, COLOR_UI_PANEL if not g_hover else (55, 50, 70), guide_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, guide_rect, 1, border_radius=6)
        g_txt = self.font_main.render("📜  Cómo Jugar", True, COLOR_WHITE)
        surface.blit(g_txt, (guide_rect.centerx - g_txt.get_width() // 2, guide_rect.centery - g_txt.get_height() // 2))

        # 6. Modal de Guía / Cómo Jugar
        if self.show_guide:
            self._draw_guide_modal(surface)

    def _draw_guide_modal(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        mw, mh = 700, 480
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        m_rect = pygame.Rect(mx, my, mw, mh)

        pygame.draw.rect(surface, (28, 25, 36), m_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, m_rect, 2, border_radius=8)

        # Título
        t_surf = self.font_title.render("📜 Guía del Estratega Real", True, COLOR_GOLD_LIGHT)
        surface.blit(t_surf, (mx + mw // 2 - t_surf.get_width() // 2, my + 20))

        guide_items = [
            ("🏰 Torres", "Haz click en los pedestales de piedra para construir 4 tipos de torres:"),
            ("   • Arqueros", "Daño físico rápido a distancia con flechas."),
            ("   • Catapulta", "Daño explosivo masivo de área (no ataca voladores)."),
            ("   • Magos", "Dispara energía mágica que ignora la armadura física."),
            ("   • Cuartel", "Despliega soldados en el camino que bloquean y luchan cuerpo a cuerpo."),
            ("👑 Hechizos Activos", "Usa las teclas [Q] Flechas, [W] Refuerzos, [E] Meteoro."),
            ("⚡ Controles", "[1, 2, 3] Velocidad  |  [Espacio] Pausar  |  [Esc] Cancelar")
        ]

        cur_y = my + 75
        for header, desc in guide_items:
            h_surf = self.font_main.render(header, True, COLOR_GOLD_LIGHT if not header.startswith(" ") else COLOR_WHITE)
            d_surf = self.font_small.render(desc, True, (220, 220, 220))
            surface.blit(h_surf, (mx + 35, cur_y))
            surface.blit(d_surf, (mx + 220, cur_y + 3))
            cur_y += 38

        # Click para cerrar
        close_txt = self.font_small.render("(Haz click en cualquier lugar para cerrar)", True, COLOR_STONE_LIGHT)
        surface.blit(close_txt, (mx + mw // 2 - close_txt.get_width() // 2, my + mh - 35))
