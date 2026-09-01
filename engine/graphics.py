"""
Generador y Renderizador de Gráficos Procedurales Medievales para 'Reino en Asedio'.
Produce texturas, sprites, iconos, animaciones y elementos de interfaz con temática medieval estilizada.
"""

import math
import pygame
from config import (
    COLOR_GRASS_BASE, COLOR_GRASS_LIGHT, COLOR_GRASS_DARK,
    COLOR_ROAD, COLOR_ROAD_BORDER, COLOR_ROAD_STONE,
    COLOR_WOOD_DARK, COLOR_WOOD_MID, COLOR_WOOD_LIGHT,
    COLOR_STONE_DARK, COLOR_STONE_MID, COLOR_STONE_LIGHT,
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK,
    COLOR_ROYAL_RED, COLOR_ROYAL_BLUE, COLOR_ARCANE_PURPLE,
    COLOR_ICE_CYAN, COLOR_FIRE_ORANGE, COLOR_WHITE, COLOR_BLACK,
    COLOR_HEALTH_GREEN, COLOR_HEALTH_BG
)

class GraphicsEngine:
    def __init__(self):
        self.cached_sprites = {}

    def draw_stone_brick(self, surf, rect, border_col=COLOR_STONE_DARK, fill_col=COLOR_STONE_MID, light_col=COLOR_STONE_LIGHT):
        pygame.draw.rect(surf, fill_col, rect)
        pygame.draw.rect(surf, border_col, rect, 1)
        # Highlight top/left
        pygame.draw.line(surf, light_col, (rect[0] + 1, rect[1] + 1), (rect[0] + rect[2] - 2, rect[1] + 1))
        pygame.draw.line(surf, light_col, (rect[0] + 1, rect[1] + 1), (rect[0] + 1, rect[1] + rect[3] - 2))

    def draw_wood_plank(self, surf, rect, border_col=COLOR_WOOD_DARK, fill_col=COLOR_WOOD_MID, light_col=COLOR_WOOD_LIGHT):
        pygame.draw.rect(surf, fill_col, rect)
        pygame.draw.rect(surf, border_col, rect, 1)
        pygame.draw.line(surf, light_col, (rect[0] + 1, rect[1] + 1), (rect[0] + rect[2] - 2, rect[1] + 1))

    # ------------------ RENDERIZADO DE TORRES ------------------

    def get_tower_sprite(self, tower_type, level, specialization=None, animation_time=0.0):
        key = f"tower_{tower_type}_{level}_{specialization}_{int(animation_time * 10) % 10}"
        if key in self.cached_sprites:
            return self.cached_sprites[key]

        size = 64
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Base común de piedra / pedestal
        base_w, base_h = 44, 20
        self.draw_stone_brick(surf, (cx - base_w//2, cy + 10, base_w, base_h))
        # Gradas
        self.draw_stone_brick(surf, (cx - base_w//2 + 4, cy + 4, base_w - 8, 10))

        if tower_type == "archer":
            # Estructura de madera / piedra según nivel
            pillar_col = COLOR_STONE_MID if level >= 2 else COLOR_WOOD_MID
            border_col = COLOR_STONE_DARK if level >= 2 else COLOR_WOOD_DARK
            
            # Postes de soporte
            self.draw_wood_plank(surf, (cx - 16, cy - 14, 6, 22), border_col, pillar_col)
            self.draw_wood_plank(surf, (cx + 10, cy - 14, 6, 22), border_col, pillar_col)
            # Plataforma superior
            self.draw_wood_plank(surf, (cx - 20, cy - 16, 40, 7))
            
            if specialization == "special_a": # Ballesta pesada
                # Balista de acero y madera
                pygame.draw.rect(surf, COLOR_STONE_LIGHT, (cx - 14, cy - 26, 28, 6), border_radius=2)
                pygame.draw.arc(surf, COLOR_GOLD, (cx - 18, cy - 32, 36, 16), math.pi*0.1, math.pi*0.9, 3)
                pygame.draw.line(surf, COLOR_GOLD_LIGHT, (cx, cy - 30), (cx, cy - 18), 3)
            elif specialization == "special_b": # Tiradores élficos
                # Tejado cónico élfico verde y dorado
                points = [(cx, cy - 34), (cx - 20, cy - 16), (cx + 20, cy - 16)]
                pygame.draw.polygon(surf, (40, 140, 70), points)
                pygame.draw.polygon(surf, COLOR_GOLD, points, 2)
                # Gema esmeralda
                pygame.draw.circle(surf, (80, 240, 140), (cx, cy - 24), 3)
            else:
                # Techo cónico medieval
                roof_col = COLOR_ROYAL_RED if level >= 2 else COLOR_WOOD_LIGHT
                points = [(cx, cy - 30), (cx - 18, cy - 16), (cx + 18, cy - 16)]
                pygame.draw.polygon(surf, roof_col, points)
                pygame.draw.polygon(surf, COLOR_WOOD_DARK, points, 2)
                # Arquero silueta
                pygame.draw.circle(surf, (220, 180, 140), (cx, cy - 20), 4) # Cabeza
                pygame.draw.line(surf, COLOR_WOOD_DARK, (cx + 2, cy - 24), (cx + 8, cy - 18), 2) # Arco

        elif tower_type == "catapult":
            # Base pesada de vigas
            self.draw_wood_plank(surf, (cx - 18, cy - 4, 36, 10))
            # Brazo de lanzamiento
            bob = math.sin(animation_time * 4) * 2
            pygame.draw.line(surf, COLOR_WOOD_DARK, (cx - 12, cy + 4), (cx + 12, cy - 18 + int(bob)), 5)
            # Cazoleta con roca
            if specialization == "special_a": # Fuego Valyrio
                rock_col = COLOR_FIRE_ORANGE
                pygame.draw.circle(surf, (255, 200, 50), (cx + 14, cy - 20 + int(bob)), 6)
            else:
                rock_col = COLOR_STONE_DARK
            pygame.draw.circle(surf, rock_col, (cx + 13, cy - 19 + int(bob)), 5)
            # Contrapeso
            pygame.draw.rect(surf, COLOR_STONE_MID, (cx - 16, cy - 2, 8, 8))

        elif tower_type == "mage":
            # Torre cónica de piedra arcana
            self.draw_stone_brick(surf, (cx - 14, cy - 16, 28, 22), COLOR_STONE_DARK, (70, 60, 95), (110, 95, 145))
            # Almenas mágicas
            pygame.draw.rect(surf, (90, 75, 120), (cx - 16, cy - 20, 32, 6))
            # Orbe flotante con brillo
            float_y = cy - 28 + math.sin(animation_time * 5) * 3
            if specialization == "special_a": # Hielo
                orb_col = COLOR_ICE_CYAN
                glow_col = (180, 240, 255)
            elif specialization == "special_b": # Rayos
                orb_col = (255, 230, 80)
                glow_col = (255, 255, 180)
            else:
                orb_col = COLOR_ARCANE_PURPLE
                glow_col = (220, 160, 255)
                
            pygame.draw.circle(surf, glow_col, (cx, int(float_y)), 7)
            pygame.draw.circle(surf, orb_col, (cx, int(float_y)), 4)
            # Anillo de energía rotatorio
            angle = animation_time * 3
            rx, ry = math.cos(angle) * 11, math.sin(angle) * 3
            pygame.draw.circle(surf, glow_col, (cx + int(rx), int(float_y + ry)), 2)

        elif tower_type == "barracks":
            # Fuerte de guarnición con puerta arqueada
            self.draw_stone_brick(surf, (cx - 20, cy - 14, 40, 24))
            # Puerta de madera con arco
            pygame.draw.rect(surf, COLOR_WOOD_DARK, (cx - 7, cy - 4, 14, 14), border_radius=4)
            # Tejado almenado
            pygame.draw.rect(surf, COLOR_STONE_LIGHT, (cx - 22, cy - 18, 44, 5))
            for i in range(5):
                pygame.draw.rect(surf, COLOR_STONE_LIGHT, (cx - 20 + i * 9, cy - 22, 6, 5))
            # Escudo de armas heráldico en la fachada
            if specialization == "special_a": # Paladines
                pygame.draw.circle(surf, COLOR_GOLD, (cx, cy - 10), 5)
                pygame.draw.line(surf, COLOR_WHITE, (cx - 3, cy - 10), (cx + 3, cy - 10), 2)
                pygame.draw.line(surf, COLOR_WHITE, (cx, cy - 13), (cx, cy - 7), 2)
            else:
                # Estandarte Real Azul
                pygame.draw.rect(surf, COLOR_ROYAL_BLUE, (cx - 4, cy - 12, 8, 7))
                pygame.draw.line(surf, COLOR_GOLD, (cx - 4, cy - 12), (cx + 4, cy - 12), 2)

        self.cached_sprites[key] = surf
        return surf

    # ------------------ RENDERIZADO DE ENEMIGOS ------------------

    def get_enemy_sprite(self, enemy_type, frame_idx=0, walk_cycle=0.0):
        key = f"enemy_{enemy_type}_{int(walk_cycle * 8) % 4}"
        if key in self.cached_sprites:
            return self.cached_sprites[key]

        size = 48
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        bob = int(math.sin(walk_cycle * math.pi * 2) * 2)

        if enemy_type == "goblin":
            # Cuerpo pequeño verde
            pygame.draw.circle(surf, (90, 160, 40), (cx, cy - 2 + bob), 7) # Cabeza
            # Orejas puntiagudas
            pygame.draw.polygon(surf, (90, 160, 40), [(cx - 6, cy - 3 + bob), (cx - 12, cy - 6 + bob), (cx - 5, cy + bob)])
            pygame.draw.polygon(surf, (90, 160, 40), [(cx + 6, cy - 3 + bob), (cx + 12, cy - 6 + bob), (cx + 5, cy + bob)])
            # Ojos rojos
            pygame.draw.circle(surf, (220, 30, 30), (cx - 2, cy - 3 + bob), 1.5)
            pygame.draw.circle(surf, (220, 30, 30), (cx + 2, cy - 3 + bob), 1.5)
            # Túnica marrón y daga
            pygame.draw.rect(surf, COLOR_WOOD_MID, (cx - 5, cy + 4 + bob, 10, 8), border_radius=2)
            pygame.draw.line(surf, COLOR_STONE_LIGHT, (cx + 6, cy + 4 + bob), (cx + 11, cy + 1 + bob), 2)

        elif enemy_type == "skeleton":
            # Calavera blanca
            pygame.draw.circle(surf, (230, 230, 225), (cx, cy - 3 + bob), 7)
            # Ojos oscuros
            pygame.draw.circle(surf, (20, 20, 20), (cx - 2, cy - 3 + bob), 2)
            pygame.draw.circle(surf, (20, 20, 20), (cx + 2, cy - 3 + bob), 2)
            # Costillas / Columna
            pygame.draw.line(surf, (210, 210, 205), (cx, cy + 4 + bob), (cx, cy + 12 + bob), 3)
            pygame.draw.line(surf, (210, 210, 205), (cx - 5, cy + 6 + bob), (cx + 5, cy + 6 + bob), 2)
            pygame.draw.line(surf, (210, 210, 205), (cx - 4, cy + 9 + bob), (cx + 4, cy + 9 + bob), 2)
            # Espada oxidada
            pygame.draw.line(surf, (150, 130, 120), (cx + 5, cy + 12 + bob), (cx + 10, cy - 2 + bob), 2)

        elif enemy_type == "orc":
            # Cuerpo voluminoso
            pygame.draw.circle(surf, (130, 65, 45), (cx, cy - 4 + bob), 9) # Cabeza
            # Colmillos
            pygame.draw.polygon(surf, COLOR_WHITE, [(cx - 4, cy - 1 + bob), (cx - 2, cy - 4 + bob), (cx - 3, cy + 1 + bob)])
            pygame.draw.polygon(surf, COLOR_WHITE, [(cx + 4, cy - 1 + bob), (cx + 2, cy - 4 + bob), (cx + 3, cy + 1 + bob)])
            # Ojos furiosos
            pygame.draw.circle(surf, (255, 200, 40), (cx - 3, cy - 4 + bob), 2)
            pygame.draw.circle(surf, (255, 200, 40), (cx + 3, cy - 4 + bob), 2)
            # Hombreras con pinchos
            pygame.draw.rect(surf, COLOR_STONE_DARK, (cx - 10, cy + 4 + bob, 20, 10), border_radius=3)
            # Hacha gigante
            pygame.draw.line(surf, COLOR_WOOD_MID, (cx + 7, cy + 14 + bob), (cx + 13, cy - 8 + bob), 3)
            pygame.draw.polygon(surf, COLOR_STONE_LIGHT, [(cx + 11, cy - 6 + bob), (cx + 18, cy - 12 + bob), (cx + 14, cy + 2 + bob)])

        elif enemy_type == "dark_knight":
            # Armadura negra gótica completa
            pygame.draw.circle(surf, (40, 42, 50), (cx, cy - 4 + bob), 8) # Yelmo
            # Visera con rendija roja brillante
            pygame.draw.line(surf, (255, 30, 30), (cx - 4, cy - 4 + bob), (cx + 4, cy - 4 + bob), 2)
            # Cuernos en el yelmo
            pygame.draw.line(surf, COLOR_STONE_MID, (cx - 6, cy - 8 + bob), (cx - 11, cy - 14 + bob), 3)
            pygame.draw.line(surf, COLOR_STONE_MID, (cx + 6, cy - 8 + bob), (cx + 11, cy - 14 + bob), 3)
            # Coraza y capa
            pygame.draw.rect(surf, (30, 32, 40), (cx - 9, cy + 3 + bob, 18, 12), border_radius=2)
            pygame.draw.polygon(surf, (120, 15, 25), [(cx - 9, cy + 5 + bob), (cx - 13, cy + 16 + bob), (cx - 5, cy + 16 + bob)])
            # Escudo de torre
            pygame.draw.rect(surf, COLOR_STONE_MID, (cx - 13, cy - 1 + bob, 6, 14), border_radius=2)

        elif enemy_type == "necromancer":
            # Túnica con capucha morada
            points = [(cx, cy - 12 + bob), (cx - 8, cy + 12 + bob), (cx + 8, cy + 12 + bob)]
            pygame.draw.polygon(surf, (80, 25, 110), points)
            # Rostro sombrío con ojos verdes nigrománticos
            pygame.draw.circle(surf, (20, 10, 30), (cx, cy - 3 + bob), 5)
            pygame.draw.circle(surf, (60, 240, 80), (cx - 2, cy - 3 + bob), 2)
            pygame.draw.circle(surf, (60, 240, 80), (cx + 2, cy - 3 + bob), 2)
            # Báculo de calavera
            pygame.draw.line(surf, COLOR_WOOD_DARK, (cx + 8, cy + 14 + bob), (cx + 10, cy - 10 + bob), 2)
            pygame.draw.circle(surf, (60, 240, 80), (cx + 10, cy - 11 + bob), 3)

        elif enemy_type == "golem":
            # Coloso de piedra agrietada
            pygame.draw.circle(surf, (95, 100, 110), (cx, cy - 6 + bob), 12)
            pygame.draw.rect(surf, (80, 85, 95), (cx - 14, cy + 2 + bob, 28, 16), border_radius=4)
            # Runas luminosas en el pecho
            pygame.draw.line(surf, COLOR_ICE_CYAN, (cx - 5, cy + 6 + bob), (cx + 5, cy + 6 + bob), 3)
            pygame.draw.line(surf, COLOR_ICE_CYAN, (cx, cy + 3 + bob), (cx, cy + 12 + bob), 3)
            # Ojos brillantes
            pygame.draw.circle(surf, COLOR_ICE_CYAN, (cx - 4, cy - 6 + bob), 2)
            pygame.draw.circle(surf, COLOR_ICE_CYAN, (cx + 4, cy - 6 + bob), 2)

        elif enemy_type == "dragon_boss":
            # Dragón con alas batientes
            wing_flap = math.sin(walk_cycle * math.pi * 3) * 8
            # Alas
            wing_l = [(cx - 6, cy), (cx - 22, cy - 16 + int(wing_flap)), (cx - 8, cy + 8)]
            wing_r = [(cx + 6, cy), (cx + 22, cy - 16 + int(wing_flap)), (cx + 8, cy + 8)]
            pygame.draw.polygon(surf, (150, 20, 20), wing_l)
            pygame.draw.polygon(surf, (150, 20, 20), wing_r)
            pygame.draw.polygon(surf, COLOR_GOLD, wing_l, 1)
            pygame.draw.polygon(surf, COLOR_GOLD, wing_r, 1)
            # Cuerpo y cola
            pygame.draw.ellipse(surf, (190, 30, 30), (cx - 9, cy - 6, 18, 20))
            pygame.draw.line(surf, (190, 30, 30), (cx, cy + 10), (cx + int(math.sin(walk_cycle*4)*6), cy + 20), 4)
            # Cabeza draconiana y cuernos dorados
            pygame.draw.polygon(surf, (220, 40, 40), [(cx, cy - 18), (cx - 7, cy - 8), (cx + 7, cy - 8)])
            pygame.draw.line(surf, COLOR_GOLD, (cx - 4, cy - 14), (cx - 10, cy - 22), 3)
            pygame.draw.line(surf, COLOR_GOLD, (cx + 4, cy - 14), (cx + 10, cy - 22), 3)
            # Ojos dorados y aliento de fuego
            pygame.draw.circle(surf, (255, 220, 40), (cx - 3, cy - 12), 2)
            pygame.draw.circle(surf, (255, 220, 40), (cx + 3, cy - 12), 2)

        self.cached_sprites[key] = surf
        return surf

    # ------------------ RENDERIZADO DE SOLDADOS ------------------

    def get_soldier_sprite(self, soldier_type="militia", walk_cycle=0.0, attacking=False):
        key = f"soldier_{soldier_type}_{int(walk_cycle * 8) % 4}_{attacking}"
        if key in self.cached_sprites:
            return self.cached_sprites[key]

        size = 36
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        bob = int(math.sin(walk_cycle * math.pi * 2) * 2)
        atk_offset = 4 if attacking else 0

        if soldier_type == "paladin":
            # Armadura brillante y dorada
            pygame.draw.circle(surf, COLOR_GOLD_LIGHT, (cx, cy - 4 + bob), 5) # Yelmo
            pygame.draw.rect(surf, COLOR_WHITE, (cx - 6, cy + 1 + bob, 12, 10), border_radius=2)
            # Escudo de paladín con cruz
            pygame.draw.rect(surf, COLOR_ROYAL_BLUE, (cx - 10, cy - 2 + bob, 6, 10), border_radius=2)
            pygame.draw.line(surf, COLOR_GOLD, (cx - 10, cy + 3 + bob), (cx - 5, cy + 3 + bob), 2)
            # Martillo de guerra sagrado
            pygame.draw.line(surf, COLOR_WOOD_MID, (cx + 4, cy + 8 + bob), (cx + 9 + atk_offset, cy - 6 + bob), 3)
            pygame.draw.rect(surf, COLOR_GOLD, (cx + 7 + atk_offset, cy - 8 + bob, 6, 5))
        elif soldier_type == "barbarian":
            # Doble hacha y aspecto salvaje
            pygame.draw.circle(surf, (210, 160, 130), (cx, cy - 4 + bob), 5)
            pygame.draw.rect(surf, (140, 70, 40), (cx - 5, cy + 1 + bob, 10, 9))
            # Dos hachas
            pygame.draw.line(surf, COLOR_WOOD_MID, (cx - 7, cy + 6 + bob), (cx - 11, cy - 2 + bob), 2)
            pygame.draw.line(surf, COLOR_WOOD_MID, (cx + 7, cy + 6 + bob), (cx + 11 + atk_offset, cy - 2 + bob), 2)
        else: # Milicia / Guardia estándar
            # Cota de malla y túnica azul real
            pygame.draw.circle(surf, COLOR_STONE_LIGHT, (cx, cy - 4 + bob), 5) # Yelmo
            pygame.draw.rect(surf, COLOR_ROYAL_BLUE, (cx - 5, cy + 1 + bob, 10, 9), border_radius=2)
            # Escudo redondo de madera/hierro
            pygame.draw.circle(surf, COLOR_STONE_MID, (cx - 7, cy + 4 + bob), 5)
            pygame.draw.circle(surf, COLOR_ROYAL_BLUE, (cx - 7, cy + 4 + bob), 3)
            # Espada de acero
            pygame.draw.line(surf, COLOR_WHITE, (cx + 5, cy + 7 + bob), (cx + 10 + atk_offset, cy - 3 + bob), 2)

        self.cached_sprites[key] = surf
        return surf

    # ------------------ RENDERIZADO DEL CASTILLO / BASE ------------------

    def get_castle_sprite(self):
        if "castle" in self.cached_sprites:
            return self.cached_sprites["castle"]

        w, h = 90, 80
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # Muros del castillo
        self.draw_stone_brick(surf, (cx - 36, 20, 72, 56), COLOR_STONE_DARK, COLOR_STONE_MID, COLOR_STONE_LIGHT)
        # Torres laterales con almenas
        self.draw_stone_brick(surf, (cx - 42, 8, 20, 68))
        self.draw_stone_brick(surf, (cx + 22, 8, 20, 68))
        # Almenas superiores
        for i in range(4):
            pygame.draw.rect(surf, COLOR_STONE_LIGHT, (cx - 34 + i * 18, 12, 10, 8))
        # Puerta levadiza arqueada
        pygame.draw.rect(surf, COLOR_WOOD_DARK, (cx - 14, 44, 28, 32), border_radius=6)
        # Rejas de hierro
        for x in range(cx - 10, cx + 12, 5):
            pygame.draw.line(surf, COLOR_BLACK, (x, 46), (x, 74), 2)
        # Estandarte Real con León Dorado
        pygame.draw.rect(surf, COLOR_ROYAL_RED, (cx - 12, 22, 24, 18))
        pygame.draw.polygon(surf, COLOR_ROYAL_RED, [(cx - 12, 40), (cx + 12, 40), (cx, 46)])
        pygame.draw.circle(surf, COLOR_GOLD, (cx, 31), 5) # Corona / León

        self.cached_sprites["castle"] = surf
        return surf

# Instancia singleton
gfx = GraphicsEngine()
