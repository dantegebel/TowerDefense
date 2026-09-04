"""
Entidades de Enemigos y Lógica de Hordas para 'Reino en Asedio'.
"""

import math
import pygame
from config import ENEMY_DATA, COLOR_HEALTH_GREEN, COLOR_HEALTH_BG, COLOR_ICE_CYAN, COLOR_FIRE_ORANGE
from engine.graphics import gfx
from engine.audio import sound_manager

class Enemy:
    def __init__(self, enemy_type, path, wave_mult=1.0):
        self.enemy_type = enemy_type
        self.data = ENEMY_DATA[enemy_type]
        self.path = path # Lista de puntos [(x, y), ...]
        self.path_index = 0
        
        # Posición inicial
        self.x = float(path[0][0])
        self.y = float(path[0][1])
        self.target_x = float(path[1][0]) if len(path) > 1 else self.x
        self.target_y = float(path[1][1]) if len(path) > 1 else self.y
        
        # Estadísticas escaladas por oleada
        self.max_hp = float(self.data["hp"] * wave_mult)
        self.hp = self.max_hp
        self.base_speed = float(self.data["speed"])
        self.speed = self.base_speed
        self.armor = float(self.data.get("armor", 0.0))
        self.magic_resist = float(self.data.get("magic_resist", 0.0))
        self.gold_reward = int(self.data["gold_reward"])
        self.damage_to_base = int(self.data.get("damage_to_base", 1))
        self.attack_damage = float(self.data.get("attack_damage", 10))
        self.attack_rate = float(self.data.get("attack_rate", 1.0))
        self.attack_cooldown = 0.0
        self.size = self.data.get("size", 20)
        self.is_boss = self.data.get("is_boss", False)
        self.is_flying = self.data.get("is_flying", False)
        self.slow_immune = self.data.get("slow_immune", False)
        self.regen_per_sec = float(self.data.get("regen_per_sec", 0.0))
        
        # Estados
        self.alive = True
        self.reached_end = False
        self.distance_traveled = 0.0
        self.walk_cycle = 0.0
        self.facing_right = True
        
        # Estados alterados (Debuffs)
        self.slow_timer = 0.0
        self.slow_factor = 1.0
        self.burn_timer = 0.0
        self.burn_dps = 0.0
        self.poison_timer = 0.0
        self.poison_dps = 0.0
        self.stun_timer = 0.0
        
        # Combate cuerpo a cuerpo
        self.engaged_soldier = None
        
        # Habilidades especiales (ej: Nigromante)
        self.summon_timer = self.data.get("summon_cooldown", 0.0)

    def take_damage(self, amount, damage_type="physical", source="", is_crit=False):
        if not self.alive:
            return 0
        
        actual_damage = amount
        if damage_type == "physical":
            actual_damage = max(1.0, amount * (1.0 - self.armor))
        elif damage_type == "magic":
            actual_damage = max(1.0, amount * (1.0 - self.magic_resist))
        
        self.hp -= actual_damage
        
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            
        return actual_damage

    def apply_slow(self, amount, duration):
        if self.slow_immune:
            return
        self.slow_factor = min(self.slow_factor, 1.0 - amount)
        self.slow_timer = max(self.slow_timer, duration)

    def apply_burn(self, dps, duration):
        self.burn_dps = max(self.burn_dps, dps)
        self.burn_timer = max(self.burn_timer, duration)

    def apply_poison(self, dps, duration):
        self.poison_dps = max(self.poison_dps, dps)
        self.poison_timer = max(self.poison_timer, duration)

    def apply_stun(self, duration):
        if self.slow_immune or self.is_boss:
            return
        self.stun_timer = max(self.stun_timer, duration)

    def update(self, dt, particle_sys, spawned_enemies_list):
        if not self.alive:
            return

        # 1. Actualizar DoTs (Daño periódico)
        if self.burn_timer > 0:
            self.burn_timer -= dt
            tick_dmg = self.burn_dps * dt
            self.take_damage(tick_dmg, damage_type="burn")
            if random_particle := (self.burn_timer > 0 and dt > 0 and int(self.burn_timer * 15) % 3 == 0):
                particle_sys.add_hit_spark(self.x, self.y, COLOR_FIRE_ORANGE, count=2)

        if self.poison_timer > 0:
            self.poison_timer -= dt
            tick_dmg = self.poison_dps * dt
            self.take_damage(tick_dmg, damage_type="poison")

        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        # Regeneración pasiva de vida
        if self.regen_per_sec > 0 and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.regen_per_sec * dt)

        if self.stun_timer > 0:
            self.stun_timer -= dt
            return # Aturdido: no se mueve ni ataca

        # 2. Habilidad de Invocación (Nigromante)
        if self.enemy_type == "necromancer" and self.summon_timer > 0:
            self.summon_timer -= dt
            if self.summon_timer <= 0:
                self.summon_timer = self.data.get("summon_cooldown", 6.0)
                # Invocar 2 esqueletos en su posición
                sound_manager.play("magic")
                particle_sys.add_magic_burst(self.x, self.y, (80, 240, 80), count=12)
                for _ in range(2):
                    skel = Enemy("skeleton", self.path)
                    skel.path_index = self.path_index
                    skel.x = self.x + math.sin(skel.path_index) * 10
                    skel.y = self.y + math.cos(skel.path_index) * 10
                    skel.target_x = self.target_x
                    skel.target_y = self.target_y
                    skel.distance_traveled = self.distance_traveled
                    spawned_enemies_list.append(skel)

        # 3. Combate cuerpo a cuerpo si está bloqueado por un soldado
        if self.engaged_soldier and self.engaged_soldier.alive:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 1.0 / self.attack_rate
                soldier = self.engaged_soldier
                sx, sy = soldier.x, soldier.y
                soldier.take_damage(self.attack_damage)
                sound_manager.play("sword_hit")
                particle_sys.add_hit_spark(sx, sy, count=3)
                if not soldier.alive:
                    self.engaged_soldier = None
            return # Se queda quieto peleando

        self.engaged_soldier = None

        # 4. Movimiento a través de la ruta
        if self.path_index < len(self.path) - 1:
            target = self.path[self.path_index + 1]
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.hypot(dx, dy)
            
            cur_speed = self.base_speed * self.slow_factor
            step = cur_speed * dt

            if dist <= step:
                self.x, self.y = target[0], target[1]
                self.path_index += 1
                self.distance_traveled += dist
                if self.path_index >= len(self.path) - 1:
                    self.reached_end = True
                    self.alive = False
            else:
                self.x += (dx / dist) * step
                self.y += (dy / dist) * step
                self.distance_traveled += step
                self.facing_right = (dx >= 0)

            self.walk_cycle += dt * (cur_speed / 40.0)

    def draw(self, surface):
        if not self.alive:
            return

        # Sprite del enemigo
        sprite = gfx.get_enemy_sprite(self.enemy_type, walk_cycle=self.walk_cycle)
        if not self.facing_right and not self.is_boss:
            sprite = pygame.transform.flip(sprite, True, False)
        
        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(sprite, rect)

        # Indicador de estado alterado (Hielo o Fuego)
        if self.slow_timer > 0:
            pygame.draw.circle(surface, COLOR_ICE_CYAN, (int(self.x), int(self.y + self.size//2)), 4)
        if self.burn_timer > 0:
            pygame.draw.circle(surface, COLOR_FIRE_ORANGE, (int(self.x), int(self.y - self.size//2 - 2)), 3)

        # Barra de Vida (Health Bar)
        bar_w = 28 if not self.is_boss else 60
        bar_h = 4 if not self.is_boss else 6
        bar_x = int(self.x - bar_w // 2)
        bar_y = int(self.y - self.size // 2 - 8)

        hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        
        # Fondo rojo y barra verde
        pygame.draw.rect(surface, COLOR_HEALTH_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        pygame.draw.rect(surface, COLOR_HEALTH_GREEN, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h), border_radius=2)
        pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=2)
