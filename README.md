# ⚔️ Reino en Asedio: Medieval Tower Defense ⚔️

Un juego completo de defensa de torres (*Tower Defense*) con temática medieval clásica desarrollado en **Python 3.13** y **Pygame-CE**.

---

## 🏰 Cómo Ejecutar el Juego

Para iniciar el juego, ejecuta en la terminal:

```bash
python main.py
```

---

## 🎮 Controles y Atajos de Teclado

| Tecla / Acción | Descripción |
| :--- | :--- |
| **Click Izquierdo** | Seleccionar pedestal para construir, seleccionar torre para mejorar/vender, lanzar hechizos. |
| **Click Derecho / Esc** | Cancelar selección o casteo de hechizo. |
| **[Q]** | Habilidad Activa: **Lluvia de Flechas** (Daño físico en área). |
| **[W]** | Habilidad Activa: **Guardia Real** (Invoca 2 soldados aliados en el camino). |
| **[E]** | Habilidad Activa: **Meteoro de Fuego** (Impacto masivo y suelo en llamas). |
| **[1] / [2] / [3]** | Cambiar velocidad del juego (**1x**, **2x**, **4x**). |
| **[Espacio]** | Pausar / Reanudar el juego. |

---

## 🏹 Tipos de Torres y Especializaciones

1. **Torre de Arqueros** (70🪙):
   - Ataques rápidos con flechas a distancia.
   - *Especialización A:* **Ballesta Pesada** (Golpes críticos y flechas perforantes).
   - *Especialización B:* **Tiradores Élficos** (Cadencia ultra rápida y veneno).

2. **Catapulta de Rocas** (110🪙):
   - Daño de área masivo con rocas explosivas (no ataca unidades aéreas).
   - *Especialización A:* **Fuego Valyrio** (Deja el suelo en llamas con daño por segundo).
   - *Especialización B:* **Batería de Morteros** (Disparos con aturdimiento).

3. **Torre de Magos** (90🪙):
   - Proyectiles de energía arcana que ignoran la armadura física.
   - *Especialización A:* **Torre de Hielo** (Ralentiza a los enemigos en un 50%).
   - *Especialización B:* **Tormenta de Rayos** (Relámpagos en cadena que saltan entre 4 enemigos).

4. **Barracones de la Guardia** (80🪙):
   - Entrena a 3 soldados que se sitúan en el camino, bloquean físicamente el paso y luchan cuerpo a cuerpo.
   - Posibilidad de cambiar la bandera de punto de reunión (*Rally Point*).
   - *Especialización A:* **Paladines Sagrados** (Escudos bendecidos y auto-curación).
   - *Especialización B:* **Caballeros Bárbaros** (Doble hacha con ataque rápido).

---

## 🧌 Enemigos y Jefes

- **Duende Asaltante**: Rápido y numeroso.
- **Soldado Esqueleto**: Infantería oscura resistente.
- **Orco Berserker**: Alta vida y daño.
- **Caballero Negro**: Blindaje pesado (70% resistencia física, vulnerable a magia).
- **Nigromante**: Invoca esqueletos durante su marcha.
- **Golem de Piedra**: Coloso tanque inmune a ralentizaciones.
- **Gran Dragón Carmesí (Jefe)**: Unidad voladora majestuosa con barra de vida colosal.

---

## 🌟 Niveles de Campaña

1. **Nivel 1: Valle Verde** - Llanuras occidentales (10 oleadas).
2. **Nivel 2: Paso de la Montaña Oscura** - Desfiladero de dos senderos convergentes (11 oleadas).
3. **Nivel 3: La Ciudadela Real** - Asalto masivo con 2 carriles y combate final contra el Gran Dragón (8 oleadas).
