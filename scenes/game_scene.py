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
from entities.towers import Tower
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
            # Menú de selección de 4 torres alrededor del pedestal
            tower_types = ["archer", "catapult", "mage", "barracks"]
            angles = [-math.pi*0.75, -math.pi*0.25, math.pi*0.25, math.pi*0.75]
            radius = 55
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
                if math.hypot(mx - (tx - 35), my - (ty - 55)) <= 20:
                    cost = TOWER_DATA[self.selected_tower.tower_type]["special_a"]["cost"]
                    if self.gold >= cost:
                        self.gold -= self.selected_tower.upgrade_special("special_a", self.gold)
                        self.particles.add_magic_burst(tx, ty, COLOR_ROYAL_BLUE, count=15)
                        return
                # Botón Especial B
                if math.hypot(mx - (tx + 35), my - (ty - 55)) <= 20:
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
            if hasattr(p, 'splash_radius'):
                p.update(dt, self.enemies, self.particles)
            elif hasattr(p, 'is_frost'):
                p.update(dt, self.enemies, self.particles)
            else:
                p.update(dt, self.particles)
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
        tower_types = ["archer", "catapult", "mage", "barracks"]
        angles = [-math.pi*0.75, -math.pi*0.25, math.pi*0.25, math.pi*0.75]
        radius = 55
        mx, my = pygame.mouse.get_pos()

        for i, ttype in enumerate(tower_types):
            bx = sx + math.cos(angles[i]) * radius
            by = sy + math.sin(angles[i]) * radius
            data = TOWER_DATA[ttype]
            cost = data["cost"]
            can_afford = self.gold >= cost
            is_hover = math.hypot(mx - bx, my - by) <= 24

            # Botón circular
            bg_col = COLOR_UI_PANEL if not is_hover else (65, 60, 80)
            border_col = COLOR_GOLD if can_afford else (120, 120, 120)
            pygame.draw.circle(surface, bg_col, (int(bx), int(by)), 24)
            pygame.draw.circle(surface, border_col, (int(bx), int(by)), 24, 2)

            # Mini icono
            if ttype == "archer":
                pygame.draw.line(surface, COLOR_WOOD_MID, (bx - 10, by + 8), (bx + 10, by - 8), 3)
            elif ttype == "catapult":
                pygame.draw.circle(surface, COLOR_FIRE_ORANGE, (int(bx), int(by)), 8)
            elif ttype == "mage":
                pygame.draw.circle(surface, COLOR_ARCANE_PURPLE, (int(bx), int(by)), 8)
            elif ttype == "barracks":
                pygame.draw.rect(surface, COLOR_ROYAL_BLUE, (bx - 8, by - 8, 16, 16), border_radius=3)

            # Etiqueta de precio debajo
            cost_surf = self.font_small.render(f"{cost}🪙", True, COLOR_GOLD if can_afford else (200, 80, 80))
            surface.blit(cost_surf, (bx - cost_surf.get_width() // 2, by + 26))

            # Tooltip al hacer hover
            if is_hover:
                tip = f"{data['name']} ({cost}g): {data['description']}"
                tip_surf = self.font_small.render(tip, True, COLOR_WHITE)
                pygame.draw.rect(surface, COLOR_UI_BG, (mx - tip_surf.get_width()//2 - 6, my - 35, tip_surf.get_width() + 12, 24), border_radius=4)
                pygame.draw.rect(surface, COLOR_GOLD, (mx - tip_surf.get_width()//2 - 6, my - 35, tip_surf.get_width() + 12, 24), 1, border_radius=4)
                surface.blit(tip_surf, (mx - tip_surf.get_width()//2, my - 31))

    def _draw_tower_inspector(self, surface):
        if not self.selected_tower:
            return
        t = self.selected_tower
        tx, ty = t.x, t.y
        data = TOWER_DATA[t.tower_type]
        mx, my = pygame.mouse.get_pos()

        # Botón de Mejora (Arriba)
        if t.level < 3:
            cost = data["upgrade_cost" if t.level == 1 else "l3_upgrade_cost"]
            can_afford = self.gold >= cost
            bx, by = tx, ty - 55
            is_hover = math.hypot(mx - bx, my - by) <= 22
            pygame.draw.circle(surface, (50, 75, 45) if is_hover else COLOR_UI_PANEL, (int(bx), int(by)), 22)
            pygame.draw.circle(surface, COLOR_GOLD if can_afford else (120, 120, 120), (int(bx), int(by)), 22, 2)
            
            lvl_surf = self.font_small.render(f"Nv.{t.level+1}", True, COLOR_WHITE)
            cost_surf = self.font_small.render(f"{cost}🪙", True, COLOR_GOLD if can_afford else (200, 80, 80))
            surface.blit(lvl_surf, (bx - lvl_surf.get_width() // 2, by - 12))
            surface.blit(cost_surf, (bx - cost_surf.get_width() // 2, by + 1))
        elif t.level == 3 and t.specialization is None:
            # Especialización A
            spec_a = data["special_a"]
            can_a = self.gold >= spec_a["cost"]
            bx, by = tx - 35, ty - 55
            pygame.draw.circle(surface, COLOR_UI_PANEL, (int(bx), int(by)), 20)
            pygame.draw.circle(surface, COLOR_ROYAL_BLUE if can_a else (120, 120, 120), (int(bx), int(by)), 20, 2)
            txt_a = self.font_small.render(f"{spec_a['cost']}🪙", True, COLOR_GOLD if can_a else (200, 80, 80))
            surface.blit(txt_a, (bx - txt_a.get_width() // 2, by - 6))

            # Especialización B
            spec_b = data["special_b"]
            can_b = self.gold >= spec_b["cost"]
            bx2, by2 = tx + 35, ty - 55
            pygame.draw.circle(surface, COLOR_UI_PANEL, (int(bx2), int(by2)), 20)
            pygame.draw.circle(surface, COLOR_ROYAL_RED if can_b else (120, 120, 120), (int(bx2), int(by2)), 20, 2)
            txt_b = self.font_small.render(f"{spec_b['cost']}🪙", True, COLOR_GOLD if can_b else (200, 80, 80))
            surface.blit(txt_b, (bx2 - txt_b.get_width() // 2, by2 - 6))

        # Botón de Venta (Abajo a la derecha)
        sell_x, sell_y = tx + 45, ty + 35
        sell_val = t.sell_value()
        pygame.draw.circle(surface, (70, 30, 35), (int(sell_x), int(sell_y)), 18)
        pygame.draw.circle(surface, COLOR_ROYAL_RED, (int(sell_x), int(sell_y)), 18, 1)
        sell_txt = self.font_small.render(f"{sell_val}🪙", True, COLOR_GOLD)
        surface.blit(sell_txt, (sell_x - sell_txt.get_width() // 2, sell_y - 6))

        # Selector de Objetivo o Bandera de Rally (Abajo a la izquierda)
        opt_x, opt_y = tx - 45, ty + 35
        pygame.draw.circle(surface, COLOR_UI_PANEL, (int(opt_x), int(opt_y)), 18)
        pygame.draw.circle(surface, COLOR_GOLD, (int(opt_x), int(opt_y)), 18, 1)
        if t.tower_type == "barracks":
            flag_txt = self.font_small.render("🚩", True, COLOR_WHITE)
            surface.blit(flag_txt, (opt_x - flag_txt.get_width() // 2, opt_y - 8))
        else:
            mode_initials = {"first": "1º", "last": "Fin", "strongest": "Max", "weakest": "Min", "closest": "Cerc"}
            mode_txt = self.font_small.render(mode_initials.get(t.targeting_mode, "1º"), True, COLOR_WHITE)
            surface.blit(mode_txt, (opt_x - mode_txt.get_width() // 2, opt_y - 6))

    def _draw_hud(self, surface):
        # 1. Barra Superior Medieval Glassmorphism
        top_h = 45
        top_surf = pygame.Surface((SCREEN_WIDTH, top_h), pygame.SRCALPHA)
        top_surf.fill((22, 20, 28, 235))
        pygame.draw.line(top_surf, COLOR_UI_BORDER, (0, top_h - 1), (SCREEN_WIDTH, top_h - 1), 2)
        surface.blit(top_surf, (0, 0))

        # Vidas (Corazones)
        lives_txt = self.font_main.render(f"❤️ {self.lives}/{self.max_lives}", True, (255, 80, 90))
        surface.blit(lives_txt, (20, 10))

        # Oro (Monedas)
        gold_txt = self.font_main.render(f"🪙 {self.gold}", True, COLOR_GOLD)
        surface.blit(gold_txt, (160, 10))

        # Oleada
        wave_str = f"Oleada: {self.current_wave_idx}/{len(self.waves)}"
        wave_txt = self.font_main.render(wave_str, True, COLOR_WHITE)
        surface.blit(wave_txt, (300, 10))

        # Botón Siguiente Oleada / Temporizador
        if not self.wave_active and self.current_wave_idx < len(self.waves):
            btn_rect = pygame.Rect(480, 6, 150, 32)
            pygame.draw.rect(surface, (60, 110, 50), btn_rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_GOLD, btn_rect, 1, border_radius=4)
            nxt_txt = self.font_small.render(f"¡Llamar! (+{int(self.wave_countdown*5)}🪙)", True, COLOR_WHITE)
            surface.blit(nxt_txt, (btn_rect.centerx - nxt_txt.get_width() // 2, btn_rect.centery - nxt_txt.get_height() // 2))
        elif self.wave_active:
            rem_txt = self.font_small.render(f"Enemigos restantes: {len(self.enemies) + len(self.wave_spawn_queue)}", True, (240, 180, 80))
            surface.blit(rem_txt, (480, 14))

        # Puntuación
        score_txt = self.font_main.render(f"Puntos: {self.score}", True, COLOR_STONE_LIGHT)
        surface.blit(score_txt, (820, 10))

        # Controles de Velocidad (1x, 2x, 4x, Pausa)
        speeds = [(1070, "1x", self.game_speed == 1.0 and not self.is_paused),
                  (1115, "2x", self.game_speed == 2.0 and not self.is_paused),
                  (1160, "4x", self.game_speed == 4.0 and not self.is_paused),
                  (1205, "⏸️" if not self.is_paused else "▶️", self.is_paused)]
        for x, label, active in speeds:
            w = 40 if len(label) <= 2 else 55
            r = pygame.Rect(x, 6, w, 32)
            bg = (85, 80, 110) if active else (40, 36, 50)
            pygame.draw.rect(surface, bg, r, border_radius=4)
            pygame.draw.rect(surface, COLOR_GOLD if active else COLOR_STONE_DARK, r, 1, border_radius=4)
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
