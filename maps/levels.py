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
    },
    {
        "id": 4,
        "name": "La Encrucijada Maldita",
        "desc": "Un pantano brumoso con 3 caminos simultáneos donde acechan Trolls y Guivernos.",
        "difficulty": "Avanzada",
        "biome": "swamp",
        "starting_gold": 460,
        "starting_lives": 20,
        "paths": [
            # Sendero 1: Flanco Noroeste
            [
                (-30, 140), (240, 140), (380, 240), (580, 240),
                (780, 180), (960, 220), (1140, 340)
            ],
            # Sendero 2: Cruce Directo Centro
            [
                (-30, 360), (220, 360), (440, 480), (660, 480),
                (860, 380), (1020, 360), (1140, 360)
            ],
            # Sendero 3: Emboscada Sur
            [
                (-30, 600), (260, 600), (460, 520), (680, 340),
                (900, 460), (1060, 460), (1140, 380)
            ]
        ],
        "castle_pos": (1180, 360),
        "spawn_points": [(-30, 140), (-30, 360), (-30, 600)],
        "building_spots": [
            (140, 220), (280, 200), (320, 320), (160, 480), (320, 480),
            (480, 180), (520, 380), (620, 170), (620, 540), (760, 300),
            (760, 420), (880, 280), (880, 530), (1020, 260), (1020, 440)
        ],
        "waves": [
            [{"type": "goblin", "count": 16, "delay": 0.6}],
            [{"type": "skeleton", "count": 18, "delay": 0.7}, {"type": "goblin", "count": 10, "delay": 0.6}],
            [{"type": "wyvern", "count": 6, "delay": 1.6}, {"type": "orc", "count": 8, "delay": 1.2}],
            [{"type": "orc", "count": 10, "delay": 1.1}, {"type": "dark_knight", "count": 6, "delay": 1.8}],
            [{"type": "troll", "count": 2, "delay": 3.5}, {"type": "goblin", "count": 20, "delay": 0.5}],
            [{"type": "wyvern", "count": 10, "delay": 1.3}, {"type": "dark_knight", "count": 8, "delay": 1.6}],
            [{"type": "necromancer", "count": 6, "delay": 2.0}, {"type": "troll", "count": 3, "delay": 3.0}],
            [{"type": "golem", "count": 3, "delay": 3.0}, {"type": "dark_knight", "count": 12, "delay": 1.4}],
            [{"type": "troll", "count": 4, "delay": 2.5}, {"type": "wyvern", "count": 12, "delay": 1.0}, {"type": "orc", "count": 15, "delay": 0.8}],
            [{"type": "dragon_boss", "count": 1, "delay": 6.0}, {"type": "troll", "count": 4, "delay": 2.2}, {"type": "golem", "count": 3, "delay": 2.5}]
        ]
    },
    {
        "id": 5,
        "name": "La Grieta de Lava",
        "desc": "El infierno volcánico con caminos bifurcados y ríos de magma. ¡La prueba suprema!",
        "difficulty": "Pesadilla",
        "biome": "volcano",
        "starting_gold": 540,
        "starting_lives": 25,
        "paths": [
            # Sendero Norte (Canal de Magma)
            [
                (-30, 180), (180, 180), (340, 120), (540, 120),
                (680, 240), (840, 240), (980, 180), (1140, 320)
            ],
            # Sendero Sur (Fisura del Abismo)
            [
                (-30, 540), (180, 540), (340, 600), (540, 600),
                (680, 480), (840, 480), (980, 540), (1140, 400)
            ],
            # Sendero Central (El Puente de Roca Ardiente)
            [
                (-30, 180), (180, 180), (380, 360), (640, 360),
                (860, 480), (1040, 360), (1140, 360)
            ],
            # Sendero Invertido Cruzado
            [
                (-30, 540), (180, 540), (380, 360), (640, 360),
                (860, 240), (1040, 360), (1140, 360)
            ]
        ],
        "castle_pos": (1180, 360),
        "spawn_points": [(-30, 180), (-30, 540)],
        "building_spots": [
            (120, 110), (120, 360), (120, 610), (260, 260), (260, 460),
            (440, 200), (440, 520), (540, 240), (540, 480), (640, 180),
            (640, 540), (760, 360), (880, 160), (880, 560), (940, 360),
            (1040, 220), (1040, 500)
        ],
        "waves": [
            [{"type": "goblin", "count": 20, "delay": 0.5}],
            [{"type": "orc", "count": 12, "delay": 1.0}, {"type": "wyvern", "count": 6, "delay": 1.5}],
            [{"type": "dark_knight", "count": 8, "delay": 1.5}, {"type": "skeleton", "count": 20, "delay": 0.6}],
            [{"type": "troll", "count": 3, "delay": 2.8}, {"type": "orc", "count": 14, "delay": 0.9}],
            [{"type": "wyvern", "count": 12, "delay": 1.0}, {"type": "necromancer", "count": 5, "delay": 2.0}],
            [{"type": "golem", "count": 4, "delay": 2.5}, {"type": "dark_knight", "count": 10, "delay": 1.4}],
            [{"type": "troll", "count": 5, "delay": 2.2}, {"type": "wyvern", "count": 14, "delay": 0.9}],
            [{"type": "necromancer", "count": 8, "delay": 1.6}, {"type": "dark_knight", "count": 14, "delay": 1.2}],
            [{"type": "dragon_boss", "count": 1, "delay": 7.0}, {"type": "golem", "count": 4, "delay": 2.5}],
            [{"type": "troll", "count": 6, "delay": 2.0}, {"type": "dark_knight", "count": 16, "delay": 1.1}, {"type": "wyvern", "count": 16, "delay": 0.8}],
            [{"type": "dragon_boss", "count": 1, "delay": 5.0}, {"type": "dragon_boss", "count": 1, "delay": 10.0}, {"type": "golem", "count": 4, "delay": 2.2}]
        ]
    },
    {
        "id": 6,
        "name": "Las Cumbres Blancas",
        "desc": "Picos nevados y ventiscas gélidas con 3 caminos donde acechan Golems de Escarcha.",
        "difficulty": "Avanzada",
        "biome": "snow",
        "starting_gold": 500,
        "starting_lives": 20,
        "paths": [
            [(-30, 160), (280, 160), (480, 240), (680, 240), (880, 360), (1140, 360)],
            [(-30, 360), (220, 360), (440, 360), (700, 360), (920, 360), (1140, 360)],
            [(-30, 560), (280, 560), (480, 480), (680, 480), (880, 360), (1140, 360)]
        ],
        "castle_pos": (1180, 360),
        "spawn_points": [(-30, 160), (-30, 360), (-30, 560)],
        "building_spots": [
            (160, 90), (360, 90), (160, 440), (360, 440), (160, 630), (360, 630),
            (560, 160), (560, 300), (560, 420), (560, 550), (780, 160), (780, 420),
            (960, 260), (960, 460), (1060, 260), (1060, 460)
        ],
        "waves": [
            [{"type": "goblin", "count": 18, "delay": 0.6}],
            [{"type": "skeleton", "count": 22, "delay": 0.6}, {"type": "orc", "count": 8, "delay": 1.2}],
            [{"type": "wyvern", "count": 8, "delay": 1.4}, {"type": "dark_knight", "count": 6, "delay": 1.8}],
            [{"type": "troll", "count": 3, "delay": 2.5}, {"type": "orc", "count": 12, "delay": 1.0}],
            [{"type": "golem", "count": 3, "delay": 3.0}, {"type": "wyvern", "count": 10, "delay": 1.1}],
            [{"type": "necromancer", "count": 6, "delay": 1.8}, {"type": "troll", "count": 4, "delay": 2.2}],
            [{"type": "dark_knight", "count": 12, "delay": 1.3}, {"type": "golem", "count": 4, "delay": 2.0}],
            [{"type": "wyvern", "count": 14, "delay": 0.9}, {"type": "troll", "count": 5, "delay": 2.0}],
            [{"type": "dragon_boss", "count": 1, "delay": 6.0}, {"type": "golem", "count": 4, "delay": 2.2}],
            [{"type": "dragon_boss", "count": 1, "delay": 5.0}, {"type": "troll", "count": 6, "delay": 1.8}, {"type": "dark_knight", "count": 14, "delay": 1.0}]
        ]
    },
    {
        "id": 7,
        "name": "Ruinas de Aethelgard",
        "desc": "Un gran cruce en 'X' sobre templos milenarios semienterrados en la arena dorada.",
        "difficulty": "Difícil",
        "biome": "desert",
        "starting_gold": 520,
        "starting_lives": 20,
        "paths": [
            [(-30, 140), (220, 140), (440, 240), (640, 360), (840, 480), (1020, 480), (1140, 360)],
            [(-30, 580), (220, 580), (440, 480), (640, 360), (840, 240), (1020, 240), (1140, 360)]
        ],
        "castle_pos": (1180, 360),
        "spawn_points": [(-30, 140), (-30, 580)],
        "building_spots": [
            (140, 230), (140, 490), (320, 180), (320, 540), (460, 360),
            (540, 220), (540, 500), (640, 240), (640, 480), (740, 220),
            (740, 500), (820, 360), (960, 160), (960, 560), (1040, 360)
        ],
        "waves": [
            [{"type": "goblin", "count": 22, "delay": 0.5}],
            [{"type": "skeleton", "count": 24, "delay": 0.5}, {"type": "orc", "count": 10, "delay": 1.0}],
            [{"type": "necromancer", "count": 6, "delay": 1.8}, {"type": "skeleton", "count": 20, "delay": 0.5}],
            [{"type": "dark_knight", "count": 8, "delay": 1.4}, {"type": "orc", "count": 14, "delay": 0.8}],
            [{"type": "troll", "count": 4, "delay": 2.2}, {"type": "wyvern", "count": 8, "delay": 1.2}],
            [{"type": "golem", "count": 4, "delay": 2.4}, {"type": "necromancer", "count": 6, "delay": 1.6}],
            [{"type": "wyvern", "count": 16, "delay": 0.8}, {"type": "troll", "count": 4, "delay": 1.8}],
            [{"type": "dark_knight", "count": 14, "delay": 1.1}, {"type": "golem", "count": 5, "delay": 2.0}],
            [{"type": "dragon_boss", "count": 1, "delay": 6.0}, {"type": "troll", "count": 5, "delay": 2.0}],
            [{"type": "dragon_boss", "count": 1, "delay": 4.0}, {"type": "dark_knight", "count": 16, "delay": 1.0}, {"type": "golem", "count": 4, "delay": 2.0}]
        ]
    },
    {
        "id": 8,
        "name": "El Pantano del Terror",
        "desc": "Aguas putrefactas y tres rutas sinuosas con doble cruce de emboscada.",
        "difficulty": "Difícil",
        "biome": "swamp",
        "starting_gold": 550,
        "starting_lives": 25,
        "paths": [
            [(-30, 160), (240, 160), (440, 280), (640, 280), (840, 180), (1040, 260), (1140, 360)],
            [(-30, 360), (220, 360), (440, 280), (640, 440), (840, 440), (1040, 360), (1140, 360)],
            [(-30, 560), (240, 560), (440, 440), (640, 440), (840, 540), (1040, 460), (1140, 360)]
        ],
        "castle_pos": (1180, 360),
        "spawn_points": [(-30, 160), (-30, 360), (-30, 560)],
        "building_spots": [
            (140, 260), (140, 460), (320, 220), (320, 500), (440, 180),
            (440, 540), (540, 360), (640, 180), (640, 540), (740, 360),
            (840, 280), (840, 440), (960, 180), (960, 540), (1040, 180), (1040, 540)
        ],
        "waves": [
            [{"type": "goblin", "count": 24, "delay": 0.5}],
            [{"type": "skeleton", "count": 26, "delay": 0.5}, {"type": "wyvern", "count": 6, "delay": 1.4}],
            [{"type": "troll", "count": 3, "delay": 2.4}, {"type": "orc", "count": 14, "delay": 0.8}],
            [{"type": "dark_knight", "count": 10, "delay": 1.3}, {"type": "necromancer", "count": 6, "delay": 1.6}],
            [{"type": "wyvern", "count": 14, "delay": 0.8}, {"type": "troll", "count": 4, "delay": 2.0}],
            [{"type": "golem", "count": 5, "delay": 2.2}, {"type": "dark_knight", "count": 12, "delay": 1.2}],
            [{"type": "troll", "count": 6, "delay": 1.8}, {"type": "necromancer", "count": 8, "delay": 1.4}],
            [{"type": "dragon_boss", "count": 1, "delay": 6.0}, {"type": "golem", "count": 4, "delay": 2.0}],
            [{"type": "dark_knight", "count": 16, "delay": 1.0}, {"type": "troll", "count": 6, "delay": 1.8}],
            [{"type": "dragon_boss", "count": 1, "delay": 4.0}, {"type": "wyvern", "count": 18, "delay": 0.7}, {"type": "golem", "count": 5, "delay": 1.8}]
        ]
    },
    {
        "id": 9,
        "name": "El Desfiladero del Dragón",
        "desc": "Un abismo rocoso con 4 senderos y constantes asaltos aéreos de Guivernos.",
        "difficulty": "Pesadilla",
        "biome": "mountain",
        "starting_gold": 580,
        "starting_lives": 25,
        "paths": [
            [(-30, 140), (260, 140), (460, 220), (680, 220), (920, 320), (1140, 340)],
            [(-30, 280), (220, 280), (420, 340), (660, 340), (880, 340), (1140, 360)],
            [(-30, 440), (220, 440), (420, 380), (660, 380), (880, 380), (1140, 380)],
            [(-30, 580), (260, 580), (460, 500), (680, 500), (920, 400), (1140, 380)]
        ],
        "castle_pos": (1180, 360),
        "spawn_points": [(-30, 140), (-30, 280), (-30, 440), (-30, 580)],
        "building_spots": [
            (140, 80), (140, 360), (140, 640), (320, 200), (320, 520),
            (520, 160), (520, 280), (520, 440), (520, 560), (760, 160),
            (760, 280), (760, 440), (760, 560), (980, 240), (980, 480), (1060, 360)
        ],
        "waves": [
            [{"type": "goblin", "count": 26, "delay": 0.4}],
            [{"type": "wyvern", "count": 12, "delay": 1.0}, {"type": "orc", "count": 14, "delay": 0.8}],
            [{"type": "dark_knight", "count": 10, "delay": 1.2}, {"type": "troll", "count": 4, "delay": 2.0}],
            [{"type": "necromancer", "count": 8, "delay": 1.5}, {"type": "skeleton", "count": 30, "delay": 0.4}],
            [{"type": "golem", "count": 5, "delay": 2.2}, {"type": "dark_knight", "count": 12, "delay": 1.1}],
            [{"type": "wyvern", "count": 18, "delay": 0.7}, {"type": "troll", "count": 6, "delay": 1.7}],
            [{"type": "dragon_boss", "count": 1, "delay": 6.0}, {"type": "golem", "count": 4, "delay": 2.0}],
            [{"type": "dark_knight", "count": 16, "delay": 1.0}, {"type": "necromancer", "count": 8, "delay": 1.3}],
            [{"type": "dragon_boss", "count": 1, "delay": 5.0}, {"type": "troll", "count": 7, "delay": 1.5}],
            [{"type": "dragon_boss", "count": 1, "delay": 4.0}, {"type": "dragon_boss", "count": 1, "delay": 8.0}, {"type": "wyvern", "count": 20, "delay": 0.6}]
        ]
    },
    {
        "id": 10,
        "name": "El Trono de la Perdición",
        "desc": "¡La batalla final por la supervivencia del Reino! Cuatro sendas volcánicas y el Gran Dragón Supremo.",
        "difficulty": "Pesadilla",
        "biome": "volcano",
        "starting_gold": 650,
        "starting_lives": 30,
        "paths": [
            [(-30, 140), (200, 140), (380, 100), (580, 100), (760, 220), (940, 220), (1140, 340)],
            [(-30, 320), (180, 320), (360, 260), (600, 260), (820, 360), (1020, 360), (1140, 360)],
            [(-30, 420), (180, 420), (360, 480), (600, 480), (820, 360), (1020, 360), (1140, 360)],
            [(-30, 600), (200, 600), (380, 620), (580, 620), (760, 500), (940, 500), (1140, 380)]
        ],
        "castle_pos": (1180, 360),
        "spawn_points": [(-30, 140), (-30, 320), (-30, 420), (-30, 600)],
        "building_spots": [
            (110, 80), (110, 370), (110, 650), (260, 200), (260, 530),
            (460, 180), (460, 370), (460, 550), (660, 180), (660, 370),
            (660, 550), (840, 200), (840, 520), (960, 300), (960, 420),
            (1050, 260), (1050, 460)
        ],
        "waves": [
            [{"type": "goblin", "count": 28, "delay": 0.4}],
            [{"type": "orc", "count": 16, "delay": 0.7}, {"type": "wyvern", "count": 10, "delay": 1.0}],
            [{"type": "dark_knight", "count": 12, "delay": 1.1}, {"type": "skeleton", "count": 30, "delay": 0.4}],
            [{"type": "troll", "count": 5, "delay": 1.8}, {"type": "orc", "count": 16, "delay": 0.7}],
            [{"type": "necromancer", "count": 8, "delay": 1.3}, {"type": "dark_knight", "count": 14, "delay": 1.0}],
            [{"type": "golem", "count": 6, "delay": 2.0}, {"type": "wyvern", "count": 16, "delay": 0.7}],
            [{"type": "troll", "count": 7, "delay": 1.6}, {"type": "golem", "count": 5, "delay": 1.8}],
            [{"type": "dragon_boss", "count": 1, "delay": 6.0}, {"type": "dark_knight", "count": 18, "delay": 0.9}],
            [{"type": "troll", "count": 8, "delay": 1.5}, {"type": "wyvern", "count": 20, "delay": 0.6}, {"type": "necromancer", "count": 8, "delay": 1.2}],
            [{"type": "dragon_boss", "count": 1, "delay": 5.0}, {"type": "dragon_boss", "count": 1, "delay": 8.0}, {"type": "golem", "count": 6, "delay": 1.6}],
            [{"type": "dragon_boss", "count": 1, "delay": 3.0}, {"type": "dragon_boss", "count": 1, "delay": 6.0}, {"type": "troll", "count": 8, "delay": 1.4}, {"type": "dark_knight", "count": 20, "delay": 0.8}]
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
        biome = self.level_data.get("biome", "grass")
        
        # Paletas de color según Bioma
        if biome == "volcano":
            base_color = (28, 22, 28)
            detail_colors = [(45, 28, 36), (65, 30, 25), (200, 70, 20)]
            road_border = (20, 14, 18)
            road_color = (60, 38, 36)
            road_stone = (90, 50, 42)
            tree_bark = (40, 25, 25)
            tree_leaves = [(180, 50, 20), (220, 80, 30), (140, 35, 15)] # Pilares ígneos
        elif biome == "snow":
            base_color = (230, 236, 244)
            detail_colors = [(255, 255, 255), (210, 225, 240), (185, 205, 225)]
            road_border = (160, 175, 195)
            road_color = (195, 210, 225)
            road_stone = (220, 230, 242)
            tree_bark = (60, 50, 45)
            tree_leaves = [(240, 248, 255), (220, 235, 250), (200, 220, 240)] # Pinos nevados
        elif biome == "desert":
            base_color = (215, 185, 125)
            detail_colors = [(195, 165, 105), (230, 205, 145), (175, 145, 90)]
            road_border = (150, 115, 75)
            road_color = (185, 145, 95)
            road_stone = (210, 175, 120)
            tree_bark = (90, 65, 40)
            tree_leaves = [(70, 120, 50), (90, 145, 65), (55, 100, 40)] # Palmeras/Oasis
        elif biome == "swamp":
            base_color = (32, 46, 36)
            detail_colors = [(24, 38, 28), (42, 60, 45), (140, 50, 180)] # Musgo y esporas
            road_border = (20, 28, 22)
            road_color = (48, 55, 42)
            road_stone = (70, 78, 60)
            tree_bark = (35, 30, 25)
            tree_leaves = [(25, 55, 30), (35, 75, 40), (50, 95, 50)]
        elif biome == "mountain":
            base_color = (55, 62, 58)
            detail_colors = [(45, 52, 48), (70, 78, 72), (85, 95, 88)]
            road_border = (35, 38, 36)
            road_color = (95, 92, 85)
            road_stone = (120, 115, 105)
            tree_bark = (50, 40, 35)
            tree_leaves = [(30, 60, 40), (45, 80, 55), (60, 100, 70)]
        else:
            base_color = COLOR_GRASS_BASE
            detail_colors = [COLOR_GRASS_LIGHT, COLOR_GRASS_DARK]
            road_border = COLOR_ROAD_BORDER
            road_color = COLOR_ROAD
            road_stone = COLOR_ROAD_STONE
            tree_bark = COLOR_WOOD_DARK
            tree_leaves = [(28, 70, 22), (40, 95, 30), (55, 120, 42)]

        surf.fill(base_color)

        # 1. Textura de terreno y partículas ambientales
        random.seed(self.level_data["id"] * 42)
        for _ in range(380):
            gx = random.randint(0, w)
            gy = random.randint(0, h)
            col = random.choice(detail_colors)
            pygame.draw.circle(surf, col, (gx, gy), random.randint(3, 8))
        
        # Detalles ambientales (flores silvestres, hongos luminosos o chispas de lava)
        if biome == "volcano":
            for _ in range(60):
                fx = random.randint(0, w)
                fy = random.randint(0, h)
                col = random.choice([(255, 140, 40), (255, 60, 20), (255, 210, 80)])
                pygame.draw.circle(surf, col, (fx, fy), random.randint(2, 4))
        elif biome == "swamp":
            for _ in range(60):
                fx = random.randint(0, w)
                fy = random.randint(0, h)
                col = random.choice([(180, 70, 220), (60, 240, 120), (140, 200, 255)])
                pygame.draw.circle(surf, col, (fx, fy), 2)
        else:
            for _ in range(80):
                fx = random.randint(0, w)
                fy = random.randint(0, h)
                col = random.choice([(240, 230, 90), (230, 80, 120), (140, 190, 255), (250, 250, 250)])
                pygame.draw.circle(surf, col, (fx, fy), 2)

        # 2. Caminos medievales con bordes sombreados
        road_width = 46
        for path in self.level_data["paths"]:
            pygame.draw.lines(surf, road_border, False, path, road_width + 8)
            pygame.draw.lines(surf, road_color, False, path, road_width)
            
            for i in range(len(path) - 1):
                p1, p2 = path[i], path[i+1]
                dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
                steps = int(dist // 14)
                for s in range(steps):
                    t = s / max(1, steps)
                    px = p1[0] + (p2[0] - p1[0]) * t + random.uniform(-10, 10)
                    py = p1[1] + (p2[1] - p1[1]) * t + random.uniform(-10, 10)
                    stone_col = random.choice([road_stone, road_border])
                    pygame.draw.ellipse(surf, stone_col, (px - 4, py - 3, 8, 6))

        # 3. Árboles, monolitos o formaciones según bioma
        for _ in range(35):
            tx = random.randint(40, w - 120)
            ty = random.randint(40, h - 80)
            on_path = False
            for path in self.level_data["paths"]:
                for i in range(len(path) - 1):
                    p1, p2 = path[i], path[i+1]
                    d = self._dist_to_segment((tx, ty), p1, p2)
                    if d < 48:
                        on_path = True
                        break
                if on_path:
                    break
            
            if not on_path:
                pygame.draw.ellipse(surf, (15, 20, 15, 120), (tx - 18, ty + 8, 36, 16))
                pygame.draw.rect(surf, tree_bark, (tx - 3, ty + 2, 6, 12))
                pygame.draw.circle(surf, tree_leaves[0], (tx, ty - 6), 18)
                pygame.draw.circle(surf, tree_leaves[1], (tx - 4, ty - 8), 14)
                pygame.draw.circle(surf, tree_leaves[2], (tx + 2, ty - 12), 10)

        # 4. Emplazamientos de construcción (Pedestales de piedra marcados)
        for spot in self.level_data["building_spots"]:
            sx, sy = spot
            pygame.draw.ellipse(surf, (15, 25, 12, 160), (sx - 26, sy + 6, 52, 22))
            pygame.draw.ellipse(surf, COLOR_STONE_MID, (sx - 24, sy - 8, 48, 24))
            pygame.draw.ellipse(surf, COLOR_STONE_LIGHT, (sx - 22, sy - 6, 44, 20))
            rune_color = (255, 140, 40) if biome == "volcano" else COLOR_GOLD
            pygame.draw.circle(surf, rune_color, (sx, sy + 3), 4, 1)

        # 5. Castillo Real o Bastión al final del camino
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
