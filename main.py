"""
Punto de Entrada Principal de 'Reino en Asedio: Medieval Tower Defense'.
Ejecuta el bucle del juego, la gestión de estados y la persistencia de progreso.
"""

import os
import sys
import json
import pygame

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLOR_BG_DARK
from engine.audio import sound_manager
from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene
from scenes.gameover_scene import GameOverScene
from maps.levels import LEVELS

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_data.json")

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.progress_data = self._load_progress()
        self.current_scene = None
        self.current_level = None
        
        # Establecer escena inicial de menú
        self.set_menu_scene()

    def _load_progress(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "level_1": {"stars": 0, "score": 0},
            "level_2": {"stars": 0, "score": 0},
            "level_3": {"stars": 0, "score": 0}
        }

    def _save_progress(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            print(f"Error al guardar progreso: {e}")

    def set_menu_scene(self):
        self.current_scene = MenuScene(self.start_level, self.progress_data)

    def start_level(self, level_data):
        self.current_level = level_data
        self.current_scene = GameScene(level_data, self.on_game_over)

    def on_game_over(self, victory, lives_left, max_lives, score, enemies_killed):
        lvl_key = f"level_{self.current_level['id']}"
        prev = self.progress_data.get(lvl_key, {"stars": 0, "score": 0})
        
        # Calcular estrellas
        stars = 0
        if victory:
            ratio = lives_left / max(1, max_lives)
            stars = 3 if ratio >= 0.85 else (2 if ratio >= 0.40 else 1)

        self.progress_data[lvl_key] = {
            "stars": max(prev["stars"], stars),
            "score": max(prev["score"], score)
        }
        self._save_progress()

        def next_level_cb():
            next_id = self.current_level["id"] + 1
            for lvl in LEVELS:
                if lvl["id"] == next_id:
                    self.start_level(lvl)
                    return
            self.set_menu_scene()

        def retry_cb():
            self.start_level(self.current_level)

        def menu_cb():
            self.set_menu_scene()

        self.current_scene = GameOverScene(
            victory, lives_left, max_lives, score, enemies_killed,
            self.current_level, next_level_cb, retry_cb, menu_cb
        )

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            # Limitar dt máximo para evitar saltos enormes por lag
            dt = min(dt, 0.1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    if self.current_scene:
                        self.current_scene.handle_event(event)

            if self.current_scene:
                self.current_scene.update(dt)
                self.current_scene.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
