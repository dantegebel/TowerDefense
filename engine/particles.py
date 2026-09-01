"""
Sistema de partículas y efectos visuales para 'Reino en Asedio'.
Maneja fuego, humo, chispas, runas arcanas, ondas de choque y números de daño flotantes.
"""

import math
import random
import pygame
from config import (
    COLOR_FIRE_ORANGE, COLOR_GOLD, COLOR_WHITE, COLOR_ICE_CYAN,
    COLOR_ARCANE_PURPLE, COLOR_ROYAL_RED
)

class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, decay_rate=1.0, shrink=True, gravity=0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.initial_size = size
        self.size = size
        self.life = float(life)
        self.max_life = float(life)
        self.decay_rate = decay_rate
        self.shrink = shrink
        self.gravity = gravity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= self.decay_rate * dt
        if self.shrink and self.max_life > 0:
            self.size = max(0.5, self.initial_size * (self.life / self.max_life))
        return self.life > 0

    def draw(self, surface):
        if self.size <= 0:
            return
        alpha = int(max(0, min(255, 255 * (self.life / self.max_life))))
        if len(self.color) == 4:
            r, g, b, _ = self.color
        else:
            r, g, b = self.color[:3]
        
        # Dibujar partícula con alpha suave
        s = pygame.Surface((int(self.size * 2) + 2, int(self.size * 2) + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, alpha), (int(self.size) + 1, int(self.size) + 1), int(self.size))
        surface.blit(s, (self.x - self.size - 1, self.y - self.size - 1))

class FloatingText:
    def __init__(self, x, y, text, color, font, size=18, life=0.9, vy=-40):
        self.x = float(x)
        self.y = float(y)
        self.text = str(text)
        self.color = color
        self.font = font
        self.life = life
        self.max_life = life
        self.vy = vy

    def update(self, dt):
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = int(max(0, min(255, 255 * (self.life / self.max_life))))
        # Sombra negra y texto
        surf_text = self.font.render(self.text, True, self.color)
        surf_shadow = self.font.render(self.text, True, (0, 0, 0))
        
        surf_text.set_alpha(alpha)
        surf_shadow.set_alpha(int(alpha * 0.8))
        
        surface.blit(surf_shadow, (self.x - surf_shadow.get_width() // 2 + 1, self.y + 1))
        surface.blit(surf_text, (self.x - surf_text.get_width() // 2, self.y))

class Shockwave:
    def __init__(self, x, y, max_radius, color, duration=0.4, width=3):
        self.x = float(x)
        self.y = float(y)
        self.max_radius = max_radius
        self.radius = 2.0
        self.color = color
        self.duration = duration
        self.time = 0.0
        self.width = width

    def update(self, dt):
        self.time += dt
        progress = self.time / self.duration
        self.radius = self.max_radius * progress
        return progress < 1.0

    def draw(self, surface):
        progress = self.time / self.duration
        alpha = int(255 * (1.0 - progress))
        if alpha <= 0 or self.radius <= 0:
            return
        r, g, b = self.color[:3]
        s = pygame.Surface((int(self.radius * 2) + 4, int(self.radius * 2) + 4), pygame.SRCALPHA)
        w = max(1, int(self.width * (1.0 - progress * 0.5)))
        pygame.draw.circle(s, (r, g, b, alpha), (int(self.radius) + 2, int(self.radius) + 2), int(self.radius), w)
        surface.blit(s, (self.x - self.radius - 2, self.y - self.radius - 2))

class GroundEffect:
    """Efecto persistente en el suelo (ej: charco de lava / fuego valyrio / hielo)"""
    def __init__(self, x, y, radius, effect_type, duration=4.0, dps=20):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.effect_type = effect_type # 'fire' or 'ice'
        self.duration = duration
        self.time_left = duration
        self.dps = dps
        self.tick_timer = 0.0

    def update(self, dt, enemies):
        self.time_left -= dt
        self.tick_timer += dt
        
        # Aplicar daño cada 0.25s
        if self.tick_timer >= 0.25:
            self.tick_timer = 0.0
            for enemy in enemies:
                if enemy.alive and not enemy.is_flying:
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    if math.hypot(dx, dy) <= self.radius:
                        if self.effect_type == 'fire':
                            enemy.take_damage(self.dps * 0.25, damage_type='magic', source="Fuego Valyrio")
                            enemy.apply_burn(self.dps, 2.0)
                        elif self.effect_type == 'ice':
                            enemy.apply_slow(0.45, 1.5)

        return self.time_left > 0

    def draw(self, surface):
        alpha = int(140 * min(1.0, self.time_left / 0.5))
        s = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        if self.effect_type == 'fire':
            # Capa exterior naranja / capa interior amarilla
            pygame.draw.circle(s, (240, 80, 20, int(alpha * 0.6)), (int(self.radius), int(self.radius)), int(self.radius))
            pygame.draw.circle(s, (255, 200, 40, int(alpha * 0.8)), (int(self.radius), int(self.radius)), int(self.radius * 0.6))
        else:
            pygame.draw.circle(s, (80, 200, 240, int(alpha * 0.5)), (int(self.radius), int(self.radius)), int(self.radius))
        surface.blit(s, (self.x - self.radius, self.y - self.radius))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        self.shockwaves = []
        self.ground_effects = []
        self.font = None

    def set_font(self, font):
        self.font = font

    def add_hit_spark(self, x, y, color=COLOR_WHITE, count=6):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 160)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.15, 0.35)
            size = random.uniform(2, 4)
            self.particles.append(Particle(x, y, vx, vy, color, size, life, gravity=60))

    def add_blood_splatter(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 120)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.2, 0.5)
            size = random.uniform(2, 4)
            self.particles.append(Particle(x, y, vx, vy, (170, 20, 30), size, life, gravity=90))

    def add_explosion(self, x, y, radius=50):
        # Onda de choque
        self.shockwaves.append(Shockwave(x, y, radius, (255, 180, 60), duration=0.35, width=4))
        # Partículas de fuego
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, radius * 3.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.25, 0.55)
            size = random.uniform(3, 7)
            col = random.choice([(255, 230, 80), (250, 110, 30), (210, 40, 20)])
            self.particles.append(Particle(x, y, vx, vy, col, size, life, gravity=-10))
        # Humo
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, radius * 1.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.5, 0.9)
            size = random.uniform(5, 11)
            self.particles.append(Particle(x, y, vx, vy, (80, 80, 85), size, life, gravity=-15))

    def add_magic_burst(self, x, y, color=COLOR_ARCANE_PURPLE, count=16):
        self.shockwaves.append(Shockwave(x, y, 35, color, duration=0.3, width=2))
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 140)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.2, 0.5)
            size = random.uniform(2, 5)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def add_floating_damage(self, x, y, amount, damage_type="physical", is_crit=False):
        if not self.font:
            return
        x_offset = random.uniform(-10, 10)
        y_offset = random.uniform(-10, 0)
        
        if is_crit:
            text = f"!{int(amount)}!"
            color = (255, 225, 50)
        elif damage_type == "magic":
            text = str(int(amount))
            color = (200, 120, 255)
        elif damage_type == "poison":
            text = str(int(amount))
            color = (90, 230, 80)
        elif damage_type == "burn":
            text = str(int(amount))
            color = (255, 120, 40)
        else:
            text = str(int(amount))
            color = COLOR_WHITE
            
        self.floating_texts.append(FloatingText(x + x_offset, y + y_offset, text, color, self.font))

    def add_floating_gold(self, x, y, amount):
        if not self.font:
            return
        text = f"+{amount} 🪙"
        self.floating_texts.append(FloatingText(x, y - 10, text, COLOR_GOLD, self.font, life=1.1, vy=-35))

    def add_ground_effect(self, x, y, radius, effect_type, duration=4.0, dps=20):
        self.ground_effects.append(GroundEffect(x, y, radius, effect_type, duration, dps))

    def update(self, dt, enemies):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [t for t in self.floating_texts if t.update(dt)]
        self.shockwaves = [s for s in self.shockwaves if s.update(dt)]
        self.ground_effects = [g for g in self.ground_effects if g.update(dt, enemies)]

    def draw_ground(self, surface):
        """Dibuja efectos en el suelo por debajo de las entidades."""
        for g in self.ground_effects:
            g.draw(surface)

    def draw_top(self, surface):
        """Dibuja partículas y textos por encima de las entidades."""
        for s in self.shockwaves:
            s.draw(surface)
        for p in self.particles:
            p.draw(surface)
        for t in self.floating_texts:
            t.draw(surface)
