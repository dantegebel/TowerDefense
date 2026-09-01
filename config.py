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
    }
}

# Configuración de Enemigos
ENEMY_DATA = {
    "goblin": {
        "name": "Duende Asaltante",
        "hp": 55,
        "speed": 85,
        "armor": 0.0,
        "magic_resist": 0.0,
        "gold_reward": 8,
        "damage_to_base": 1,
        "attack_damage": 8,
        "attack_rate": 1.0,
        "size": 18,
        "color": (90, 150, 45)
    },
    "skeleton": {
        "name": "Soldado Esqueleto",
        "hp": 95,
        "speed": 62,
        "armor": 0.15,
        "magic_resist": 0.0,
        "gold_reward": 12,
        "damage_to_base": 1,
        "attack_damage": 12,
        "attack_rate": 0.9,
        "size": 20,
        "color": (210, 210, 205)
    },
    "orc": {
        "name": "Orco Berserker",
        "hp": 220,
        "speed": 50,
        "armor": 0.25,
        "magic_resist": 0.1,
        "gold_reward": 22,
        "damage_to_base": 2,
        "attack_damage": 24,
        "attack_rate": 0.8,
        "size": 24,
        "color": (145, 65, 40)
    },
    "dark_knight": {
        "name": "Caballero Negro",
        "hp": 380,
        "speed": 40,
        "armor": 0.65,
        "magic_resist": -0.15,
        "gold_reward": 35,
        "damage_to_base": 3,
        "attack_damage": 35,
        "attack_rate": 0.75,
        "size": 26,
        "color": (45, 45, 55)
    },
    "necromancer": {
        "name": "Nigromante",
        "hp": 200,
        "speed": 45,
        "armor": 0.05,
        "magic_resist": 0.50,
        "gold_reward": 40,
        "damage_to_base": 2,
        "attack_damage": 18,
        "attack_rate": 0.6,
        "size": 22,
        "color": (105, 30, 130),
        "summon_cooldown": 6.0
    },
    "golem": {
        "name": "Golem de Piedra",
        "hp": 800,
        "speed": 28,
        "armor": 0.50,
        "magic_resist": 0.30,
        "gold_reward": 75,
        "damage_to_base": 5,
        "attack_damage": 55,
        "attack_rate": 0.5,
        "size": 32,
        "color": (110, 115, 125),
        "slow_immune": True
    },
    "dragon_boss": {
        "name": "Gran Dragón Carmesí (Jefe)",
        "hp": 2800,
        "speed": 34,
        "armor": 0.35,
        "magic_resist": 0.35,
        "gold_reward": 250,
        "damage_to_base": 15,
        "attack_damage": 80,
        "attack_rate": 0.4,
        "size": 48,
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
