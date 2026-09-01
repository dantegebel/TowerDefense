"""
Soldados y Tropas Aliadas de Barracones / Refuerzos para 'Reino en Asedio'.
"""

import math
import pygame
from config import COLOR_HEALTH_GREEN, COLOR_HEALTH_BG
from engine.graphics import gfx
from engine.audio import sound_manager

class Soldier:
    def __init__(self, x, y, rally_x, rally_y, soldier_type="militia", stats=None, parent_tower=None):
        self.x = float(x)
        self.y = float(y)
        self.rally_x = float(rally_x)
        self.rally_y = float(rally_y)
        self.soldier_type = soldier_type
        self.parent_tower = parent_tower
        
        # Estadísticas
        stats = stats or {}
        self.max_hp = float(stats.get("hp", 90))
        self.hp = self.max_hp
        self.damage = float(stats.get("damage", 10))
        self.armor = float(stats.get("armor", 0.20))
        self.speed = 60.0
        self.attack_rate = float(stats.get("attack_speed", 1.0))
        self.regen_per_sec = float(stats.get("regen_per_sec", 0.0))
        
        self.attack_cooldown = 0.0
        self.alive = True
        self.engaged_enemy = None
        self.walk_cycle = 0.0
        self.facing_right = True
        self.is_attacking = False
        self.duration = stats.get("duration", None) # Para refuerzos temporales

    def take_damage(self, amount):
        if not self.alive:
            return
        actual_damage = max(1.0, amount * (1.0 - self.armor))
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            if self.engaged_enemy:
                self.engaged_enemy.engaged_soldier = None
                self.engaged_enemy = None

    def set_rally_point(self, rx, ry):
        self.rally_x = float(rx)
        self.rally_y = float(ry)
        if self.engaged_enemy:
            self.engaged_enemy.engaged_soldier = None
            self.engaged_enemy = None

    def update(self, dt, enemies, particle_sys):
        if not self.alive:
            return

        # Refuerzos temporales (desvanecimiento)
        if self.duration is not None:
            self.duration -= dt
            if self.duration <= 0:
                self.alive = False
                if self.engaged_enemy:
                    self.engaged_enemy.engaged_soldier = None
                return

        # Regeneración (Paladines)
        if self.regen_per_sec > 0 and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.regen_per_sec * dt)

        # Si está combatiendo a un enemigo
        if self.engaged_enemy and self.engaged_enemy.alive:
            self.is_attacking = True
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 1.0 / self.attack_rate
                target = self.engaged_enemy
                ex, ey = target.x, target.y
                dmg_dealt = target.take_damage(self.damage, damage_type="physical", source="Soldado")
                sound_manager.play("sword_hit")
                particle_sys.add_blood_splatter(ex, ey, count=4)
                particle_sys.add_floating_damage(ex, ey, dmg_dealt, "physical")
                if not target.alive:
                    self.engaged_enemy = None
            return

        self.engaged_enemy = None
        self.is_attacking = False

        # Buscar enemigos cercanos en el camino para bloquear (Rango de intercepción ~35px)
        for enemy in enemies:
            if enemy.alive and not enemy.is_flying and enemy.engaged_soldier is None:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                dist = math.hypot(dx, dy)
                if dist <= 38:
                    self.engaged_enemy = enemy
                    enemy.engaged_soldier = self
                    return

        # Si no hay combate, moverse al punto de reunión (Rally Point)
        dx = self.rally_x - self.x
        dy = self.rally_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 3:
            step = min(dist, self.speed * dt)
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            self.walk_cycle += dt * 3.0
            self.facing_right = (dx >= 0)

    def draw(self, surface):
        if not self.alive:
            return

        sprite = gfx.get_soldier_sprite(self.soldier_type, walk_cycle=self.walk_cycle, attacking=self.is_attacking)
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
            
        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(sprite, rect)

        # Barra de vida
        if self.hp < self.max_hp or self.duration is not None:
            bar_w = 22
            bar_h = 3
            bar_x = int(self.x - bar_w // 2)
            bar_y = int(self.y - 18)
            hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
            
            pygame.draw.rect(surface, COLOR_HEALTH_BG, (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, COLOR_HEALTH_GREEN, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
            pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h), 1)
