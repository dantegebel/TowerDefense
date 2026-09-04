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
        
        # Inicializar audio de manera segura
        sound_manager.ensure_initialized()

        self.virtual_width = SCREEN_WIDTH
        self.virtual_height = SCREEN_HEIGHT
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))
        
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Monkey-patch pygame.mouse.get_pos para soporte transparente de escalado en todas las escenas
        self._orig_mouse_get_pos = pygame.mouse.get_pos
        pygame.mouse.get_pos = self.get_virtual_mouse_pos
        
        self.progress_data = self._load_progress()
        self.current_scene = None
        self.current_level = None
        
        # Establecer escena inicial de menú
        self.set_menu_scene()

    def get_viewport_transform(self):
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / self.virtual_width, win_h / self.virtual_height)
        render_w = int(self.virtual_width * scale)
        render_h = int(self.virtual_height * scale)
        offset_x = (win_w - render_w) // 2
        offset_y = (win_h - render_h) // 2
        return scale, offset_x, offset_y, render_w, render_h

    def to_virtual_coords(self, physical_pos):
        scale, offset_x, offset_y, _, _ = self.get_viewport_transform()
        if scale <= 0:
            return physical_pos
        px, py = physical_pos
        vx = (px - offset_x) / scale
        vy = (py - offset_y) / scale
        return int(max(0, min(self.virtual_width, vx))), int(max(0, min(self.virtual_height, vy)))

    def get_virtual_mouse_pos(self):
        raw_pos = self._orig_mouse_get_pos()
        return self.to_virtual_coords(raw_pos)

    def _load_progress(self):
        prog = {f"level_{lvl['id']}": {"stars": 0, "score": 0} for lvl in LEVELS}
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    prog.update(data)
            except Exception:
                pass
        return prog

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
            dt = min(dt, 0.1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                else:
                    # Mapear coordenadas de ratón al canvas virtual
                    if hasattr(event, "pos"):
                        vx, vy = self.to_virtual_coords(event.pos)
                        event.dict["pos"] = (vx, vy)
                        # También asignar atributo si el evento lo expone
                        try:
                            event.pos = (vx, vy)
                        except AttributeError:
                            pass
                    
                    if self.current_scene:
                        self.current_scene.handle_event(event)

            # Actualizar y dibujar en el canvas virtual
            if self.current_scene:
                self.current_scene.update(dt)
                self.current_scene.draw(self.virtual_screen)

            # Escalar y presentar en pantalla con bandas negras (letterboxing)
            scale, offset_x, offset_y, render_w, render_h = self.get_viewport_transform()
            self.screen.fill(COLOR_BG_DARK)
            scaled_surf = pygame.transform.smoothscale(self.virtual_screen, (render_w, render_h))
            self.screen.blit(scaled_surf, (offset_x, offset_y))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
