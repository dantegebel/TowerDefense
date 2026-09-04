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
| **[F11]** | Alternar **Pantalla Completa** (o arrastra los bordes de la ventana libremente). |
| **[Q]** | Habilidad Activa: **Lluvia de Flechas** (Daño físico en área). |
| **[W]** | Habilidad Activa: **Guardia Real** (Invoca 2 soldados aliados en el camino). |
| **[E]** | Habilidad Activa: **Meteoro de Fuego** (Impacto masivo y suelo en llamas). |
| **[1] / [2] / [4]** | Cambiar velocidad del juego (**1x**, **2x**, **4x**). |
| **[Espacio] / [P]** | Pausar / Reanudar el juego. |

---

## 🏹 Las 6 Torres Defensivas y sus 12 Especializaciones (Tier 4)

Al subir cualquier estructura a **Nivel 3**, se desbloquean dos ramas de especialización legendaria (**[A]** y **[B]**). Pasa el cursor sobre cada opción para ver su ficha técnica completa:

1. **Torre de Arqueros** (70🪙):
   - Ataques rápidos con flechas a distancia.
   - *Rama [A]:* **Ballesta Pesada** (Flechas perforantes con alta probabilidad crítica x2.5).
   - *Rama [B]:* **Tiradores Élficos** (Cadencia extrema de 3 tiros/s con veneno acumulativo).

2. **Catapulta de Rocas** (110🪙):
   - Daño de área masivo con rocas explosivas (no ataca unidades aéreas).
   - *Rama [A]:* **Fuego Valyrio** (Lava ardiente en el suelo con 25 DPS de quemadura).
   - *Rama [B]:* **Batería de Morteros** (Proyectiles pesados con aturdimiento de 0.8s).

3. **Torre de Magos** (90🪙):
   - Proyectiles de energía arcana que ignoran la armadura física enemiga.
   - *Rama [A]:* **Torre de Hielo** (Esferas gélidas que ralentizan a los enemigos en un 50%).
   - *Rama [B]:* **Tormenta de Rayos** (Relámpagos en cadena que saltan entre hasta 4 objetivos).

4. **Barracones de la Guardia** (80🪙):
   - Entrena a 3 soldados que se sitúan en el camino, bloquean físicamente el paso y luchan cuerpo a cuerpo.
   - Permite reubicar libremente su bandera de reunión (*Rally Point*).
   - *Rama [A]:* **Paladines Sagrados** (Escudos bendecidos, 65% armadura y auto-regeneración de vida).
   - *Rama [B]:* **Caballeros Bárbaros** (Doble hacha con ataque rápido y 65 de daño cuerpo a cuerpo).

5. **Torre de Alquimia** (100🪙):
   - Lanza frascos de brea y ácido corrosivo que funden la armadura y ralentizan.
   - *Rama [A]:* **Laboratorio de Plagas** (Nubes venenosas persistentes con 22 DPS de daño continuo).
   - *Rama [B]:* **Lanza-Ácido Corrosivo** (Destruye el 80% de la armadura enemiga e inflige quemadura).

6. **Santuario Solar** (120🪙):
   - Canaliza un rayo solar continuo divino ideal para derretir tanques y jefes colosales.
   - *Rama [A]:* **Juicio Divino** (Rayo superconcentrado de 240 de daño a 3 pulsos/s).
   - *Rama [B]:* **Aura de Bendición Real** (Aura dorada que otorga +30% daño y alcance a torres aliadas cercanas).

---

## 🧌 Enemigos y Jefes

- **Duende Asaltante**: Rápido y numeroso.
- **Soldado Esqueleto**: Infantería oscura resistente.
- **Orco Berserker**: Gran vida y alto daño de impacto.
- **Caballero Negro**: Blindaje pesado (65% resistencia física, vulnerable a daño arcano/ácido).
- **Nigromante**: Invoca esqueletos oscuros durante su avance.
- **Troll de las Cavernas**: Bestia colosal con regeneración pasiva constante de vida (+18 HP/s).
- **Golem de Piedra**: Coloso tanque inmune a ralentizaciones y aturdimientos.
- **Guiverno Alado**: Depredador aéreo veloz que sobrevuela las defensas terrestres.
- **Gran Dragón Carmesí (Jefe)**: Majestuoso dragón rojo con aliento ígneo y barra de vida colosal.

---

## 🌟 Campaña Completa de 10 Niveles

1. **Nivel 1: Valle Verde** - Llanuras occidentales con 1 sendero sinuoso (10 oleadas, Bioma Pradera).
2. **Nivel 2: Paso de la Montaña Oscura** - Desfiladero con 2 senderos convergentes en un puente (11 oleadas, Bioma Montaña).
3. **Nivel 3: La Ciudadela Real** - Asalto masivo con 2 carriles independientes y duelo contra el Gran Dragón (8 oleadas, Bioma Pradera).
4. **Nivel 4: La Encrucijada Maldita** - Pantano brumoso con 3 caminos simultáneos invadidos por Trolls y Guivernos (10 oleadas, Bioma Pantano).
5. **Nivel 5: La Grieta de Lava** - Bastión volcánico con 4 rutas serpenteantes y doble jefe dragón (11 oleadas, Bioma Volcánico).
6. **Nivel 6: Cumbres Blancas** - Paso helado del norte con ventiscas y 2 rutas convergentes (10 oleadas, Bioma Nieve).
7. **Nivel 7: Ruinas de Aethelgard** - Antiguo templo en el desierto con 3 caminos entre dunas y oasis (11 oleadas, Bioma Desierto).
8. **Nivel 8: El Pantano del Terror** - Ciénaga profunda de aguas estancadas con 3 caminos serpenteantes (12 oleadas, Bioma Pantano).
9. **Nivel 9: El Desfiladero del Dragón** - Garganta montañosa vertical con 3 rutas de asedio y enjambres de guivernos (12 oleadas, Bioma Montaña).
10. **Nivel 10: El Trono de la Perdición** - Batalla final legendaria con 4 caminos simultáneos de lava y asedio titánico (14 oleadas, Bioma Volcánico).

