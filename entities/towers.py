"""
Torres Defensivas, Proyectiles y Lógica de Ataque para 'Reino en Asedio'.
"""

import math
import random
import pygame
from config import (
    TOWER_DATA, COLOR_WHITE, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_FIRE_ORANGE,
    COLOR_ARCANE_PURPLE, COLOR_ICE_CYAN, COLOR_STONE_MID, COLOR_STONE_LIGHT,
    COLOR_ROYAL_BLUE, COLOR_ROYAL_RED, COLOR_BLACK
)
from engine.graphics import gfx
from engine.audio import sound_manager
from entities.soldiers import Soldier

# ------------------ PROYECTILES ------------------

class Arrow:
    def __init__(self, x, y, target, damage, damage_type="physical", is_crit=False, poison=None):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.damage_type = damage_type
        self.is_crit = is_crit
        self.poison = poison # (dps, duration)
        self.speed = 460.0
        self.alive = True
        self.target_pos = (target.x, target.y) if target.alive else (x, y)
        self.angle = 0.0

    def update(self, dt, particle_sys):
        if not self.alive:
            return

        if self.target and self.target.alive:
            self.target_pos = (self.target.x, self.target.y)

        dx = self.target_pos[0] - self.x
        dy = self.target_pos[1] - self.y
        dist = math.hypot(dx, dy)
        self.angle = math.atan2(dy, dx)

        step = self.speed * dt
        if dist <= step or dist < 8:
            self.alive = False
            if self.target and self.target.alive:
                dmg = self.target.take_damage(self.damage, self.damage_type, is_crit=self.is_crit)
                if self.poison:
                    self.target.apply_poison(self.poison[0], self.poison[1])
                sound_manager.play("arrow_hit")
                particle_sys.add_hit_spark(self.target.x, self.target.y, count=3)
                particle_sys.add_floating_damage(self.target.x, self.target.y, dmg, self.damage_type, self.is_crit)
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step

    def draw(self, surface):
        if not self.alive:
            return
        # Dibujar flecha estilizada
        arrow_len = 14
        ex = self.x + math.cos(self.angle) * arrow_len
        ey = self.y + math.sin(self.angle) * arrow_len
        pygame.draw.line(surface, COLOR_WHITE, (self.x, self.y), (ex, ey), 2)
        # Pluma
        pygame.draw.circle(surface, COLOR_GOLD, (int(self.x), int(self.y)), 2)

class CatapultRock:
    def __init__(self, x, y, target_x, target_y, damage, splash_radius, is_fire=False, is_stun=False, burn_info=None):
        self.start_x = float(x)
        self.start_y = float(y)
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.x = self.start_x
        self.y = self.start_y
        self.damage = damage
        self.splash_radius = splash_radius
        self.is_fire = is_fire
        self.is_stun = is_stun
        self.burn_info = burn_info # (dps, duration)
        
        self.total_dist = math.hypot(self.target_x - self.start_x, self.target_y - self.start_y)
        self.speed = 280.0
        self.total_time = max(0.4, self.total_dist / self.speed)
        self.time = 0.0
        self.alive = True
        self.arc_height = min(120.0, self.total_dist * 0.45)

    def update(self, dt, enemies, particle_sys):
        if not self.alive:
            return

        self.time += dt
        progress = min(1.0, self.time / self.total_time)
        
        # Trayectoria parabólica
        self.x = self.start_x + (self.target_x - self.start_x) * progress
        linear_y = self.start_y + (self.target_y - self.start_y) * progress
        # Parábola de altura
        height_offset = 4 * self.arc_height * progress * (1.0 - progress)
        self.y = linear_y - height_offset

        # Partículas de humo/fuego en vuelo
        if self.is_fire and random.random() < 0.6:
            particle_sys.add_hit_spark(self.x, self.y, COLOR_FIRE_ORANGE, count=1)

        if progress >= 1.0:
            self.alive = False
            sound_manager.play("explosion")
            particle_sys.add_explosion(self.target_x, self.target_y, self.splash_radius)
            
            # Daño de área
            for enemy in enemies:
                if enemy.alive and not enemy.is_flying:
                    dist = math.hypot(enemy.x - self.target_x, enemy.y - self.target_y)
                    if dist <= self.splash_radius:
                        # Daño con atenuación por distancia mínima
                        dmg_factor = max(0.4, 1.0 - (dist / self.splash_radius) * 0.6)
                        actual_dmg = self.damage * dmg_factor
                        dealt = enemy.take_damage(actual_dmg, "physical")
                        particle_sys.add_floating_damage(enemy.x, enemy.y, dealt, "physical")
                        
                        if self.is_stun:
                            enemy.apply_stun(0.8)
                        if self.burn_info:
                            enemy.apply_burn(self.burn_info[0], self.burn_info[1])

            # Suelo en llamas con Fuego Valyrio
            if self.is_fire and self.burn_info:
                particle_sys.add_ground_effect(self.target_x, self.target_y, self.splash_radius, 'fire', duration=4.0, dps=self.burn_info[0])

    def draw(self, surface):
        if not self.alive:
            return
        col = COLOR_FIRE_ORANGE if self.is_fire else COLOR_STONE_MID
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), 6, 1)

class MagicBolt:
    def __init__(self, x, y, target, damage, is_frost=False, is_chain=False, chain_count=0):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.is_frost = is_frost
        self.is_chain = is_chain
        self.chain_count = chain_count
        self.speed = 360.0
        self.alive = True

    def update(self, dt, enemies, particle_sys):
        if not self.alive:
            return

        if not self.target or not self.target.alive:
            # Reasignar al enemigo más cercano si murió
            closest = None
            min_d = 200
            for e in enemies:
                if e.alive:
                    d = math.hypot(e.x - self.x, e.y - self.y)
                    if d < min_d:
                        min_d = d
                        closest = e
            self.target = closest
            if not self.target:
                self.alive = False
                return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt

        if dist <= step or dist < 10:
            self.alive = False
            dmg = self.target.take_damage(self.damage, "magic")
            particle_sys.add_floating_damage(self.target.x, self.target.y, dmg, "magic")

            if self.is_frost:
                sound_manager.play("freeze")
                self.target.apply_slow(0.5, 2.5)
                particle_sys.add_magic_burst(self.target.x, self.target.y, COLOR_ICE_CYAN, count=8)
            else:
                sound_manager.play("magic_zap")
                particle_sys.add_magic_burst(self.target.x, self.target.y, COLOR_ARCANE_PURPLE, count=8)

            # Cadena de rayos
            if self.is_chain and self.chain_count > 0:
                sound_manager.play("lightning")
                # Buscar siguiente objetivo
                next_targets = [e for e in enemies if e.alive and e != self.target]
                if next_targets:
                    next_targets.sort(key=lambda e: math.hypot(e.x - self.target.x, e.y - self.target.y))
                    next_target = next_targets[0]
                    if math.hypot(next_target.x - self.target.x, next_target.y - self.target.y) <= 160:
                        # Relámpago instantáneo
                        particle_sys.shockwaves.append(
                            type('Shock', (), {'x': self.target.x, 'y': self.target.y, 'update': lambda s, dt: False, 'draw': lambda s, surf: pygame.draw.line(surf, (255, 240, 90), (self.target.x, self.target.y), (next_target.x, next_target.y), 3)})()
                        )
                        c_dmg = next_target.take_damage(self.damage * 0.75, "magic")
                        particle_sys.add_floating_damage(next_target.x, next_target.y, c_dmg, "magic")
                        particle_sys.add_hit_spark(next_target.x, next_target.y, (255, 240, 90), count=6)
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step

    def draw(self, surface):
        if not self.alive:
            return
        col = COLOR_ICE_CYAN if self.is_frost else (COLOR_ARCANE_PURPLE if not self.is_chain else (255, 240, 90))
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.x), int(self.y)), 3)

class AlchemistPotion:
    def __init__(self, x, y, target, damage, armor_shred=0.20, is_plague=False, is_acid=False):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.armor_shred = armor_shred
        self.is_plague = is_plague
        self.is_acid = is_acid
        self.speed = 340.0
        self.alive = True
        self.target_pos = (target.x, target.y) if target and target.alive else (x, y)
        self.angle = 0.0

    def update(self, dt, enemies, particle_sys):
        if not self.alive:
            return
        if self.target and self.target.alive:
            self.target_pos = (self.target.x, self.target.y)
        dx = self.target_pos[0] - self.x
        dy = self.target_pos[1] - self.y
        dist = math.hypot(dx, dy)
        self.angle += dt * 15.0
        step = self.speed * dt
        if dist <= step or dist < 12:
            self.alive = False
            sound_manager.play("acid_splash")
            splash_rad = 55 if self.is_plague else 40
            liquid_col = (140, 50, 210) if self.is_plague else (60, 240, 80)
            particle_sys.add_magic_burst(self.target_pos[0], self.target_pos[1], liquid_col, count=10)
            for e in enemies:
                if e.alive and math.hypot(e.x - self.target_pos[0], e.y - self.target_pos[1]) <= splash_rad:
                    dmg = e.take_damage(self.damage, "magic")
                    e.armor = max(0.0, e.armor - self.armor_shred)
                    e.apply_slow(0.35, 2.5)
                    if self.is_plague:
                        e.apply_poison(22, 4.0)
                    if self.is_acid:
                        e.apply_burn(30, 3.0)
                    particle_sys.add_floating_damage(e.x, e.y, dmg, "magic")
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step

    def draw(self, surface):
        if not self.alive:
            return
        col = (140, 50, 210) if self.is_plague else (60, 240, 80)
        pygame.draw.circle(surface, (230, 210, 180), (int(self.x), int(self.y - 4)), 3)
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(surface, (200, 255, 180), (int(self.x), int(self.y)), 2)

class SunBeamEffect:
    def __init__(self, x1, y1, target, damage, is_divine=False):
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.target = target
        self.damage = damage
        self.is_divine = is_divine
        self.alive = True
        self.timer = 0.20

    def update(self, dt, enemies, particle_sys):
        if not self.alive:
            return
        self.timer -= dt
        if self.timer <= 0 or not self.target or not self.target.alive:
            self.alive = False
            return
        dmg = self.target.take_damage(self.damage * dt * 2.0, "magic")
        if self.timer > 0.16:
            sound_manager.play("sun_beam")
            particle_sys.add_hit_spark(self.target.x, self.target.y, (255, 240, 100), count=2)

    def draw(self, surface):
        if not self.alive or not self.target:
            return
        beam_width = 5 if self.is_divine else 3
        glow_color = (255, 240, 150) if not self.is_divine else (255, 160, 40)
        pygame.draw.line(surface, glow_color, (int(self.x1), int(self.y1)), (int(self.target.x), int(self.target.y)), beam_width + 4)
        pygame.draw.line(surface, COLOR_WHITE, (int(self.x1), int(self.y1)), (int(self.target.x), int(self.target.y)), beam_width)
        pygame.draw.circle(surface, COLOR_GOLD_LIGHT, (int(self.target.x), int(self.target.y)), 6)

# ------------------ CLASE BASE DE TORRE ------------------

class Tower:
    def __init__(self, tower_type, x, y):
        self.tower_type = tower_type
        self.x = float(x)
        self.y = float(y)
        self.level = 1
        self.specialization = None # "special_a" or "special_b"
        self.targeting_mode = "first" # 'first', 'last', 'strongest', 'weakest', 'closest'
        
        data = TOWER_DATA[tower_type]
        self.cost = data["cost"]
        self.total_invested = self.cost
        self.range = float(data.get("range", data.get("rally_range", 160)))
        self.damage = float(data.get("damage", 10))
        self.fire_rate = float(data.get("fire_rate", 1.0))
        self.damage_type = data.get("damage_type", "physical")
        self.min_range = float(data.get("min_range", 0.0))
        self.splash_radius = float(data.get("splash_radius", 0.0))
        
        self.cooldown = 0.0
        self.animation_time = 0.0
        self.selected = False
        
        # Para barracones
        self.soldiers = []
        self.rally_x = self.x
        self.rally_y = self.y + 45
        self.respawn_timer = 0.0
        
        if tower_type == "barracks":
            self._init_barracks()

    def _init_barracks(self):
        self.soldiers = []
        angles = [-0.4, 0.0, 0.4]
        for i in range(3):
            sx = self.rally_x + math.sin(angles[i]) * 20
            sy = self.rally_y + math.cos(angles[i]) * 10
            s = Soldier(self.x, self.y, sx, sy, soldier_type="militia", stats=TOWER_DATA["barracks"], parent_tower=self)
            self.soldiers.append(s)

    def set_rally_point(self, rx, ry):
        self.rally_x = rx
        self.rally_y = ry
        angles = [-0.4, 0.0, 0.4]
        for i, s in enumerate(self.soldiers):
            sx = self.rally_x + math.sin(angles[i]) * 20
            sy = self.rally_y + math.cos(angles[i]) * 10
            s.set_rally_point(sx, sy)

    def upgrade_level(self, player_gold):
        data = TOWER_DATA[self.tower_type]
        if self.level == 1:
            cost = data["upgrade_cost"]
            if player_gold >= cost:
                self.level = 2
                self.total_invested += cost
                if self.tower_type == "archer":
                    self.damage = data["l2_damage"]
                    self.range = data["l2_range"]
                    self.fire_rate = data["l2_fire_rate"]
                elif self.tower_type == "catapult":
                    self.damage = data["l2_damage"]
                    self.range = data["l2_range"]
                    self.splash_radius = data["l2_splash"]
                elif self.tower_type == "mage":
                    self.damage = data["l2_damage"]
                    self.range = data["l2_range"]
                    self.fire_rate = data["l2_fire_rate"]
                elif self.tower_type == "alchemist":
                    self.damage = data["l2_damage"]
                    self.range = data["l2_range"]
                    self.fire_rate = data["l2_fire_rate"]
                    self.armor_shred = data["l2_armor_shred"]
                elif self.tower_type == "sun_shrine":
                    self.damage = data["l2_damage"]
                    self.range = data["l2_range"]
                    self.fire_rate = data["l2_fire_rate"]
                elif self.tower_type == "barracks":
                    for s in self.soldiers:
                        s.max_hp = data["l2_hp"]
                        s.hp = s.max_hp
                        s.damage = data["l2_damage"]
                        s.armor = data["l2_armor"]
                sound_manager.play("upgrade")
                return cost
        elif self.level == 2:
            cost = data["l3_upgrade_cost"]
            if player_gold >= cost:
                self.level = 3
                self.total_invested += cost
                if self.tower_type == "archer":
                    self.damage = data["l3_damage"]
                    self.range = data["l3_range"]
                    self.fire_rate = data["l3_fire_rate"]
                elif self.tower_type == "catapult":
                    self.damage = data["l3_damage"]
                    self.range = data["l3_range"]
                    self.splash_radius = data["l3_splash"]
                elif self.tower_type == "mage":
                    self.damage = data["l3_damage"]
                    self.range = data["l3_range"]
                    self.fire_rate = data["l3_fire_rate"]
                elif self.tower_type == "alchemist":
                    self.damage = data["l3_damage"]
                    self.range = data["l3_range"]
                    self.fire_rate = data["l3_fire_rate"]
                    self.armor_shred = data["l3_armor_shred"]
                elif self.tower_type == "sun_shrine":
                    self.damage = data["l3_damage"]
                    self.range = data["l3_range"]
                    self.fire_rate = data["l3_fire_rate"]
                elif self.tower_type == "barracks":
                    for s in self.soldiers:
                        s.max_hp = data["l3_hp"]
                        s.hp = s.max_hp
                        s.damage = data["l3_damage"]
                        s.armor = data["l3_armor"]
                sound_manager.play("upgrade")
                return cost
        return 0

    def upgrade_special(self, spec_key, player_gold):
        if self.level != 3 or self.specialization is not None:
            return 0
        data = TOWER_DATA[self.tower_type][spec_key]
        cost = data["cost"]
        if player_gold >= cost:
            self.specialization = spec_key
            self.total_invested += cost
            if self.tower_type == "archer":
                self.damage = data["damage"]
                self.range = data["range"]
                self.fire_rate = data["fire_rate"]
            elif self.tower_type == "catapult":
                self.damage = data["damage"]
                self.splash_radius = data["splash_radius"]
                self.fire_rate = data["fire_rate"]
            elif self.tower_type == "mage":
                self.damage = data["damage"]
                self.range = data["range"]
                self.fire_rate = data["fire_rate"]
            elif self.tower_type == "alchemist":
                self.damage = data["damage"]
                self.range = data["range"]
                self.fire_rate = data["fire_rate"]
                self.armor_shred = data.get("armor_shred", 0.60)
            elif self.tower_type == "sun_shrine":
                self.damage = data["damage"]
                self.range = data["range"]
                self.fire_rate = data["fire_rate"]
                if spec_key == "special_b":
                    self.buff_radius = data.get("buff_radius", 150)
            elif self.tower_type == "barracks":
                stype = "paladin" if spec_key == "special_a" else "barbarian"
                for s in self.soldiers:
                    s.soldier_type = stype
                    s.max_hp = data["hp"]
                    s.hp = s.max_hp
                    s.damage = data["damage"]
                    s.armor = data["armor"]
                    s.regen_per_sec = data.get("regen_per_sec", 0.0)
                    s.attack_rate = data.get("attack_speed", 1.0)
            sound_manager.play("upgrade")
            return cost
        return 0

    def sell_value(self):
        return int(self.total_invested * 0.70)

    def get_target(self, enemies):
        in_range = []
        for e in enemies:
            if not e.alive:
                continue
            dist = math.hypot(e.x - self.x, e.y - self.y)
            if self.min_range <= dist <= self.range:
                # Catapulta no puede atacar voladores
                if self.tower_type == "catapult" and e.is_flying:
                    continue
                in_range.append(e)

        if not in_range:
            return None

        if self.targeting_mode == "first":
            in_range.sort(key=lambda e: e.distance_traveled, reverse=True)
        elif self.targeting_mode == "last":
            in_range.sort(key=lambda e: e.distance_traveled)
        elif self.targeting_mode == "strongest":
            in_range.sort(key=lambda e: e.hp, reverse=True)
        elif self.targeting_mode == "weakest":
            in_range.sort(key=lambda e: e.hp)
        elif self.targeting_mode == "closest":
            in_range.sort(key=lambda e: math.hypot(e.x - self.x, e.y - self.y))

        return in_range[0]

    def update(self, dt, enemies, projectiles_list, particle_sys):
        self.animation_time += dt

        # Actualizar soldados si es cuartel
        if self.tower_type == "barracks":
            dead_count = sum(1 for s in self.soldiers if not s.alive)
            if dead_count > 0:
                self.respawn_timer += dt
                if self.respawn_timer >= TOWER_DATA["barracks"]["respawn_time"]:
                    self.respawn_timer = 0.0
                    for s in self.soldiers:
                        if not s.alive:
                            s.alive = True
                            s.hp = s.max_hp
                            s.x, s.y = self.x, self.y
                            break
            
            for s in self.soldiers:
                s.update(dt, enemies, particle_sys)
            return

        # Torres de ataque
        self.cooldown -= dt
        if self.cooldown <= 0:
            target = self.get_target(enemies)
            if target:
                self.cooldown = 1.0 / self.fire_rate
                self._fire_at(target, projectiles_list)

    def _fire_at(self, target, projectiles_list):
        if self.tower_type == "archer":
            sound_manager.play("bow_shoot")
            is_crit = False
            dmg = self.damage
            poison = None
            if self.specialization == "special_a":
                if random.random() < 0.35:
                    is_crit = True
                    dmg *= 2.5
            elif self.specialization == "special_b":
                poison = (8, 3.0)
            projectiles_list.append(Arrow(self.x, self.y - 16, target, dmg, self.damage_type, is_crit, poison))

        elif self.tower_type == "catapult":
            is_fire = (self.specialization == "special_a")
            is_stun = (self.specialization == "special_b")
            burn_info = (25, 4.0) if is_fire else None
            pred_x = target.x + (target.target_x - target.x) * 0.3
            pred_y = target.y + (target.target_y - target.y) * 0.3
            projectiles_list.append(CatapultRock(self.x, self.y - 12, pred_x, pred_y, self.damage, self.splash_radius, is_fire, is_stun, burn_info))

        elif self.tower_type == "mage":
            is_frost = (self.specialization == "special_a")
            is_chain = (self.specialization == "special_b")
            chain_count = 4 if is_chain else 0
            projectiles_list.append(MagicBolt(self.x, self.y - 20, target, self.damage, is_frost, is_chain, chain_count))

        elif self.tower_type == "alchemist":
            is_plag = (self.specialization == "special_a")
            is_acid = (self.specialization == "special_b")
            shred = getattr(self, "armor_shred", 0.20)
            projectiles_list.append(AlchemistPotion(self.x, self.y - 14, target, self.damage, shred, is_plague=is_plag, is_acid=is_acid))

        elif self.tower_type == "sun_shrine":
            is_div = (self.specialization == "special_a")
            projectiles_list.append(SunBeamEffect(self.x, self.y - 22, target, self.damage, is_divine=is_div))

    def draw(self, surface):
        # Dibujar torre
        sprite = gfx.get_tower_sprite(self.tower_type, self.level, self.specialization, self.animation_time)
        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(sprite, rect)

        # Si está seleccionada, dibujar círculo de alcance y bandera de rally
        if self.selected:
            # Círculo de rango
            range_surf = pygame.Surface((int(self.range * 2) + 4, int(self.range * 2) + 4), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (240, 210, 80, 45), (int(self.range) + 2, int(self.range) + 2), int(self.range))
            pygame.draw.circle(range_surf, (240, 210, 80, 160), (int(self.range) + 2, int(self.range) + 2), int(self.range), 2)
            surface.blit(range_surf, (self.x - self.range - 2, self.y - self.range - 2))

            # Si es cuartel, dibujar bandera de rally
            if self.tower_type == "barracks":
                pygame.draw.line(surface, COLOR_GOLD, (int(self.x), int(self.y)), (int(self.rally_x), int(self.rally_y)), 1)
                pygame.draw.circle(surface, COLOR_ROYAL_BLUE, (int(self.rally_x), int(self.rally_y)), 5)
                pygame.draw.circle(surface, COLOR_GOLD, (int(self.rally_x), int(self.rally_y)), 5, 1)

        # Dibujar soldados
        if self.tower_type == "barracks":
            for s in self.soldiers:
                s.draw(surface)
