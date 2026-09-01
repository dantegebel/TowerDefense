"""
Habilidades y Poderes Activos del Jugador para 'Reino en Asedio'.
"""

import math
import random
import pygame
from config import SPELL_DATA, COLOR_FIRE_ORANGE, COLOR_GOLD, COLOR_WHITE
from engine.audio import sound_manager
from entities.soldiers import Soldier

class ActiveRainOfArrows:
    def __init__(self, x, y, radius=95, arrow_count=30, damage_per_arrow=14):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.total_arrows = arrow_count
        self.damage_per_arrow = damage_per_arrow
        self.arrows_fired = 0
        self.fire_timer = 0.0
        self.alive = True
        self.visual_arrows = []

    def update(self, dt, enemies, particle_sys):
        self.fire_timer += dt
        
        # Disparar una flecha cada 0.03s
        while self.fire_timer >= 0.03 and self.arrows_fired < self.total_arrows:
            self.fire_timer -= 0.03
            self.arrows_fired += 1
            
            # Punto de impacto aleatorio dentro del círculo
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, self.radius)
            tx = self.x + math.cos(angle) * r
            ty = self.y + math.sin(angle) * r
            
            # Animación de flecha cayendo desde el cielo
            self.visual_arrows.append({'x': tx + 30, 'y': ty - 120, 'tx': tx, 'ty': ty, 'prog': 0.0})

        # Actualizar flechas visuales
        for arr in self.visual_arrows:
            arr['prog'] += dt * 6.0
            if arr['prog'] >= 1.0 and not arr.get('hit', False):
                arr['hit'] = True
                particle_sys.add_hit_spark(arr['tx'], arr['ty'], COLOR_WHITE, count=2)
                # Daño a enemigos cercanos
                for e in enemies:
                    if e.alive:
                        if math.hypot(e.x - arr['tx'], e.y - arr['ty']) <= 25:
                            dmg = e.take_damage(self.damage_per_arrow, "physical")
                            particle_sys.add_floating_damage(e.x, e.y, dmg, "physical")
                            break

        self.visual_arrows = [a for a in self.visual_arrows if a['prog'] < 1.1]

        if self.arrows_fired >= self.total_arrows and len(self.visual_arrows) == 0:
            self.alive = False

    def draw(self, surface):
        for arr in self.visual_arrows:
            prog = min(1.0, arr['prog'])
            cur_x = arr['x'] + (arr['tx'] - arr['x']) * prog
            cur_y = arr['y'] + (arr['ty'] - arr['y']) * prog
            pygame.draw.line(surface, COLOR_WHITE, (cur_x, cur_y), (cur_x - 4, cur_y - 14), 2)

class ActiveMeteor:
    def __init__(self, x, y, radius=110, damage=280, burn_dps=30, burn_duration=4.5):
        self.target_x = float(x)
        self.target_y = float(y)
        self.x = self.target_x + 120
        self.y = self.target_y - 250
        self.radius = radius
        self.damage = damage
        self.burn_dps = burn_dps
        self.burn_duration = burn_duration
        self.prog = 0.0
        self.alive = True

    def update(self, dt, enemies, particle_sys):
        self.prog += dt * 1.8
        self.x = (self.target_x + 120) + (self.target_x - (self.target_x + 120)) * self.prog
        self.y = (self.target_y - 250) + (self.target_y - (self.target_y - 250)) * self.prog

        # Estela de fuego
        particle_sys.add_hit_spark(self.x, self.y, COLOR_FIRE_ORANGE, count=3)

        if self.prog >= 1.0:
            self.alive = False
            sound_manager.play("explosion")
            particle_sys.add_explosion(self.target_x, self.target_y, self.radius)
            particle_sys.add_ground_effect(self.target_x, self.target_y, self.radius, 'fire', self.burn_duration, self.burn_dps)
            
            for e in enemies:
                if e.alive:
                    dist = math.hypot(e.x - self.target_x, e.y - self.target_y)
                    if dist <= self.radius:
                        dmg = e.take_damage(self.damage, "magic")
                        particle_sys.add_floating_damage(e.x, e.y, dmg, "magic")
                        e.apply_burn(self.burn_dps, self.burn_duration)

    def draw(self, surface):
        if not self.alive:
            return
        # Sombra proyectada en el suelo
        shadow_size = int(self.radius * 0.4 * self.prog)
        shadow_surf = pygame.Surface((shadow_size * 2 + 2, shadow_size + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, int(160 * self.prog)), (0, 0, shadow_size * 2, shadow_size))
        surface.blit(shadow_surf, (self.target_x - shadow_size, self.target_y - shadow_size // 2))

        # Esfera del meteoro en llamas
        pygame.draw.circle(surface, COLOR_FIRE_ORANGE, (int(self.x), int(self.y)), 16)
        pygame.draw.circle(surface, (255, 230, 80), (int(self.x), int(self.y)), 10)
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.x), int(self.y)), 5)

class SpellManager:
    def __init__(self):
        self.cooldowns = {
            "rain_of_arrows": 0.0,
            "reinforcements": 0.0,
            "meteor": 0.0
        }
        self.active_spells = []
        self.selected_spell = None

    def update(self, dt, enemies, particle_sys):
        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] = max(0.0, self.cooldowns[k] - dt)

        for sp in self.active_spells:
            sp.update(dt, enemies, particle_sys)
        self.active_spells = [sp for sp in self.active_spells if sp.alive]

    def is_ready(self, spell_key):
        return self.cooldowns.get(spell_key, 0.0) <= 0

    def get_progress(self, spell_key):
        max_cd = SPELL_DATA[spell_key]["cooldown"]
        cur_cd = self.cooldowns.get(spell_key, 0.0)
        return max(0.0, 1.0 - (cur_cd / max_cd))

    def cast(self, spell_key, x, y, soldiers_list, particle_sys):
        if not self.is_ready(spell_key):
            return False

        data = SPELL_DATA[spell_key]
        self.cooldowns[spell_key] = data["cooldown"]

        if spell_key == "rain_of_arrows":
            sound_manager.play(data["sound"])
            self.active_spells.append(ActiveRainOfArrows(x, y, data["radius"], data["arrow_count"], data["damage_per_arrow"]))

        elif spell_key == "reinforcements":
            sound_manager.play(data["sound"])
            particle_sys.add_magic_burst(x, y, COLOR_GOLD, count=10)
            for i in range(data["count"]):
                offset_x = (i - 0.5) * 25
                stats = {
                    "hp": data["hp"],
                    "damage": data["damage"],
                    "armor": data["armor"],
                    "duration": data["duration"]
                }
                s = Soldier(x + offset_x, y, x + offset_x, y, soldier_type="militia", stats=stats)
                soldiers_list.append(s)

        elif spell_key == "meteor":
            self.active_spells.append(ActiveMeteor(x, y, data["radius"], data["damage"], data["burn_dps"], data["burn_duration"]))

        self.selected_spell = None
        return True

    def draw(self, surface):
        for sp in self.active_spells:
            sp.draw(surface)
