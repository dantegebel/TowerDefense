"""
Definición de Mapas, Caminos, Emplazamientos de Torres y Oleadas para 'Reino en Asedio'.
"""

import math
import random
import pygame
from config import (
    COLOR_GRASS_BASE, COLOR_GRASS_LIGHT, COLOR_GRASS_DARK,
    COLOR_ROAD, COLOR_ROAD_BORDER, COLOR_ROAD_STONE,
    COLOR_WATER, COLOR_STONE_MID, COLOR_STONE_LIGHT,
    COLOR_WOOD_MID, COLOR_WOOD_DARK, COLOR_GOLD
)
from engine.graphics import gfx

LEVELS = [
    {
        "id": 1,
        "name": "Valle Verde",
        "desc": "El primer bastión del reino en las llanuras occidentales.",
        "difficulty": "Fácil",
        "starting_gold": 260,
        "starting_lives": 20,
        "paths": [
            [
                (-30, 220), (220, 220), (380, 160), (540, 160),
                (640, 310), (560, 480), (740, 560), (960, 560), (1140, 560)
            ]
        ],
        "castle_pos": (1180, 560),
        "spawn_points": [(-30, 220)],
        "building_spots": [
            (220, 140), (320, 260), (480, 230), (600, 220),
            (500, 380), (680, 430), (820, 480), (960, 480)
        ],
        "waves": [
            # Oleada 1: Goblins
            [{"type": "goblin", "count": 6, "delay": 1.2}],
            # Oleada 2: Goblins + Esqueletos
            [{"type": "goblin", "count": 8, "delay": 1.0}, {"type": "skeleton", "count": 4, "delay": 1.4}],
            # Oleada 3: Enjambre de Esqueletos
            [{"type": "skeleton", "count": 10, "delay": 1.1}],
            # Oleada 4: Orcos Berserker
            [{"type": "goblin", "count": 8, "delay": 0.8}, {"type": "orc", "count": 3, "delay": 2.2}],
            # Oleada 5: Asalto Mixto
            [{"type": "skeleton", "count": 12, "delay": 0.9}, {"type": "orc", "count": 5, "delay": 1.8}],
            # Oleada 6: Caballeros Negros
            [{"type": "dark_knight", "count": 3, "delay": 2.8}, {"type": "goblin", "count": 14, "delay": 0.6}],
            # Oleada 7: Nigromantes oscuros
            [{"type": "necromancer", "count": 3, "delay": 3.0}, {"type": "skeleton", "count": 12, "delay": 0.8}],
            # Oleada 8: Ejército Acorazado
            [{"type": "orc", "count": 8, "delay": 1.4}, {"type": "dark_knight", "count": 5, "delay": 2.2}],
            # Oleada 9: Golem de Piedra
            [{"type": "golem", "count": 1, "delay": 4.0}, {"type": "dark_knight", "count": 4, "delay": 2.0}, {"type": "goblin", "count": 15, "delay": 0.5}],
            # Oleada 10: Asalto Final del Valle
            [{"type": "golem", "count": 2, "delay": 4.0}, {"type": "necromancer", "count": 4, "delay": 2.5}, {"type": "orc", "count": 10, "delay": 1.2}]
        ]
    },
    {
        "id": 2,
        "name": "Paso de la Montaña Oscura",
        "desc": "Un desfiladero rocoso donde dos senderos convergen en un estrecho puente.",
        "difficulty": "Media",
        "starting_gold": 320,
        "starting_lives": 20,
        "paths": [
            # Sendero Norte
            [
                (-30, 150), (260, 150), (440, 280), (620, 360),
                (840, 360), (1020, 480), (1140, 480)
            ],
            # Sendero Sur
            [
                (-30, 580), (280, 580), (460, 450), (620, 360),
                (840, 360), (1020, 480), (1140, 480)
            ]
        ],
        "castle_pos": (1180, 480),
        "spawn_points": [(-30, 150), (-30, 580)],
        "building_spots": [
            (160, 80), (320, 80), (180, 460), (340, 500),
            (420, 190), (520, 270), (520, 450), (700, 280),
            (760, 440), (920, 280), (960, 400)
        ],
        "waves": [
            [{"type": "goblin", "count": 10, "delay": 0.9}],
            [{"type": "skeleton", "count": 12, "delay": 1.0}],
            [{"type": "orc", "count": 6, "delay": 1.6}, {"type": "goblin", "count": 10, "delay": 0.7}],
            [{"type": "dark_knight", "count": 4, "delay": 2.2}, {"type": "skeleton", "count": 10, "delay": 0.9}],
            [{"type": "necromancer", "count": 4, "delay": 2.5}, {"type": "orc", "count": 8, "delay": 1.3}],
            [{"type": "golem", "count": 2, "delay": 3.5}, {"type": "goblin", "count": 16, "delay": 0.5}],
            [{"type": "dark_knight", "count": 8, "delay": 1.8}, {"type": "orc", "count": 8, "delay": 1.2}],
            [{"type": "golem", "count": 2, "delay": 3.0}, {"type": "necromancer", "count": 5, "delay": 2.0}],
            [{"type": "dark_knight", "count": 10, "delay": 1.5}, {"type": "golem", "count": 3, "delay": 2.8}],
            [{"type": "dragon_boss", "count": 1, "delay": 6.0}, {"type": "orc", "count": 12, "delay": 1.0}],
            [{"type": "golem", "count": 4, "delay": 2.5}, {"type": "dark_knight", "count": 12, "delay": 1.2}, {"type": "necromancer", "count": 6, "delay": 1.8}]
        ]
    },
    {
        "id": 3,
        "name": "La Ciudadela Real",
        "desc": "El asedio supremo al corazón del Reino. ¡El Gran Dragón Carmesí comanda las huestes!",
        "difficulty": "Difícil",
        "starting_gold": 380,
        "starting_lives": 25,
        "paths": [
            # Sendero Superior
            [
                (-30, 160), (320, 160), (520, 240), (740, 240), (960, 360), (1140, 360)
            ],
            # Sendero Inferior
            [
                (-30, 560), (320, 560), (520, 480), (740, 480), (960, 360), (1140, 360)
            ]
        ],
        "castle_pos": (1180, 360),
        "spawn_points": [(-30, 160), (-30, 560)],
        "building_spots": [
            (160, 80), (360, 80), (220, 240), (420, 240),
            (620, 160), (620, 320), (620, 480), (840, 160),
            (840, 440), (1020, 240), (1020, 480), (220, 480),
            (360, 640), (160, 640)
        ],
        "waves": [
            [{"type": "goblin", "count": 14, "delay": 0.7}],
            [{"type": "orc", "count": 8, "delay": 1.2}, {"type": "skeleton", "count": 14, "delay": 0.8}],
            [{"type": "dark_knight", "count": 6, "delay": 1.8}, {"type": "necromancer", "count": 4, "delay": 2.2}],
            [{"type": "golem", "count": 2, "delay": 3.0}, {"type": "orc", "count": 12, "delay": 1.0}],
            [{"type": "dark_knight", "count": 10, "delay": 1.4}, {"type": "golem", "count": 3, "delay": 2.5}],
            [{"type": "necromancer", "count": 8, "delay": 1.8}, {"type": "skeleton", "count": 25, "delay": 0.5}],
            [{"type": "dragon_boss", "count": 1, "delay": 8.0}, {"type": "golem", "count": 2, "delay": 3.0}],
            [{"type": "dragon_boss", "count": 1, "delay": 5.0}, {"type": "dark_knight", "count": 12, "delay": 1.2}, {"type": "golem", "count": 4, "delay": 2.0}]
        ]
    }
]

class MapRenderer:
    def __init__(self, level_data):
        self.level_data = level_data
        self.cached_bg = None
        self._render_background()

    def _render_background(self):
        w, h = 1280, 720
        surf = pygame.Surface((w, h))
        surf.fill(COLOR_GRASS_BASE)

        # 1. Textura de hierba y detalles de flores / piedras
        random.seed(self.level_data["id"] * 42)
        for _ in range(350):
            gx = random.randint(0, w)
            gy = random.randint(0, h)
            col = random.choice([COLOR_GRASS_LIGHT, COLOR_GRASS_DARK])
            pygame.draw.circle(surf, col, (gx, gy), random.randint(3, 8))
        
        # Flores silvestres
        for _ in range(80):
            fx = random.randint(0, w)
            fy = random.randint(0, h)
            col = random.choice([(240, 230, 90), (230, 80, 120), (140, 190, 255), (250, 250, 250)])
            pygame.draw.circle(surf, col, (fx, fy), 2)

        # 2. Caminos de adoquines medievales con bordes sombreados
        road_width = 46
        for path in self.level_data["paths"]:
            # Borde exterior de tierra oscura
            pygame.draw.lines(surf, COLOR_ROAD_BORDER, False, path, road_width + 8)
            # Relleno del camino de adoquines
            pygame.draw.lines(surf, COLOR_ROAD, False, path, road_width)
            
            # Dibujar piedras de adoquines a lo largo del camino
            for i in range(len(path) - 1):
                p1, p2 = path[i], path[i+1]
                dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
                steps = int(dist // 14)
                for s in range(steps):
                    t = s / max(1, steps)
                    px = p1[0] + (p2[0] - p1[0]) * t + random.uniform(-10, 10)
                    py = p1[1] + (p2[1] - p1[1]) * t + random.uniform(-10, 10)
                    stone_col = random.choice([COLOR_ROAD_STONE, COLOR_ROAD_BORDER])
                    pygame.draw.ellipse(surf, stone_col, (px - 4, py - 3, 8, 6))

        # 3. Árboles y follaje en el mapa
        for _ in range(35):
            tx = random.randint(40, w - 120)
            ty = random.randint(40, h - 80)
            # Evitar colocar árboles encima de los caminos
            on_path = False
            for path in self.level_data["paths"]:
                for i in range(len(path) - 1):
                    p1, p2 = path[i], path[i+1]
                    # Distancia al segmento
                    d = self._dist_to_segment((tx, ty), p1, p2)
                    if d < 48:
                        on_path = True
                        break
                if on_path:
                    break
            
            if not on_path:
                # Sombra de árbol
                pygame.draw.ellipse(surf, (20, 45, 15, 120), (tx - 18, ty + 8, 36, 16))
                # Tronco
                pygame.draw.rect(surf, COLOR_WOOD_DARK, (tx - 3, ty + 2, 6, 12))
                # Copa frondosa
                pygame.draw.circle(surf, (28, 70, 22), (tx, ty - 6), 18)
                pygame.draw.circle(surf, (40, 95, 30), (tx - 4, ty - 8), 14)
                pygame.draw.circle(surf, (55, 120, 42), (tx + 2, ty - 12), 10)

        # 4. Emplazamientos de construcción (Pedestales de piedra marcados)
        for spot in self.level_data["building_spots"]:
            sx, sy = spot
            # Sombra y pedestal de piedra marcado con runa dorada
            pygame.draw.ellipse(surf, (15, 25, 12, 160), (sx - 26, sy + 6, 52, 22))
            pygame.draw.ellipse(surf, COLOR_STONE_MID, (sx - 24, sy - 8, 48, 24))
            pygame.draw.ellipse(surf, COLOR_STONE_LIGHT, (sx - 22, sy - 6, 44, 20))
            pygame.draw.circle(surf, COLOR_GOLD, (sx, sy + 3), 4, 1)

        # 5. Castillo Real al final del camino
        cx, cy = self.level_data["castle_pos"]
        castle_surf = gfx.get_castle_sprite()
        surf.blit(castle_surf, (cx - castle_surf.get_width()//2 - 15, cy - castle_surf.get_height()//2 - 10))

        self.cached_bg = surf

    def _dist_to_segment(self, p, p1, p2):
        x, y = p
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(x - x1, y - y1)
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(x - proj_x, y - proj_y)

    def draw(self, surface):
        if self.cached_bg:
            surface.blit(self.cached_bg, (0, 0))
