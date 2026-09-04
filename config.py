"""
Configuración global del juego: Reino en Asedio (Medieval Tower Defense)
"""

# Dimensiones de pantalla
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Reino en Asedio: Medieval Tower Defense"

# Paleta de Colores Medievales
COLOR_BG_DARK = (18, 16, 24)
COLOR_GRASS_BASE = (54, 98, 43)
COLOR_GRASS_LIGHT = (72, 122, 58)
COLOR_GRASS_DARK = (38, 74, 30)
COLOR_ROAD = (156, 138, 114)
COLOR_ROAD_BORDER = (112, 98, 80)
COLOR_ROAD_STONE = (180, 165, 142)
COLOR_WATER = (45, 95, 140)
COLOR_WATER_DEEP = (30, 68, 105)

COLOR_WOOD_DARK = (78, 46, 24)
COLOR_WOOD_MID = (120, 75, 42)
COLOR_WOOD_LIGHT = (168, 112, 68)

COLOR_STONE_DARK = (55, 58, 64)
COLOR_STONE_MID = (92, 98, 108)
COLOR_STONE_LIGHT = (145, 152, 164)

COLOR_GOLD = (235, 185, 52)
COLOR_GOLD_LIGHT = (255, 218, 105)
COLOR_GOLD_DARK = (180, 135, 25)

COLOR_ROYAL_RED = (180, 32, 42)
COLOR_ROYAL_BLUE = (35, 75, 165)
COLOR_ARCANE_PURPLE = (155, 60, 220)
COLOR_ICE_CYAN = (90, 215, 240)
COLOR_FIRE_ORANGE = (245, 110, 25)

COLOR_WHITE = (245, 245, 250)
COLOR_BLACK = (15, 15, 18)
COLOR_UI_BG = (28, 25, 34, 230)
COLOR_UI_BORDER = (205, 160, 75)
COLOR_UI_PANEL = (42, 38, 52)
COLOR_HEALTH_GREEN = (45, 200, 75)
COLOR_HEALTH_BG = (140, 25, 30)

# Balance de Economía y Vida
STARTING_LIVES = 20
STARTING_GOLD = 250

# Configuración de Torres
TOWER_DATA = {
    "archer": {
        "name": "Torre de Arqueros",
        "description": "Disparo rápido de flechas a distancia. Efectivo contra tropas ligeras.",
        "cost": 70,
        "range": 160,
        "damage": 12,
        "fire_rate": 1.2,
        "damage_type": "physical",
        "upgrade_cost": 60,
        "l2_damage": 22,
        "l2_range": 180,
        "l2_fire_rate": 1.5,
        "l3_damage": 38,
        "l3_range": 200,
        "l3_fire_rate": 1.8,
        "l3_upgrade_cost": 100,
        "special_a": {
            "name": "Ballesta Pesada",
            "desc": "Flechas perforantes con alta probabilidad crítica.",
            "cost": 150,
            "damage": 85,
            "range": 220,
            "fire_rate": 1.3,
            "crit_chance": 0.35,
            "crit_mult": 2.5
        },
        "special_b": {
            "name": "Tiradores Élficos",
            "desc": "Cadencia extrema con veneno acumulativo.",
            "cost": 140,
            "damage": 30,
            "range": 210,
            "fire_rate": 3.0,
            "poison_dps": 8,
            "poison_duration": 3.0
        }
    },
    "catapult": {
        "name": "Catapulta de Rocas",
        "description": "Lanza proyectiles explosivos pesados con daño de área. Ataque lento.",
        "cost": 110,
        "range": 190,
        "min_range": 45,
        "damage": 40,
        "splash_radius": 55,
        "fire_rate": 0.45,
        "damage_type": "physical",
        "upgrade_cost": 85,
        "l2_damage": 75,
        "l2_range": 210,
        "l2_splash": 65,
        "l3_damage": 130,
        "l3_range": 230,
        "l3_splash": 75,
        "l3_upgrade_cost": 140,
        "special_a": {
            "name": "Fuego Valyrio",
            "desc": "Rocas en llamas que dejan lava ardiente en el suelo.",
            "cost": 180,
            "damage": 190,
            "splash_radius": 85,
            "burn_dps": 25,
            "burn_duration": 4.0,
            "fire_rate": 0.45
        },
        "special_b": {
            "name": "Batería de Morteros",
            "desc": "Dispara proyectiles con aturdimiento.",
            "cost": 190,
            "damage": 110,
            "splash_radius": 60,
            "stun_duration": 0.8,
            "fire_rate": 0.55
        }
    },
    "mage": {
        "name": "Torre de Magos",
        "description": "Dispara esferas de energía arcana que ignoran la armadura física.",
        "cost": 90,
        "range": 150,
        "damage": 25,
        "fire_rate": 0.85,
        "damage_type": "magic",
        "upgrade_cost": 75,
        "l2_damage": 48,
        "l2_range": 170,
        "l2_fire_rate": 1.0,
        "l3_damage": 82,
        "l3_range": 190,
        "l3_fire_rate": 1.15,
        "l3_upgrade_cost": 125,
        "special_a": {
            "name": "Torre de Hielo",
            "desc": "Ralentiza a los enemigos en un 50% con aura gélida.",
            "cost": 160,
            "damage": 65,
            "range": 180,
            "slow_amount": 0.5,
            "slow_duration": 2.5,
            "fire_rate": 1.1
        },
        "special_b": {
            "name": "Tormenta de Rayos",
            "desc": "Rayos en cadena que saltan entre hasta 4 objetivos.",
            "cost": 175,
            "damage": 105,
            "range": 200,
            "chain_targets": 4,
            "fire_rate": 0.95
        }
    },
    "barracks": {
        "name": "Barracones de Guardia",
        "description": "Entrena a 3 soldados que bloquean y luchan contra los enemigos en el camino.",
        "cost": 80,
        "range": 160,
        "rally_range": 160,
        "soldier_count": 3,
        "soldier_hp": 90,
        "soldier_damage": 10,
        "soldier_armor": 0.20,
        "respawn_time": 10.0,
        "upgrade_cost": 70,
        "l2_hp": 150,
        "l2_damage": 18,
        "l2_armor": 0.35,
        "l3_hp": 240,
        "l3_damage": 30,
        "l3_armor": 0.50,
        "l3_upgrade_cost": 110,
        "special_a": {
            "name": "Paladines Sagrados",
            "desc": "Guerreros legendarios con escudos bendecidos y auto-curación.",
            "cost": 160,
            "hp": 420,
            "damage": 45,
            "armor": 0.65,
            "regen_per_sec": 8
        },
        "special_b": {
            "name": "Caballeros Bárbaros",
            "desc": "Doble hacha con ataque rápido.",
            "cost": 150,
            "hp": 320,
            "damage": 65,
            "armor": 0.40,
            "attack_speed": 1.5
        }
    },
    "alchemist": {
        "name": "Torre de Alquimia",
        "description": "Lanza frascos de ácido corrosivo que funden la armadura física y dejan brea en el suelo.",
        "cost": 100,
        "range": 165,
        "damage": 22,
        "fire_rate": 0.8,
        "damage_type": "magic",
        "armor_shred": 0.20,
        "upgrade_cost": 80,
        "l2_damage": 42,
        "l2_range": 180,
        "l2_fire_rate": 0.95,
        "l2_armor_shred": 0.35,
        "l3_damage": 70,
        "l3_range": 195,
        "l3_fire_rate": 1.1,
        "l3_armor_shred": 0.50,
        "l3_upgrade_cost": 130,
        "special_a": {
            "name": "Laboratorio de Plagas",
            "desc": "Nubes venenosas tóxicas persistentes con daño continuo acumulativo.",
            "cost": 170,
            "damage": 110,
            "range": 215,
            "fire_rate": 1.2,
            "poison_dps": 22,
            "poison_duration": 4.0,
            "armor_shred": 0.60
        },
        "special_b": {
            "name": "Lanza-Ácido Corrosivo",
            "desc": "Disolución ácida extrema: anula el 80% de la armadura enemiga y quema.",
            "cost": 180,
            "damage": 150,
            "range": 210,
            "fire_rate": 0.9,
            "armor_shred": 0.80,
            "burn_dps": 30,
            "burn_duration": 3.0
        }
    },
    "sun_shrine": {
        "name": "Santuario Solar",
        "description": "Canaliza un rayo solar continuo celestial ideal para derretir tanques colosales y jefes.",
        "cost": 120,
        "range": 175,
        "damage": 35,
        "fire_rate": 2.0,
        "damage_type": "magic",
        "upgrade_cost": 95,
        "l2_damage": 65,
        "l2_range": 195,
        "l2_fire_rate": 2.2,
        "l3_damage": 110,
        "l3_range": 215,
        "l3_fire_rate": 2.5,
        "l3_upgrade_cost": 150,
        "special_a": {
            "name": "Juicio Divino",
            "desc": "Rayo solar superconcentrado; máxima potencia de aniquilación individual.",
            "cost": 210,
            "damage": 240,
            "range": 235,
            "fire_rate": 3.0
        },
        "special_b": {
            "name": "Aura de Bendición Real",
            "desc": "Emite un aura dorada que aumenta en +30% el daño y alcance de torres aliadas cercanas.",
            "cost": 190,
            "damage": 130,
            "range": 220,
            "fire_rate": 2.5,
            "buff_radius": 150,
            "buff_damage_mult": 1.30
        }
    }
}

# Configuración de Enemigos
ENEMY_DATA = {
    "goblin": {
        "name": "Duende Asaltante",
        "hp": 95,
        "speed": 82,
        "armor": 0.05,
        "magic_resist": 0.0,
        "gold_reward": 10,
        "damage_to_base": 1,
        "attack_damage": 10,
        "attack_rate": 1.0,
        "size": 18,
        "color": (90, 150, 45)
    },
    "skeleton": {
        "name": "Soldado Esqueleto",
        "hp": 165,
        "speed": 60,
        "armor": 0.20,
        "magic_resist": 0.0,
        "gold_reward": 14,
        "damage_to_base": 1,
        "attack_damage": 14,
        "attack_rate": 0.9,
        "size": 20,
        "color": (210, 210, 205)
    },
    "orc": {
        "name": "Orco Berserker",
        "hp": 380,
        "speed": 48,
        "armor": 0.30,
        "magic_resist": 0.10,
        "gold_reward": 25,
        "damage_to_base": 2,
        "attack_damage": 28,
        "attack_rate": 0.8,
        "size": 24,
        "color": (145, 65, 40)
    },
    "dark_knight": {
        "name": "Caballero Negro",
        "hp": 650,
        "speed": 38,
        "armor": 0.65,
        "magic_resist": -0.10,
        "gold_reward": 45,
        "damage_to_base": 3,
        "attack_damage": 42,
        "attack_rate": 0.75,
        "size": 26,
        "color": (45, 45, 55)
    },
    "necromancer": {
        "name": "Nigromante",
        "hp": 340,
        "speed": 44,
        "armor": 0.10,
        "magic_resist": 0.50,
        "gold_reward": 50,
        "damage_to_base": 2,
        "attack_damage": 20,
        "attack_rate": 0.6,
        "size": 22,
        "color": (105, 30, 130),
        "summon_cooldown": 5.5
    },
    "troll": {
        "name": "Troll de las Cavernas",
        "hp": 920,
        "speed": 34,
        "armor": 0.25,
        "magic_resist": 0.15,
        "gold_reward": 65,
        "damage_to_base": 3,
        "attack_damage": 45,
        "attack_rate": 0.7,
        "size": 30,
        "color": (65, 115, 80),
        "regen_per_sec": 18.0
    },
    "golem": {
        "name": "Golem de Piedra",
        "hp": 1450,
        "speed": 26,
        "armor": 0.55,
        "magic_resist": 0.35,
        "gold_reward": 90,
        "damage_to_base": 5,
        "attack_damage": 65,
        "attack_rate": 0.5,
        "size": 34,
        "color": (110, 115, 125),
        "slow_immune": True
    },
    "wyvern": {
        "name": "Guiverno Alado",
        "hp": 480,
        "speed": 66,
        "armor": 0.15,
        "magic_resist": 0.30,
        "gold_reward": 45,
        "damage_to_base": 2,
        "attack_damage": 26,
        "attack_rate": 0.9,
        "size": 34,
        "color": (125, 45, 145),
        "is_flying": True
    },
    "dragon_boss": {
        "name": "Gran Dragón Carmesí (Jefe)",
        "hp": 4800,
        "speed": 32,
        "armor": 0.35,
        "magic_resist": 0.35,
        "gold_reward": 300,
        "damage_to_base": 15,
        "attack_damage": 90,
        "attack_rate": 0.4,
        "size": 52,
        "color": (210, 35, 30),
        "is_boss": True,
        "is_flying": True
    }
}

# Habilidades del Jugador (Spells)
SPELL_DATA = {
    "rain_of_arrows": {
        "name": "Lluvia de Flechas",
        "desc": "Dispara una andanada de flechas sobre un área amplia.",
        "key": "Q",
        "cooldown": 25.0,
        "radius": 95,
        "arrow_count": 30,
        "damage_per_arrow": 14,
        "sound": "arrow_rain"
    },
    "reinforcements": {
        "name": "Guardia Real",
        "desc": "Despliega 2 soldados temporales en cualquier punto del camino.",
        "key": "W",
        "cooldown": 20.0,
        "count": 2,
        "duration": 22.0,
        "hp": 180,
        "damage": 22,
        "armor": 0.30,
        "sound": "horn"
    },
    "meteor": {
        "name": "Meteoro de Fuego",
        "desc": "Invoca un meteoro cataclísmico que desintegra a los enemigos.",
        "key": "E",
        "cooldown": 45.0,
        "radius": 110,
        "damage": 280,
        "burn_dps": 30,
        "burn_duration": 4.5,
        "sound": "explosion"
    }
}
