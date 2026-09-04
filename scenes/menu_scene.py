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
from engine.graphics import gfx
from maps.levels import LEVELS

class MenuScene:
    def __init__(self, on_start_level_callback, progress_data):
        self.on_start_level = on_start_level_callback
        self.progress_data = progress_data # {"level_1": {"stars": 3, "score": 1200}, ...}
        self.show_guide = False
        self.anim_time = 0.0
        
        # Paginación de niveles
        self.current_page = 0
        self.levels_per_page = 3
        self.total_pages = math.ceil(len(LEVELS) / self.levels_per_page)

        self.font_title = pygame.font.SysFont("georgia", 44, bold=True)
        self.font_subtitle = pygame.font.SysFont("georgia", 22, italic=True)
        self.font_main = pygame.font.SysFont("georgia", 18, bold=True)
        self.font_small = pygame.font.SysFont("georgia", 14)
        self.font_mini = pygame.font.SysFont("georgia", 12)
        
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
            guide_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 55, 200, 38)
            if guide_rect.collidepoint(mx, my):
                self.show_guide = True
                sound_manager.play("click")
                return

            # Flechas de paginación
            card_y = 175
            card_h = 360
            arrow_y = card_y + card_h // 2 - 25
            prev_rect = pygame.Rect(35, arrow_y, 45, 50)
            next_rect = pygame.Rect(SCREEN_WIDTH - 80, arrow_y, 45, 50)

            if self.current_page > 0 and prev_rect.collidepoint(mx, my):
                self.current_page -= 1
                sound_manager.play("click")
                return

            if self.current_page < self.total_pages - 1 and next_rect.collidepoint(mx, my):
                self.current_page += 1
                sound_manager.play("click")
                return

            # Selección de Niveles (Tarjetas de la página actual)
            card_w = 320
            spacing = 40
            start_idx = self.current_page * self.levels_per_page
            end_idx = min(start_idx + self.levels_per_page, len(LEVELS))
            page_levels = LEVELS[start_idx:end_idx]
            num_cards = len(page_levels)
            start_x = (SCREEN_WIDTH - (card_w * num_cards + spacing * (num_cards - 1))) // 2

            for i, level in enumerate(page_levels):
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

        # 2. Título Principal y Espadas Medievales
        bob = math.sin(self.anim_time * 2.5) * 4
        title_text = "REINO EN ASEDIO"
        title_surf = self.font_title.render(title_text, True, COLOR_GOLD_LIGHT)
        title_shadow = self.font_title.render(title_text, True, (0, 0, 0))
        tx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        ty = 38 + int(bob)
        surface.blit(title_shadow, (tx + 2, ty + 2))
        surface.blit(title_surf, (tx, ty))

        # Espadas cruzadas a ambos lados del título
        gfx.draw_swords(surface, tx - 36, ty + 24, 15, COLOR_GOLD_LIGHT)
        gfx.draw_swords(surface, tx + title_surf.get_width() + 36, ty + 24, 15, COLOR_GOLD_LIGHT)

        sub_surf = self.font_subtitle.render("Defensa Estratégica de Torres Medievales", True, COLOR_WHITE)
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 98))

        # 3. Botón de Sonido
        snd_bg = pygame.Rect(SCREEN_WIDTH - 60, 15, 45, 40)
        pygame.draw.rect(surface, COLOR_UI_PANEL, snd_bg, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, snd_bg, 1, border_radius=6)
        gfx.draw_speaker(surface, snd_bg.centerx, snd_bg.centery, sound_manager.enabled)

        # 4. Tarjetas de Nivel Paginadas
        card_w, card_h = 320, 360
        spacing = 40
        card_y = 155
        mx, my = pygame.mouse.get_pos()

        start_idx = self.current_page * self.levels_per_page
        end_idx = min(start_idx + self.levels_per_page, len(LEVELS))
        page_levels = LEVELS[start_idx:end_idx]
        num_cards = len(page_levels)
        start_x = (SCREEN_WIDTH - (card_w * num_cards + spacing * (num_cards - 1))) // 2

        for i, level in enumerate(page_levels):
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

            diff = level['difficulty']
            if diff == "Fácil":
                diff_col = (90, 210, 110)
            elif diff == "Media":
                diff_col = (240, 190, 60)
            elif diff == "Avanzada":
                diff_col = (230, 130, 40)
            else:
                diff_col = COLOR_ROYAL_RED
            diff_surf = self.font_small.render(diff, True, diff_col)
            surface.blit(diff_surf, (cx + card_w - diff_surf.get_width() - 20, card_y + 16))

            name_surf = self.font_main.render(level['name'], True, COLOR_WHITE)
            surface.blit(name_surf, (cx + 20, card_y + 44))

            # Descripción
            desc_lines = [level['desc'][:32], level['desc'][32:64], level['desc'][64:]]
            for l_idx, line in enumerate(desc_lines):
                if line.strip():
                    l_surf = self.font_small.render(line.strip(), True, (180, 180, 190))
                    surface.blit(l_surf, (cx + 20, card_y + 85 + l_idx * 18))

            # Caminos y oleadas informativas (sin emojis que generen cajas tofu)
            paths_count = len(level['paths'])
            waves_count = len(level['waves'])
            info_txt = f"{waves_count} Oleadas   •   {paths_count} {'Caminos' if paths_count > 1 else 'Camino'}"
            info_surf = self.font_small.render(info_txt, True, (205, 205, 215))
            surface.blit(info_surf, (cx + card_w // 2 - info_surf.get_width() // 2, card_y + 152))

            # Estrellas doradas vectoriales procedurales
            lvl_key = f"level_{level['id']}"
            saved = self.progress_data.get(lvl_key, {"stars": 0, "score": 0})
            num_stars = saved.get("stars", 0)
            star_y = card_y + 192
            for s_idx in range(3):
                sx = cx + card_w // 2 - 28 + s_idx * 28
                gfx.draw_star(surface, sx, star_y, radius=11, filled=(s_idx < num_stars))

            score_txt = self.font_small.render(f"Récord: {saved['score']} pts", True, COLOR_STONE_LIGHT)
            surface.blit(score_txt, (cx + card_w // 2 - score_txt.get_width() // 2, card_y + 215))

            # Botón Jugar
            btn_rect = pygame.Rect(cx + 30, card_y + card_h - 60, card_w - 60, 44)
            btn_hover = btn_rect.collidepoint(mx, my)
            pygame.draw.rect(surface, (65, 120, 50) if btn_hover else (45, 90, 38), btn_rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, btn_rect, 1, border_radius=6)
            
            play_txt = self.font_main.render("BATALLA", True, COLOR_WHITE)
            surface.blit(play_txt, (btn_rect.centerx - play_txt.get_width() // 2, btn_rect.centery - play_txt.get_height() // 2))

        # 5. Flechas de navegación de páginas (si hay más de 1 página)
        if self.total_pages > 1:
            arrow_y = card_y + card_h // 2 - 25
            prev_rect = pygame.Rect(35, arrow_y, 45, 50)
            next_rect = pygame.Rect(SCREEN_WIDTH - 80, arrow_y, 45, 50)

            # Flecha Izquierda
            if self.current_page > 0:
                p_hover = prev_rect.collidepoint(mx, my)
                pygame.draw.rect(surface, (55, 50, 70) if p_hover else COLOR_UI_PANEL, prev_rect, border_radius=6)
                pygame.draw.rect(surface, COLOR_GOLD, prev_rect, 1, border_radius=6)
                gfx.draw_arrow(surface, prev_rect.centerx, prev_rect.centery, "left", COLOR_GOLD_LIGHT, 11)

            # Flecha Derecha
            if self.current_page < self.total_pages - 1:
                n_hover = next_rect.collidepoint(mx, my)
                pygame.draw.rect(surface, (55, 50, 70) if n_hover else COLOR_UI_PANEL, next_rect, border_radius=6)
                pygame.draw.rect(surface, COLOR_GOLD, next_rect, 1, border_radius=6)
                gfx.draw_arrow(surface, next_rect.centerx, next_rect.centery, "right", COLOR_GOLD_LIGHT, 11)

            # Indicador de Página
            page_str = f"Página {self.current_page + 1} de {self.total_pages}"
            page_surf = self.font_small.render(page_str, True, COLOR_STONE_LIGHT)
            surface.blit(page_surf, (SCREEN_WIDTH // 2 - page_surf.get_width() // 2, card_y + card_h + 16))

        # 6. Botón de Cómo Jugar
        guide_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT - 55, 220, 38)
        g_hover = guide_rect.collidepoint(mx, my)
        pygame.draw.rect(surface, COLOR_UI_PANEL if not g_hover else (55, 50, 70), guide_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, guide_rect, 1, border_radius=6)
        g_txt = self.font_main.render("CÓDEX DE JUEGO", True, COLOR_WHITE)
        surface.blit(g_txt, (guide_rect.centerx - g_txt.get_width() // 2, guide_rect.centery - g_txt.get_height() // 2))

        # 6. Modal de Guía / Cómo Jugar
        if self.show_guide:
            self._draw_guide_modal(surface)

    def _draw_guide_modal(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        surface.blit(overlay, (0, 0))

        mw, mh = 1120, 610
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        m_rect = pygame.Rect(mx, my, mw, mh)

        # Marco del Códex Real
        pygame.draw.rect(surface, (24, 21, 31), m_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_GOLD, m_rect, 2, border_radius=10)
        pygame.draw.rect(surface, (45, 38, 55), (mx + 6, my + 6, mw - 12, mh - 12), 1, border_radius=8)

        # Título y Subtítulo
        t_surf = self.font_title.render("CÓDEX Y GUÍA DEL ESTRATEGA REAL", True, COLOR_GOLD_LIGHT)
        surface.blit(t_surf, (mx + mw // 2 - t_surf.get_width() // 2, my + 14))

        sub_surf = self.font_subtitle.render("Estructuras Defensivas, Especializaciones Tier 4, Hechizos y Controles", True, (210, 205, 220))
        surface.blit(sub_surf, (mx + mw // 2 - sub_surf.get_width() // 2, my + 54))

        # Línea divisoria decorativa
        pygame.draw.line(surface, COLOR_UI_BORDER, (mx + 25, my + 82), (mx + mw - 25, my + 82), 1)

        # =================== COLUMNA 1: 6 TORRES Y 12 ESPECIALIZACIONES ===================
        col1_x = mx + 25
        col1_w = 600
        cur_y = my + 92

        sec1_title = self.font_main.render("ESTRUCTURAS DEFENSIVAS Y ESPECIALIZACIONES (NV. 4)", True, COLOR_GOLD_LIGHT)
        surface.blit(sec1_title, (col1_x, cur_y))
        cur_y += 24

        towers_guide = [
            ("1. Arqueros (70 Oro)", "Físico rápido a distancia.",
             "[A] Ballesta Pesada: Flechas críticas (+150% daño)",
             "[B] Tiradores Élficos: Cadencia extrema con veneno continuo"),
            ("2. Catapulta (110 Oro)", "Daño masivo de área (AOE).",
             "[A] Fuego Valyrio: Deja lava ardiente que quema en el suelo",
             "[B] Morteros Pesados: Bombas con onda de aturdimiento"),
            ("3. Magos (90 Oro)", "Magia arcana que ignora armadura.",
             "[A] Torre de Hielo: Ralentiza a los enemigos en un 50%",
             "[B] Rayos en Cadena: Descargas que rebotan en 4 objetivos"),
            ("4. Cuartel (80 Oro)", "Despliega soldados en el camino.",
             "[A] Paladines Sagrados: Gran armadura y auto-regeneración",
             "[B] Caballeros Bárbaros: Doble hacha y gran daño corporal"),
            ("5. Alquimia (100 Oro)", "Ácido corrosivo y charcos de brea.",
             "[A] Laboratorio de Plagas: Nubes venenosas persistentes",
             "[B] Lanza-Ácido: Reduce el 80% de la armadura enemiga"),
            ("6. Santuario Solar (120 Oro)", "Rayo celestial continuo.",
             "[A] Juicio Divino: Rayo hiperconcentrado antitanques y jefes",
             "[B] Aura de Bendición: +30% daño/rango a torres aliadas")
        ]

        for t_name, t_role, branch_a, branch_b in towers_guide:
            # Caja de cada torre
            t_box = pygame.Rect(col1_x, cur_y, col1_w, 68)
            pygame.draw.rect(surface, (33, 29, 43), t_box, border_radius=6)
            pygame.draw.rect(surface, (55, 48, 70), t_box, 1, border_radius=6)

            h_s = self.font_main.render(t_name, True, COLOR_GOLD)
            r_s = self.font_mini.render(t_role, True, (190, 190, 205))
            surface.blit(h_s, (col1_x + 8, cur_y + 4))
            surface.blit(r_s, (col1_x + h_s.get_width() + 16, cur_y + 6))

            a_s = self.font_mini.render(f"• {branch_a}", True, (100, 215, 255))
            b_s = self.font_mini.render(f"• {branch_b}", True, (255, 150, 120))
            surface.blit(a_s, (col1_x + 12, cur_y + 26))
            surface.blit(b_s, (col1_x + 12, cur_y + 45))

            cur_y += 73

        # =================== COLUMNA 2: HECHIZOS, CONTROLES Y TÁCTICA ===================
        col2_x = mx + 645
        col2_w = mw - 670
        cur_y2 = my + 92

        # 1. Hechizos
        sec2_title = self.font_main.render("HECHIZOS REALES (TECLAS RÁPIDAS)", True, COLOR_GOLD_LIGHT)
        surface.blit(sec2_title, (col2_x, cur_y2))
        cur_y2 += 24

        spells_guide = [
            ("[Q] Lluvia de Flechas", "Lanza una descarga letal sobre el área elegida."),
            ("[W] Guardia Real", "Convoca 2 soldados leales en cualquier punto del camino."),
            ("[E] Meteoro Ígneo", "Impacto destructor masivo que arrasa a grupos densos.")
        ]
        for s_key, s_desc in spells_guide:
            s_box = pygame.Rect(col2_x, cur_y2, col2_w, 36)
            pygame.draw.rect(surface, (33, 29, 43), s_box, border_radius=4)
            pygame.draw.rect(surface, (55, 48, 70), s_box, 1, border_radius=4)
            k_s = self.font_small.render(s_key, True, COLOR_GOLD)
            d_s = self.font_mini.render(s_desc, True, (210, 210, 210))
            surface.blit(k_s, (col2_x + 8, cur_y2 + 4))
            surface.blit(d_s, (col2_x + 8, cur_y2 + 20))
            cur_y2 += 40

        cur_y2 += 6

        # 2. Controles y Pantalla
        sec3_title = self.font_main.render("CONTROLES Y PANTALLA", True, COLOR_GOLD_LIGHT)
        surface.blit(sec3_title, (col2_x, cur_y2))
        cur_y2 += 24

        ctrls = [
            ("[F11] Pantalla Completa", "Alterna pantalla completa o redimensiona la ventana."),
            ("[1, 2, 4] Velocidad", "Cambia el ritmo de la batalla (1x normal, 2x rápido, 4x veloz)."),
            ("[Espacio] / [P] Pausa", "Pausa el combate para planear tus defensas."),
            ("[Esc] Cancelar", "Cancela el hechizo activo o deselecciona la torre.")
        ]
        for c_key, c_desc in ctrls:
            c_box = pygame.Rect(col2_x, cur_y2, col2_w, 32)
            pygame.draw.rect(surface, (30, 27, 40), c_box, border_radius=4)
            pygame.draw.rect(surface, (50, 45, 65), c_box, 1, border_radius=4)
            k_s = self.font_mini.render(c_key, True, COLOR_WHITE)
            d_s = self.font_mini.render(c_desc, True, (180, 180, 195))
            surface.blit(k_s, (col2_x + 8, cur_y2 + 3))
            surface.blit(d_s, (col2_x + 8, cur_y2 + 16))
            cur_y2 += 36

        cur_y2 += 6

        # 3. Consejos tácticos
        sec4_title = self.font_main.render("CONSEJOS TÁCTICOS", True, COLOR_GOLD_LIGHT)
        surface.blit(sec4_title, (col2_x, cur_y2))
        cur_y2 += 22

        tips = [
            "• Al subir una torre a Nv.3, pasa el ratón sobre [A] o [B] para ver estadísticas completas.",
            "• Usa Cuarteles para retener enemigos dentro del fuego de Catapultas y Alquimia.",
            "• El Santuario Solar es la mejor respuesta contra jefes y monstruos acorazados."
        ]
        for tip in tips:
            tip_s = self.font_mini.render(tip, True, (215, 210, 180))
            surface.blit(tip_s, (col2_x + 4, cur_y2))
            cur_y2 += 18

        # Click para cerrar
        close_txt = self.font_small.render("(Haz click en cualquier lugar para cerrar este códex)", True, COLOR_STONE_LIGHT)
        surface.blit(close_txt, (mx + mw // 2 - close_txt.get_width() // 2, my + mh - 24))
