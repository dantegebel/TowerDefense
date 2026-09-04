"""
Motor de Audio Procedural para 'Reino en Asedio'.
Genera efectos de sonido y música ambiental sintetizada mediante NumPy y Pygame Mixer.
"""

import numpy as np
import pygame

class SoundEngine:
    def __init__(self):
        self.enabled = True
        self.volume_sfx = 0.7
        self.volume_music = 0.5
        self.sounds = {}
        self.music_channel = None
        self.music_sound = None
        self.sample_rate = 44100
        self.initialized = False
        
        self.ensure_initialized()

    def ensure_initialized(self):
        """Intenta inicializar el mezclador de audio con múltiples fallbacks (44.1k, 48k, auto)."""
        if self.initialized:
            return True
        
        # Si pygame mixer no está inicializado, intentar varias configuraciones
        if not pygame.mixer.get_init():
            init_configs = [
                {"frequency": 44100, "size": -16, "channels": 2, "buffer": 1024},
                {"frequency": 48000, "size": -16, "channels": 2, "buffer": 1024},
                {} # Configuración por defecto del sistema operativo
            ]
            for cfg in init_configs:
                try:
                    pygame.mixer.init(**cfg)
                    break
                except Exception:
                    continue

        mix_init = pygame.mixer.get_init()
        if mix_init:
            try:
                self.sample_rate = mix_init[0]
                pygame.mixer.set_num_channels(32)
                self._generate_all_sounds()
                self._generate_ambient_music()
                self.initialized = True
                self.enabled = True
                return True
            except Exception as e:
                print(f"[AudioEngine] Error al generar sonidos: {e}")
                self.enabled = False
                return False
        else:
            self.enabled = False
            return False

    def _generate_sound_from_wave(self, wave_data):
        """Convierte un array de numpy float32 (-1 a 1) en un pygame.mixer.Sound adaptado a mono o estéreo."""
        wave_data = np.clip(wave_data, -1.0, 1.0)
        audio_int16 = (wave_data * 32767).astype(np.int16)
        
        mix_init = pygame.mixer.get_init()
        channels = mix_init[2] if mix_init else 2
        
        if channels == 1:
            # Modo Mono: sndarray requiere estrictamente un array 1D
            if audio_int16.ndim > 1:
                final_wave = np.ascontiguousarray(audio_int16[:, 0])
            else:
                final_wave = np.ascontiguousarray(audio_int16)
        else:
            # Modo Estéreo: sndarray requiere un array 2D (N, 2)
            if audio_int16.ndim == 1:
                final_wave = np.ascontiguousarray(np.column_stack((audio_int16, audio_int16)))
            else:
                final_wave = np.ascontiguousarray(audio_int16)
                
        return pygame.sndarray.make_sound(final_wave)

    def _generate_all_sounds(self):
        sr = self.sample_rate
        
        # 1. Disparo de arco (Bow shoot)
        duration = 0.15
        t = np.linspace(0, duration, int(sr * duration), False)
        # Ruido blanco modulado y un tono decreciente de cuerda (twang)
        freq = 320 * np.exp(-t * 18)
        twang = np.sin(2 * np.pi * freq * t)
        noise = np.random.uniform(-0.4, 0.4, len(t))
        env = np.exp(-t * 22)
        bow_wave = (twang * 0.7 + noise * 0.3) * env
        self.sounds["bow_shoot"] = self._generate_sound_from_wave(bow_wave)

        # 2. Impacto de flecha (Arrow hit)
        duration = 0.12
        t = np.linspace(0, duration, int(sr * duration), False)
        thud = np.sin(2 * np.pi * 180 * np.exp(-t * 30) * t)
        hit_wave = thud * np.exp(-t * 35)
        self.sounds["arrow_hit"] = self._generate_sound_from_wave(hit_wave)

        # 3. Choque de espadas (Sword slash / clank)
        duration = 0.22
        t = np.linspace(0, duration, int(sr * duration), False)
        freq1, freq2, freq3 = 2400, 3100, 4800
        clank = (np.sin(2 * np.pi * freq1 * t) * 0.4 +
                 np.sin(2 * np.pi * freq2 * t) * 0.3 +
                 np.sin(2 * np.pi * freq3 * t) * 0.3)
        noise = np.random.uniform(-0.3, 0.3, len(t))
        env = np.exp(-t * 25)
        sword_wave = (clank * 0.7 + noise * 0.3) * env
        self.sounds["sword_hit"] = self._generate_sound_from_wave(sword_wave)

        # 4. Explosión / Catapulta (Explosion / Rock impact)
        duration = 0.55
        t = np.linspace(0, duration, int(sr * duration), False)
        noise = np.random.uniform(-1.0, 1.0, len(t))
        low_rumble = np.sin(2 * np.pi * 80 * np.exp(-t * 4) * t)
        env = np.exp(-t * 7)
        explosion_wave = (noise * 0.6 + low_rumble * 0.4) * env
        self.sounds["explosion"] = self._generate_sound_from_wave(explosion_wave)

        # 5. Magia arcana (Magic zap / bolt)
        duration = 0.30
        t = np.linspace(0, duration, int(sr * duration), False)
        freq = 600 + 400 * np.sin(2 * np.pi * 15 * t) - t * 800
        magic_tone = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
        env = np.exp(-t * 10)
        magic_wave = magic_tone * 0.5 * env
        self.sounds["magic_zap"] = self.sounds["magic"] = self._generate_sound_from_wave(magic_wave)

        # 6. Escarcha / Congelación (Ice freeze)
        duration = 0.35
        t = np.linspace(0, duration, int(sr * duration), False)
        high_chime = np.sin(2 * np.pi * (1800 + 600 * t) * t) * 0.5 + np.sin(2 * np.pi * (2600 - 400 * t) * t) * 0.5
        noise = np.random.uniform(-0.2, 0.2, len(t))
        env = np.exp(-t * 9)
        freeze_wave = (high_chime * 0.6 + noise * 0.4) * env
        self.sounds["freeze"] = self._generate_sound_from_wave(freeze_wave)

        # 7. Rayo / Chispa (Lightning zap)
        duration = 0.28
        t = np.linspace(0, duration, int(sr * duration), False)
        freq = 1200 * np.exp(-t * 12)
        zap = np.sin(2 * np.pi * freq * t) + np.random.uniform(-0.6, 0.6, len(t))
        env = np.exp(-t * 15)
        lightning_wave = zap * 0.5 * env
        self.sounds["lightning"] = self._generate_sound_from_wave(lightning_wave)

        # 8. Monedas / Recompensa de Oro (Coin pickup)
        duration = 0.20
        t = np.linspace(0, duration, int(sr * duration), False)
        coin_wave = np.zeros_like(t)
        # Dos tonos rápidos estilo arpegio (987Hz -> 1318Hz, B5 -> E6)
        split = int(len(t) * 0.4)
        coin_wave[:split] = np.sin(2 * np.pi * 987.77 * t[:split]) * np.exp(-t[:split] * 12)
        coin_wave[split:] = np.sin(2 * np.pi * 1318.51 * (t[split:] - t[split])) * np.exp(-(t[split:] - t[split]) * 15)
        self.sounds["coin"] = self._generate_sound_from_wave(coin_wave * 0.6)

        # 9. Cuerno de Batalla Medieval (War Horn / Wave start)
        duration = 1.1
        t = np.linspace(0, duration, int(sr * duration), False)
        f0 = 220 # A3
        horn = (np.sin(2 * np.pi * f0 * t) * 0.6 +
                np.sin(2 * np.pi * (f0 * 2) * t) * 0.3 +
                np.sin(2 * np.pi * (f0 * 3) * t) * 0.15 +
                np.sin(2 * np.pi * (f0 * 4) * t) * 0.08)
        # Ataque suave y sostenido
        env = np.minimum(t * 5, 1.0) * np.exp(-t * 1.8)
        horn_wave = horn * env * 0.7
        self.sounds["horn"] = self._generate_sound_from_wave(horn_wave)

        # 10. Click de botón / UI
        duration = 0.05
        t = np.linspace(0, duration, int(sr * duration), False)
        click_wave = np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 80)
        self.sounds["click"] = self._generate_sound_from_wave(click_wave * 0.5)

        # 11. Mejora de torre (Upgrade / Build)
        duration = 0.35
        t = np.linspace(0, duration, int(sr * duration), False)
        up_wave = (np.sin(2 * np.pi * 440 * t) * 0.4 +
                   np.sin(2 * np.pi * 554.37 * t) * 0.3 +
                   np.sin(2 * np.pi * 659.25 * t) * 0.3) * np.exp(-t * 8)
        self.sounds["upgrade"] = self._generate_sound_from_wave(up_wave * 0.7)
        self.sounds["build"] = self.sounds["upgrade"]

        # 12. Lluvia de flechas (Arrow rain)
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration), False)
        noise = np.random.uniform(-0.5, 0.5, len(t))
        # Varios silbidos aleatorios
        whistle = np.sin(2 * np.pi * (800 + 400 * np.sin(20 * t)) * t) * 0.3
        env = np.sin(np.pi * t / duration)
        self.sounds["arrow_rain"] = self._generate_sound_from_wave((noise * 0.5 + whistle) * env * 0.6)

        # 13. Victoria (Victory fanfare)
        duration = 1.6
        t = np.linspace(0, duration, int(sr * duration), False)
        notes = [523.25, 659.25, 783.99, 1046.50] # C5, E5, G5, C6
        fanfare = np.zeros_like(t)
        n_len = len(t) // 4
        for i, n in enumerate(notes):
            idx_s = i * n_len
            idx_e = (i + 1) * n_len if i < 3 else len(t)
            sub_t = t[idx_s:idx_e] - t[idx_s]
            decay = 5.0 if i < 3 else 1.8
            fanfare[idx_s:idx_e] = (np.sin(2 * np.pi * n * sub_t) * 0.6 + 
                                    np.sin(2 * np.pi * n * 2 * sub_t) * 0.3) * np.exp(-sub_t * decay)
        self.sounds["victory"] = self._generate_sound_from_wave(fanfare * 0.7)

        # 14. Derrota (Defeat sound)
        duration = 1.5
        t = np.linspace(0, duration, int(sr * duration), False)
        f_start = 220
        f_end = 80
        freqs = f_start + (f_end - f_start) * (t / duration)
        defeat_wave = (np.sin(2 * np.pi * freqs * t) * 0.6 + 
                       np.sin(2 * np.pi * (freqs * 0.5) * t) * 0.4) * np.exp(-t * 2)
        self.sounds["defeat"] = self._generate_sound_from_wave(defeat_wave * 0.7)

        # 15. Salpicadura de ácido / brea (Alquimista)
        duration = 0.25
        t = np.linspace(0, duration, int(sr * duration), False)
        noise = np.random.uniform(-0.6, 0.6, len(t))
        bubble = np.sin(2 * np.pi * (350 + 200 * np.sin(40 * t)) * t)
        env = np.exp(-t * 12)
        self.sounds["acid_splash"] = self._generate_sound_from_wave((bubble * 0.6 + noise * 0.4) * env * 0.7)

        # 16. Rayo Solar celestial (Santuario Solar)
        duration = 0.35
        t = np.linspace(0, duration, int(sr * duration), False)
        laser = np.sin(2 * np.pi * (700 + 350 * np.exp(-t * 8)) * t) * 0.5
        harm = np.sin(2 * np.pi * (1400 + 700 * np.exp(-t * 8)) * t) * 0.3
        env = np.sin(np.pi * t / duration) ** 0.5
        self.sounds["sun_beam"] = self._generate_sound_from_wave((laser + harm) * env * 0.6)

    def _generate_ambient_music(self):
        """Genera un loop musical ambiental medieval sintetizado (laúd y cuerdas suaves)."""
        sr = self.sample_rate
        bpm = 75
        beat_len = 60 / bpm
        total_beats = 32
        total_duration = total_beats * beat_len # ~25.6 segundos
        t_total = np.linspace(0, total_duration, int(sr * total_duration), False)
        
        music_wave = np.zeros_like(t_total)
        
        # Progresión armónica medieval (D menor, F mayor, C mayor, G menor / Dm)
        chord_freqs = [
            [146.83, 220.00, 261.63, 293.66, 349.23], # Dm
            [174.61, 220.00, 261.63, 349.23, 440.00], # F
            [130.81, 196.00, 261.63, 329.63, 392.00], # C
            [146.83, 220.00, 293.66, 349.23, 440.00], # Dm cadencia
        ]
        
        step_duration = beat_len * 0.5 # Corcheas
        total_steps = int(total_duration / step_duration)
        
        for step in range(total_steps):
            bar = (step // 8) % 4
            chord = chord_freqs[bar]
            note_idx = (step % 5 + (step // 3) % 2) % len(chord)
            freq = chord[note_idx]
            
            s_start = int(step * step_duration * sr)
            s_len = int(step_duration * 2.5 * sr)
            s_end = min(s_start + s_len, len(t_total))
            actual_len = s_end - s_start
            
            t_note = np.linspace(0, actual_len / sr, actual_len, False)
            note_wave = (np.sin(2 * np.pi * freq * t_note) * 0.5 +
                         np.sin(2 * np.pi * freq * 2 * t_note) * 0.25 +
                         np.sin(2 * np.pi * freq * 3 * t_note) * 0.15 +
                         np.sin(2 * np.pi * freq * 4 * t_note) * 0.10)
            env = np.exp(-t_note * 4.5)
            music_wave[s_start:s_end] += note_wave * env * 0.22

        music_wave = np.clip(music_wave, -0.9, 0.9)
        self.music_sound = self._generate_sound_from_wave(music_wave)

    def play(self, sound_name):
        """Reproduce un efecto de sonido."""
        if not self.initialized:
            self.ensure_initialized()
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            snd.set_volume(self.volume_sfx)
            snd.play()

    def start_music(self):
        """Inicia la música ambiental en bucle."""
        if not self.initialized:
            self.ensure_initialized()
        if not self.enabled or not self.music_sound:
            return
        if self.music_channel is None:
            try:
                self.music_channel = pygame.mixer.Channel(0)
            except Exception:
                return
        self.music_sound.set_volume(self.volume_music)
        self.music_channel.play(self.music_sound, loops=-1)

    def stop_music(self):
        if self.music_channel:
            self.music_channel.stop()

    def toggle_sound(self):
        if not self.initialized:
            self.ensure_initialized()
        
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_music()
        else:
            self.start_music()
        return self.enabled

# Instancia singleton global
sound_manager = SoundEngine()
