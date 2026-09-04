"""
Escena Principal de Juego y Sistema HUD para 'Reino en Asedio'.
"""

import math
import random
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_UI_BG, COLOR_UI_BORDER,
    COLOR_UI_PANEL, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_ROYAL_RED,
    COLOR_ROYAL_BLUE, COLOR_WHITE, COLOR_BLACK, COLOR_HEALTH_GREEN,
    TOWER_DATA, SPELL_DATA, COLOR_FIRE_ORANGE, COLOR_ARCANE_PURPLE,
    COLOR_ICE_CYAN, COLOR_STONE_LIGHT, COLOR_STONE_MID, COLOR_STONE_DARK,
    COLOR_WOOD_MID, COLOR_WOOD_DARK
)
from engine.audio import sound_manager
from engine.graphics import gfx
from engine.particles import ParticleSystem
from entities.enemies import Enemy
from entities.towers import Tower, Arrow
from entities.spells import SpellManager
from maps.levels import MapRenderer

class GameScene:
    def __init__(self, level_data, on_game_over_callback):
        self.level_data = level_data
        self.on_game_over = on_game_over_callback
        
        self.map_renderer = MapRenderer(level_data)
        self.particles = ParticleSystem()
        self.spells = SpellManager()
        
        # Estado del juego
        self.lives = level_data.get("starting_lives", 20)
        self.max_lives = self.lives
        self.gold = level_data.get("starting_gold", 260)
        self.score = 0
        self.game_speed = 1.0
        self.is_paused = False
        
        # Oleadas
        self.waves = level_data["waves"]
        self.current_wave_idx = 0
        self.wave_active = False
        self.wave_spawn_queue = []
        self.wave_spawn_timer = 0.0
        self.wave_countdown = 6.0 # Tiempo para la siguiente oleada
        self.total_enemies_killed = 0
        self.total_damage_dealt = 0
        
        # Entidades
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.free_soldiers = [] # Refuerzos por hechizo
        
        # Interacción y UI
        self.selected_spot = None
        self.selected_tower = None
        self.placing_rally_tower = None
        self.casting_spell = None
        self.hovered_btn = None
        
        # Fuentes tipográficas
        self.font_title = pygame.font.SysFont("georgia", 24, bold=True)
        self.font_main = pygame.font.SysFont("georgia", 18, bold=True)
        self.font_small = pygame.font.SysFont("georgia", 13, bold=True)
        self.particles.set_font(self.font_small)
        
        # Iniciar música ambiental
        sound_manager.start_music()

    def start_next_wave(self, early_bonus=True):
        if self.current_wave_idx >= len(self.waves):
            return

        if self.wave_countdown > 0 and early_bonus:
            bonus = int(self.wave_countdown * 5)
            self.gold += bonus
            self.particles.add_floating_gold(SCREEN_WIDTH // 2, 60, bonus)

        self.wave_active = True
        self.wave_countdown = 0.0
        sound_manager.play("horn")
        
        wave_data = self.waves[self.current_wave_idx]
        self.wave_spawn_queue = []
        
        paths = self.level_data["paths"]
        for group in wave_data:
            enemy_type = group["type"]
            count = group["count"]
            delay = group["delay"]
            for i in range(count):
                path = random.choice(paths)
                self.wave_spawn_queue.append({
                    "type": enemy_type,
                    "path": path,
                    "delay": delay
                })

        self.current_wave_idx += 1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.is_paused = not self.is_paused
            elif event.key == pygame.K_1:
                self.game_speed = 1.0
                self.is_paused = False
            elif event.key == pygame.K_2:
                self.game_speed = 2.0
                self.is_paused = False
            elif event.key == pygame.K_3:
                self.game_speed = 4.0
                self.is_paused = False
            elif event.key == pygame.K_q:
                self._select_spell("rain_of_arrows")
            elif event.key == pygame.K_w:
                self._select_spell("reinforcements")
            elif event.key == pygame.K_e:
                self._select_spell("meteor")
            elif event.key == pygame.K_ESCAPE:
                self.selected_tower = None
                self.selected_spot = None
                self.casting_spell = None
                self.placing_rally_tower = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Click izquierdo
                self._handle_left_click(event.pos)
            elif event.button == 3: # Click derecho cancela
                self.selected_tower = None
                self.selected_spot = None
                self.casting_spell = None
                self.placing_rally_tower = None

    def _select_spell(self, spell_key):
        if self.spells.is_ready(spell_key):
            self.casting_spell = spell_key
            self.selected_tower = None
            self.selected_spot = None
            sound_manager.play("click")

    def _handle_left_click(self, pos):
        mx, my = pos

        # 1. Click en la barra superior (Controles de velocidad, pausa, sonido, llamar oleada)
        if my <= 45:
            # Botón siguiente oleada
            if 480 <= mx <= 630 and not self.wave_active and self.current_wave_idx < len(self.waves):
                self.start_next_wave(early_bonus=True)
                return
            # Velocidades
            if 1070 <= mx <= 1110:
                self.game_speed = 1.0
                self.is_paused = False
                return
            if 1115 <= mx <= 1155:
                self.game_speed = 2.0
                self.is_paused = False
                return
            if 1160 <= mx <= 1200:
                self.game_speed = 4.0
                self.is_paused = False
                return
            if 1205 <= mx <= 1260:
                self.is_paused = not self.is_paused
                return

        # 2. Click en hechizos (Panel inferior izquierdo)
        if my >= SCREEN_HEIGHT - 80 and mx <= 270:
            spell_keys = ["rain_of_arrows", "reinforcements", "meteor"]
            for i, k in enumerate(spell_keys):
                bx = 20 + i * 80
                by = SCREEN_HEIGHT - 75
                if bx <= mx <= bx + 70 and by <= my <= by + 65:
                    self._select_spell(k)
                    return

        # 3. Si estamos colocando un hechizo activo
        if self.casting_spell:
            if self.spells.cast(self.casting_spell, mx, my, self.free_soldiers, self.particles):
                self.casting_spell = None
                return

        # 4. Si estamos colocando el punto de reunión de un cuartel
        if self.placing_rally_tower:
            dist = math.hypot(mx - self.placing_rally_tower.x, my - self.placing_rally_tower.y)
            if dist <= self.placing_rally_tower.range:
                self.placing_rally_tower.set_rally_point(mx, my)
                sound_manager.play("build")
                self.placing_rally_tower = None
                return

        # 5. Si hay un menú de construcción abierto para un pedestal
        if self.selected_spot:
            sx, sy = self.selected_spot
            # Menú de selección de 6 torres alrededor del pedestal
            tower_types = ["archer", "catapult", "mage", "barracks", "alchemist", "sun_shrine"]
            angles = [i * (2 * math.pi / 6) - math.pi / 2 for i in range(6)]
            radius = 62
            for i, ttype in enumerate(tower_types):
                bx = sx + math.cos(angles[i]) * radius
                by = sy + math.sin(angles[i]) * radius
                if math.hypot(mx - bx, my - by) <= 24:
                    cost = TOWER_DATA[ttype]["cost"]
                    if self.gold >= cost:
                        self.gold -= cost
                        new_t = Tower(ttype, sx, sy)
                        self.towers.append(new_t)
                        sound_manager.play("build")
                        self.particles.add_magic_burst(sx, sy, COLOR_GOLD, count=10)
                        self.selected_spot = None
                        return

        # 6. Si hay una torre seleccionada (Panel de mejoras / venta / modo objetivo)
        if self.selected_tower:
            tx, ty = self.selected_tower.x, self.selected_tower.y
            
            # Botón de Mejora de Nivel (Arriba de la torre)
            if self.selected_tower.level < 3:
                cost = TOWER_DATA[self.selected_tower.tower_type]["upgrade_cost" if self.selected_tower.level == 1 else "l3_upgrade_cost"]
                if math.hypot(mx - tx, my - (ty - 55)) <= 22:
                    if self.gold >= cost:
                        self.gold -= self.selected_tower.upgrade_level(self.gold)
                        self.particles.add_magic_burst(tx, ty, COLOR_GOLD_LIGHT, count=12)
                        return
            elif self.selected_tower.level == 3 and self.selected_tower.specialization is None:
                # Botón Especial A
                if math.hypot(mx - (tx - 40), my - (ty - 55)) <= 24:
                    cost = TOWER_DATA[self.selected_tower.tower_type]["special_a"]["cost"]
                    if self.gold >= cost:
                        self.gold -= self.selected_tower.upgrade_special("special_a", self.gold)
                        self.particles.add_magic_burst(tx, ty, COLOR_ROYAL_BLUE, count=15)
                        return
                # Botón Especial B
                if math.hypot(mx - (tx + 40), my - (ty - 55)) <= 24:
                    cost = TOWER_DATA[self.selected_tower.tower_type]["special_b"]["cost"]
                    if self.gold >= cost:
                        self.gold -= self.selected_tower.upgrade_special("special_b", self.gold)
                        self.particles.add_magic_burst(tx, ty, COLOR_ROYAL_RED, count=15)
                        return

            # Botón de Venta (Abajo a la derecha)
            if math.hypot(mx - (tx + 45), my - (ty + 35)) <= 18:
                val = self.selected_tower.sell_value()
                self.gold += val
                sound_manager.play("coin")
                self.particles.add_floating_gold(tx, ty, val)
                self.towers.remove(self.selected_tower)
                self.selected_tower = None
                return

            # Botón de Rally Point si es barracón (Abajo a la izquierda)
            if self.selected_tower.tower_type == "barracks":
                if math.hypot(mx - (tx - 45), my - (ty + 35)) <= 18:
                    self.placing_rally_tower = self.selected_tower
                    sound_manager.play("click")
                    return

            # Selector de prioridad de objetivo
            if self.selected_tower.tower_type != "barracks":
                if math.hypot(mx - (tx - 45), my - (ty + 35)) <= 18:
                    modes = ["first", "last", "strongest", "weakest", "closest"]
                    idx = (modes.index(self.selected_tower.targeting_mode) + 1) % len(modes)
                    self.selected_tower.targeting_mode = modes[idx]
                    sound_manager.play("click")
                    return

        # 7. Selección de Torres en el mapa
        for t in self.towers:
            if math.hypot(mx - t.x, my - t.y) <= 30:
                for ot in self.towers:
                    ot.selected = False
                t.selected = True
                self.selected_tower = t
                self.selected_spot = None
                sound_manager.play("click")
                return

        # 8. Selección de Emplazamientos de construcción vacíos
        for spot in self.level_data["building_spots"]:
            if math.hypot(mx - spot[0], my - spot[1]) <= 28:
                # Comprobar que no haya una torre ya construida aquí
                has_tower = any(math.hypot(t.x - spot[0], t.y - spot[1]) < 10 for t in self.towers)
                if not has_tower:
                    self.selected_spot = spot
                    if self.selected_tower:
                        self.selected_tower.selected = False
                        self.selected_tower = None
                    sound_manager.play("click")
                    return

        # Deseleccionar al hacer click en el fondo
        if self.selected_tower:
            self.selected_tower.selected = False
            self.selected_tower = None
        self.selected_spot = None

    def update(self, raw_dt):
        if self.is_paused:
            return

        dt = raw_dt * self.game_speed

        # 1. Gestión de Oleadas y Spawn
        if not self.wave_active and self.current_wave_idx < len(self.waves):
            self.wave_countdown -= dt
            if self.wave_countdown <= 0:
                self.start_next_wave(early_bonus=False)

        if self.wave_active and self.wave_spawn_queue:
            self.wave_spawn_timer -= dt
            if self.wave_spawn_timer <= 0:
                item = self.wave_spawn_queue.pop(0)
                self.wave_spawn_timer = item["delay"]
                enemy = Enemy(item["type"], item["path"])
                self.enemies.append(enemy)

        if self.wave_active and not self.wave_spawn_queue and len(self.enemies) == 0:
            # Oleada terminada
            self.wave_active = False
            self.wave_countdown = 8.0 # Tiempo de descanso
            # Recompensa de fin de oleada
            wave_bonus = 25 + self.current_wave_idx * 5
            self.gold += wave_bonus
            self.particles.add_floating_gold(SCREEN_WIDTH // 2, 80, wave_bonus)

            # Si se completaron todas las oleadas -> Victoria
            if self.current_wave_idx >= len(self.waves):
                sound_manager.play("victory")
                self.on_game_over(True, self.lives, self.max_lives, self.score, self.total_enemies_killed)
                return

        # 2. Actualizar Enemigos
        spawned_enemies = []
        for e in self.enemies:
            e.update(dt, self.particles, spawned_enemies)
            if not e.alive:
                if e.reached_end:
                    self.lives -= e.damage_to_base
                    sound_manager.play("defeat")
                    self.particles.add_hit_spark(e.x, e.y, COLOR_ROYAL_RED, count=12)
                    if self.lives <= 0:
                        self.lives = 0
                        sound_manager.play("defeat")
                        self.on_game_over(False, 0, self.max_lives, self.score, self.total_enemies_killed)
                        return
                else:
                    # Enemigo derrotado
                    self.gold += e.gold_reward
                    self.score += e.gold_reward * 10
                    self.total_enemies_killed += 1
                    sound_manager.play("coin")
                    self.particles.add_floating_gold(e.x, e.y, e.gold_reward)
                    self.particles.add_blood_splatter(e.x, e.y, count=6)

        self.enemies.extend(spawned_enemies)
        self.enemies = [e for e in self.enemies if e.alive and not e.reached_end]

        # 3. Actualizar Torres
        for t in self.towers:
            t.update(dt, self.enemies, self.projectiles, self.particles)

        # 4. Actualizar Soldados Libres (Refuerzos)
        for s in self.free_soldiers:
            s.update(dt, self.enemies, self.particles)
        self.free_soldiers = [s for s in self.free_soldiers if s.alive]

        # 5. Actualizar Proyectiles
        for p in self.projectiles:
            if isinstance(p, Arrow):
                p.update(dt, self.particles)
            else:
                p.update(dt, self.enemies, self.particles)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # 6. Actualizar Hechizos y Partículas
        self.spells.update(dt, self.enemies, self.particles)
        self.particles.update(dt, self.enemies)

    def draw(self, surface):
        # 1. Fondo del mapa
        self.map_renderer.draw(surface)

        # 2. Efectos en el suelo (Lava, charcos de fuego)
        self.particles.draw_ground(surface)

        # 3. Emplazamientos interactivos
        mx, my = pygame.mouse.get_pos()
        for spot in self.level_data["building_spots"]:
            if math.hypot(mx - spot[0], my - spot[1]) <= 28:
                pygame.draw.circle(surface, COLOR_GOLD_LIGHT, spot, 26, 2)

        # 4. Soldados y Refuerzos
        for s in self.free_soldiers:
            s.draw(surface)

        # 5. Enemigos
        for e in self.enemies:
            e.draw(surface)

        # 6. Torres
        for t in self.towers:
            t.draw(surface)

        # 7. Proyectiles
        for p in self.projectiles:
            p.draw(surface)

        # 8. Hechizos y Partículas superiores
        self.spells.draw(surface)
        self.particles.draw_top(surface)

        # 9. Retícula de casteo de hechizo
        if self.casting_spell:
            radius = SPELL_DATA[self.casting_spell].get("radius", 60)
            s = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 60, 60, 70), (radius + 2, radius + 2), radius)
            pygame.draw.circle(s, (255, 200, 50, 220), (radius + 2, radius + 2), radius, 2)
            surface.blit(s, (mx - radius - 2, my - radius - 2))

        # 10. Modales de Interfaz (Construcción y Mejoras)
        self._draw_building_wheel(surface)
        self._draw_tower_inspector(surface)

        # 11. HUD Superior e Inferior
        self._draw_hud(surface)

    def _draw_building_wheel(self, surface):
        if not self.selected_spot:
            return
        sx, sy = self.selected_spot
        tower_types = ["archer", "catapult", "mage", "barracks", "alchemist", "sun_shrine"]
        angles = [i * (2 * math.pi / 6) - math.pi / 2 for i in range(6)]
        radius = 62
        mx, my = pygame.mouse.get_pos()
        hovered_info = None

        for i, ttype in enumerate(tower_types):
            bx = sx + math.cos(angles[i]) * radius
            by = sy + math.sin(angles[i]) * radius
            data = TOWER_DATA[ttype]
            cost = data["cost"]
            can_afford = self.gold >= cost
            is_hover = math.hypot(mx - bx, my - by) <= 24

            # Botón circular
            bg_col = (55, 50, 70) if is_hover else (32, 28, 42)
            border_col = COLOR_GOLD_LIGHT if (can_afford and is_hover) else (COLOR_GOLD if can_afford else (110, 105, 120))
            pygame.draw.circle(surface, bg_col, (int(bx), int(by)), 24)
            pygame.draw.circle(surface, border_col, (int(bx), int(by)), 24, 2)

            # Mini icono según tipo de torre
            if ttype == "archer":
                pygame.draw.line(surface, COLOR_WOOD_MID, (bx - 9, by + 7), (bx + 9, by - 7), 3)
                pygame.draw.circle(surface, (120, 220, 100), (int(bx + 6), int(by - 6)), 3)
            elif ttype == "catapult":
                pygame.draw.circle(surface, COLOR_FIRE_ORANGE, (int(bx), int(by)), 8)
                pygame.draw.line(surface, COLOR_WOOD_DARK, (bx - 6, by + 6), (bx + 6, by - 2), 2)
            elif ttype == "mage":
                pygame.draw.circle(surface, COLOR_ARCANE_PURPLE, (int(bx), int(by)), 8)
                pygame.draw.circle(surface, (230, 200, 255), (int(bx), int(by)), 4)
            elif ttype == "barracks":
                pygame.draw.rect(surface, COLOR_ROYAL_BLUE, (bx - 8, by - 8, 16, 16), border_radius=3)
                pygame.draw.circle(surface, COLOR_GOLD, (int(bx), int(by)), 3)
            elif ttype == "alchemist":
                pygame.draw.circle(surface, (40, 220, 90), (int(bx), int(by + 2)), 8)
                pygame.draw.rect(surface, (180, 240, 200), (bx - 3, by - 8, 6, 7), border_radius=1)
            elif ttype == "sun_shrine":
                pygame.draw.circle(surface, COLOR_GOLD_LIGHT, (int(bx), int(by)), 7)
                for a in range(8):
                    ang = a * (math.pi / 4)
                    px = bx + math.cos(ang) * 11
                    py = by + math.sin(ang) * 11
                    pygame.draw.line(surface, (255, 230, 120), (bx, by), (px, py), 1)

            # Etiqueta de precio debajo
            cost_surf = self.font_small.render(f"{cost}g", True, COLOR_GOLD if can_afford else (220, 80, 80))
            surface.blit(cost_surf, (bx - cost_surf.get_width() // 2, by + 26))

            if is_hover:
                hovered_info = (data, cost, can_afford)

        # Si hay hover en alguna torre del selector, dibujar tarjeta flotante
        if hovered_info:
            data, cost, can_afford = hovered_info
            tip_title = f"{data['name']} ({cost}g)"
            tip_desc = data['description']
            title_s = self.font_main.render(tip_title, True, COLOR_GOLD_LIGHT if can_afford else (230, 100, 100))
            desc_s = self.font_small.render(tip_desc, True, (220, 220, 230))
            w = max(title_s.get_width(), desc_s.get_width()) + 24
            h = 56
            rx = min(max(10, mx - w // 2), SCREEN_WIDTH - w - 10)
            ry = max(10, my - 70)
            pygame.draw.rect(surface, (26, 23, 34), (rx, ry, w, h), border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, (rx, ry, w, h), 1, border_radius=6)
            surface.blit(title_s, (rx + 12, ry + 6))
            surface.blit(desc_s, (rx + 12, ry + 30))

    def _draw_tower_inspector(self, surface):
        if not self.selected_tower:
            return
        t = self.selected_tower
        tx, ty = t.x, t.y
        data = TOWER_DATA[t.tower_type]
        mx, my = pygame.mouse.get_pos()

        # Si ya tiene especialización activa, mostrar insignia en lo alto
        if t.specialization:
            spec_info = data.get(t.specialization, {})
            spec_name = spec_info.get("name", t.specialization)
            badge_surf = self.font_small.render(f"★ {spec_name} (Nv.4)", True, COLOR_GOLD_LIGHT)
            bw = badge_surf.get_width() + 16
            pygame.draw.rect(surface, (26, 22, 36), (tx - bw // 2, ty - 56, bw, 22), border_radius=4)
            pygame.draw.rect(surface, COLOR_GOLD, (tx - bw // 2, ty - 56, bw, 22), 1, border_radius=4)
            surface.blit(badge_surf, (tx - badge_surf.get_width() // 2, ty - 53))

        # Botón de Mejora de Nivel (1 -> 2, 2 -> 3)
        elif t.level < 3:
            cost_key = "upgrade_cost" if t.level == 1 else "l3_upgrade_cost"
            cost = data[cost_key]
            can_afford = self.gold >= cost
            bx, by = tx, ty - 55
            is_hover = math.hypot(mx - bx, my - by) <= 22
            
            pygame.draw.circle(surface, (50, 75, 45) if is_hover else (32, 28, 42), (int(bx), int(by)), 22)
            pygame.draw.circle(surface, COLOR_GOLD if can_afford else (120, 120, 120), (int(bx), int(by)), 22, 2)
            
            lvl_surf = self.font_small.render(f"Nv.{t.level+1}", True, COLOR_WHITE)
            cost_surf = self.font_small.render(f"{cost}g", True, COLOR_GOLD if can_afford else (220, 90, 90))
            surface.blit(lvl_surf, (bx - lvl_surf.get_width() // 2, by - 12))
            surface.blit(cost_surf, (bx - cost_surf.get_width() // 2, by + 1))

            if is_hover:
                nxt_lvl = t.level + 1
                nxt_dmg = data.get(f"l{nxt_lvl}_damage", "-")
                nxt_rng = data.get(f"l{nxt_lvl}_range", "-")
                card_w, card_h = 240, 68
                cx = min(max(10, mx - card_w // 2), SCREEN_WIDTH - card_w - 10)
                cy = max(10, my - 85)
                pygame.draw.rect(surface, (26, 23, 34), (cx, cy, card_w, card_h), border_radius=6)
                pygame.draw.rect(surface, COLOR_GOLD, (cx, cy, card_w, card_h), 1, border_radius=6)
                t_s = self.font_small.render(f"Mejorar a Nivel {nxt_lvl} ({cost}g)", True, COLOR_GOLD_LIGHT)
                d_s = self.font_small.render(f"Daño: {t.damage} ➔ {nxt_dmg} | Rango: {int(t.range)} ➔ {nxt_rng}", True, COLOR_WHITE)
                c_s = self.font_small.render("¡Clic para mejorar!" if can_afford else "Oro insuficiente", True, (120, 220, 120) if can_afford else (240, 90, 90))
                surface.blit(t_s, (cx + 10, cy + 8))
                surface.blit(d_s, (cx + 10, cy + 28))
                surface.blit(c_s, (cx + 10, cy + 46))

        # Especializaciones A y B (Nivel 3 -> Nivel 4)
        elif t.level == 3 and t.specialization is None:
            spec_a = data["special_a"]
            spec_b = data["special_b"]
            can_a = self.gold >= spec_a["cost"]
            can_b = self.gold >= spec_b["cost"]

            bx_a, by_a = tx - 40, ty - 55
            bx_b, by_b = tx + 40, ty - 55
            hover_a = math.hypot(mx - bx_a, my - by_a) <= 24
            hover_b = math.hypot(mx - bx_b, my - by_b) <= 24

            # Rótulo superior orientativo
            lbl_surf = self.font_small.render("Elige Especialización (Nv.4)", True, COLOR_GOLD_LIGHT)
            lw = lbl_surf.get_width() + 16
            pygame.draw.rect(surface, (20, 18, 28, 220), (tx - lw // 2, ty - 88, lw, 20), border_radius=4)
            pygame.draw.rect(surface, COLOR_UI_BORDER, (tx - lw // 2, ty - 88, lw, 20), 1, border_radius=4)
            surface.blit(lbl_surf, (tx - lbl_surf.get_width() // 2, ty - 86))

            # Botón Especialización A (Azul / Cyan)
            bg_a = (40, 55, 75) if hover_a else (25, 30, 45)
            border_a = (80, 200, 255) if can_a else (110, 120, 140)
            pygame.draw.circle(surface, bg_a, (int(bx_a), int(by_a)), 24)
            pygame.draw.circle(surface, border_a, (int(bx_a), int(by_a)), 24, 2)
            lbl_a = self.font_main.render("A", True, (100, 220, 255))
            cost_a = self.font_small.render(f"{spec_a['cost']}g", True, COLOR_GOLD if can_a else (220, 90, 90))
            surface.blit(lbl_a, (bx_a - lbl_a.get_width() // 2, by_a - 14))
            surface.blit(cost_a, (bx_a - cost_a.get_width() // 2, by_a + 2))

            # Nombre breve debajo de botón A
            name_a_short = spec_a['name'][:12]
            ns_a = self.font_small.render(name_a_short, True, COLOR_WHITE)
            surface.blit(ns_a, (bx_a - ns_a.get_width() // 2, by_a + 26))

            # Botón Especialización B (Rojo / Fuego)
            bg_b = (75, 45, 40) if hover_b else (45, 25, 25)
            border_b = (255, 120, 80) if can_b else (140, 110, 110)
            pygame.draw.circle(surface, bg_b, (int(bx_b), int(by_b)), 24)
            pygame.draw.circle(surface, border_b, (int(bx_b), int(by_b)), 24, 2)
            lbl_b = self.font_main.render("B", True, (255, 140, 100))
            cost_b = self.font_small.render(f"{spec_b['cost']}g", True, COLOR_GOLD if can_b else (220, 90, 90))
            surface.blit(lbl_b, (bx_b - lbl_b.get_width() // 2, by_b - 14))
            surface.blit(cost_b, (bx_b - cost_b.get_width() // 2, by_b + 2))

            # Nombre breve debajo de botón B
            name_b_short = spec_b['name'][:12]
            ns_b = self.font_small.render(name_b_short, True, COLOR_WHITE)
            surface.blit(ns_b, (bx_b - ns_b.get_width() // 2, by_b + 26))

            # TARJETA DETALLADA DE EXPLICACIÓN AL PASAR EL RATÓN (Hover A o Hover B)
            if hover_a:
                self._draw_spec_card(surface, "A", spec_a, can_a, (80, 200, 255), mx, my)
            elif hover_b:
                self._draw_spec_card(surface, "B", spec_b, can_b, (255, 140, 100), mx, my)

        # Botón de Venta (Abajo a la derecha)
        sell_x, sell_y = tx + 45, ty + 35
        sell_val = t.sell_value()
        pygame.draw.circle(surface, (70, 30, 35), (int(sell_x), int(sell_y)), 18)
        pygame.draw.circle(surface, COLOR_ROYAL_RED, (int(sell_x), int(sell_y)), 18, 1)
        sell_txt = self.font_small.render(f"+{sell_val}g", True, COLOR_GOLD)
        surface.blit(sell_txt, (sell_x - sell_txt.get_width() // 2, sell_y - 6))

        # Selector de Objetivo o Bandera de Rally (Abajo a la izquierda)
        opt_x, opt_y = tx - 45, ty + 35
        pygame.draw.circle(surface, COLOR_UI_PANEL, (int(opt_x), int(opt_y)), 18)
        pygame.draw.circle(surface, COLOR_GOLD, (int(opt_x), int(opt_y)), 18, 1)
        if t.tower_type == "barracks":
            gfx.draw_flag(surface, opt_x, opt_y, COLOR_WHITE, 8)
        else:
            mode_initials = {"first": "1º", "last": "Fin", "strongest": "Max", "weakest": "Min", "closest": "Cerc"}
            mode_txt = self.font_small.render(mode_initials.get(t.targeting_mode, "1º"), True, COLOR_WHITE)
            surface.blit(mode_txt, (opt_x - mode_txt.get_width() // 2, opt_y - 6))

    def _draw_spec_card(self, surface, branch_key, s_data, afford, accent_col, mx, my):
        lines = []
        lines.append((f"Rama [{branch_key}]: {s_data['name']}", accent_col, True))
        lines.append((f"Coste: {s_data['cost']} Monedas de Oro", COLOR_GOLD if afford else (240, 90, 90), False))
        lines.append((f"Efecto: {s_data['desc']}", (220, 220, 220), False))
        
        # Atributos destacados
        perks = []
        if "damage" in s_data:
            perks.append(f"Daño: {s_data['damage']}")
        if "hp" in s_data:
            perks.append(f"Vida: {s_data['hp']}")
        if "range" in s_data:
            perks.append(f"Alcance: {s_data['range']}")
        if "fire_rate" in s_data:
            perks.append(f"Cadencia: {s_data['fire_rate']}/s")
        if "crit_chance" in s_data:
            perks.append(f"Crítico: {int(s_data['crit_chance']*100)}% (x{s_data.get('crit_mult', 2.0)})")
        if "poison_dps" in s_data:
            perks.append(f"Veneno: {s_data['poison_dps']} DPS")
        if "burn_dps" in s_data:
            perks.append(f"Fuego: {s_data['burn_dps']} DPS")
        if "stun_duration" in s_data:
            perks.append(f"Aturde: {s_data['stun_duration']}s")
        if "slow_amount" in s_data:
            perks.append(f"Ralentiza: {int(s_data['slow_amount']*100)}%")
        if "chain_targets" in s_data:
            perks.append(f"Rayo: {s_data['chain_targets']} enemigos")
        if "armor_shred" in s_data:
            perks.append(f"Ácido: -{int(s_data['armor_shred']*100)}% armadura")
        if "buff_damage_mult" in s_data:
            perks.append(f"Aura Aliada: +{int((s_data['buff_damage_mult']-1)*100)}% daño")

        if perks:
            lines.append((" | ".join(perks[:3]), COLOR_GOLD_LIGHT, False))
            if len(perks) > 3:
                lines.append((" | ".join(perks[3:]), COLOR_GOLD_LIGHT, False))

        prompt = "¡Haz clic para elegir esta rama!" if afford else "Oro insuficiente para esta rama"
        prompt_col = (120, 240, 120) if afford else (240, 90, 90)
        lines.append((prompt, prompt_col, False))

        card_w = 340
        card_h = 24 + len(lines) * 20
        cx = min(max(15, mx - card_w // 2), SCREEN_WIDTH - card_w - 15)
        cy = max(15, my - card_h - 15)
        
        pygame.draw.rect(surface, (22, 19, 30), (cx, cy, card_w, card_h), border_radius=8)
        pygame.draw.rect(surface, accent_col, (cx, cy, card_w, card_h), 2, border_radius=8)

        cur_y = cy + 10
        for text, col, is_bold in lines:
            f = self.font_main if is_bold else self.font_small
            surf = f.render(text, True, col)
            surface.blit(surf, (cx + 12, cur_y))
            cur_y += 20

    def _draw_hud(self, surface):
        # 1. Barra Superior Medieval Glassmorphism
        top_h = 45
        top_surf = pygame.Surface((SCREEN_WIDTH, top_h), pygame.SRCALPHA)
        top_surf.fill((22, 20, 28, 235))
        pygame.draw.line(top_surf, COLOR_UI_BORDER, (0, top_h - 1), (SCREEN_WIDTH, top_h - 1), 2)
        surface.blit(top_surf, (0, 0))

        # Vidas (Corazones vectoriales)
        gfx.draw_heart(surface, 28, 22, size=14)
        lives_txt = self.font_main.render(f"{self.lives}/{self.max_lives}", True, (255, 100, 110))
        surface.blit(lives_txt, (42, 11))

        # Oro (Monedas vectoriales)
        gfx.draw_coin(surface, 155, 22, radius=8)
        gold_txt = self.font_main.render(f"{self.gold}", True, COLOR_GOLD)
        surface.blit(gold_txt, (168, 11))

        # Oleada
        wave_str = f"Oleada: {self.current_wave_idx}/{len(self.waves)}"
        wave_txt = self.font_main.render(wave_str, True, COLOR_WHITE)
        surface.blit(wave_txt, (290, 11))

        # Botón Siguiente Oleada / Temporizador
        if not self.wave_active and self.current_wave_idx < len(self.waves):
            btn_rect = pygame.Rect(480, 6, 150, 32)
            pygame.draw.rect(surface, (60, 110, 50), btn_rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_GOLD, btn_rect, 1, border_radius=4)
            nxt_txt = self.font_small.render(f"¡Llamar! (+{int(self.wave_countdown*5)}g)", True, COLOR_WHITE)
            surface.blit(nxt_txt, (btn_rect.centerx - nxt_txt.get_width() // 2, btn_rect.centery - nxt_txt.get_height() // 2))
        elif self.wave_active:
            rem_txt = self.font_small.render(f"Enemigos restantes: {len(self.enemies) + len(self.wave_spawn_queue)}", True, (240, 180, 80))
            surface.blit(rem_txt, (480, 14))

        # Puntuación
        score_txt = self.font_main.render(f"Puntos: {self.score}", True, COLOR_STONE_LIGHT)
        surface.blit(score_txt, (820, 11))

        # Controles de Velocidad (1x, 2x, 4x, Pausa)
        speeds = [(1070, "1x", self.game_speed == 1.0 and not self.is_paused),
                  (1115, "2x", self.game_speed == 2.0 and not self.is_paused),
                  (1160, "4x", self.game_speed == 4.0 and not self.is_paused),
                  (1205, "pause", self.is_paused)]
        for x, label, active in speeds:
            w = 40 if len(label) <= 2 else 55
            r = pygame.Rect(x, 6, w, 32)
            bg = (85, 80, 110) if active else (40, 36, 50)
            pygame.draw.rect(surface, bg, r, border_radius=4)
            pygame.draw.rect(surface, COLOR_GOLD if active else COLOR_STONE_DARK, r, 1, border_radius=4)
            if label == "pause":
                gfx.draw_pause_play(surface, r.centerx, r.centery, self.is_paused, COLOR_GOLD if active else COLOR_WHITE, 7)
            else:
                lbl = self.font_small.render(label, True, COLOR_GOLD if active else COLOR_WHITE)
                surface.blit(lbl, (r.centerx - lbl.get_width() // 2, r.centery - lbl.get_height() // 2))

        # 2. Panel de Hechizos Inferior Izquierdo
        spell_keys = ["rain_of_arrows", "reinforcements", "meteor"]
        spell_colors = [(200, 200, 255), (120, 220, 140), (255, 120, 50)]
        for i, k in enumerate(spell_keys):
            bx = 20 + i * 80
            by = SCREEN_HEIGHT - 75
            r = pygame.Rect(bx, by, 70, 65)
            data = SPELL_DATA[k]
            ready = self.spells.is_ready(k)
            is_selected = (self.casting_spell == k)
            
            # Fondo
            bg_col = (50, 45, 65) if ready else (25, 22, 32)
            pygame.draw.rect(surface, bg_col, r, border_radius=6)
            border_col = COLOR_GOLD_LIGHT if is_selected else (COLOR_GOLD if ready else (80, 80, 80))
            pygame.draw.rect(surface, border_col, r, 2 if (ready or is_selected) else 1, border_radius=6)

            # Barra de recarga (Cooldown)
            prog = self.spells.get_progress(k)
            if prog < 1.0:
                cd_h = int(r.height * (1.0 - prog))
                cd_rect = pygame.Rect(r.x, r.bottom - cd_h, r.width, cd_h)
                pygame.draw.rect(surface, (0, 0, 0, 160), cd_rect, border_bottom_left_radius=6, border_bottom_right_radius=6)

            # Icono y Tecla de atajo
            key_txt = self.font_small.render(f"[{data['key']}]", True, COLOR_GOLD_LIGHT if ready else (120, 120, 120))
            name_txt = self.font_small.render(data["name"][:7], True, COLOR_WHITE if ready else (100, 100, 100))
            surface.blit(key_txt, (r.centerx - key_txt.get_width() // 2, r.y + 6))
            surface.blit(name_txt, (r.centerx - name_txt.get_width() // 2, r.y + 36))
