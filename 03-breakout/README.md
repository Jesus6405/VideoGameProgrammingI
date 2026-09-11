# 🎮 Breakout - Power-Ups Edition

Proyecto del curso de Programación de Videojuegos I. Esta edición extiende el clásico juego **Breakout** incorporando una arquitectura dinámica de *power-ups* aleatorios que caen al destruir ladrillos.

---

## 🕹️ Controles del Juego

| Tecla | Acción |
| :--- | :--- |
| **`Flecha Izquierda` / `Flecha Derecha`** | Mover la paleta horizontalmente |
| **`Barra Espaciadora` (`Space`)** | Pausar / Reanudar el juego |
| **`Tecla F`** | **Disparar cañones** (cuando el power-up de cañones está activo) |
| **`Enter`** | Confirmar / Servir en inicio / Lanzar pelota atrapada |
| **`Escape`** | Salir del juego |

---

## 🌟 Power-Ups Implementados

### 🎾 1. Power-Up de Captura de Pelota (`BallCatch`)
- **Icono**: Esfera adhesiva de agarre.
- **Duración**: 12 segundos.
- **Mecánica**:
  - Al recolectar este power-up, la superficie superior de la paleta se vuelve adherente (resaltada visualmente con un indicador brillante verde).
  - Cuando una pelota colisiona con la paleta en movimiento o reposo, en lugar de rebotar inmediatamente, **queda atrapada e inmovilizada en el punto exacto de impacto**.
  - Al igual que en el estado de saque, el jugador puede mover libremente la paleta a través de la pantalla llevando la pelota adherida.
  - Al presionar el **Enter**, la pelota es lanzada nuevamente.

---

### 🚀 2. Power-Up de Cañones (`Cannons`)
- **Icono**: Torretas de disparo lateral.
- **Duración**: 12 segundos.
- **Mecánica**:
  - Transforma la paleta equipándola con **dos torretas de cañón en sus extremos izquierdo y derecho**.
  - Al presionar la tecla **`F`**, la paleta dispara **simultáneamente un par de proyectiles láser** verticalmente hacia arriba a gran velocidad.
  - **Comportamiento de impacto**: Al colisionar con un ladrillo, el proyectil impacta al ladrillo (reduciendo su resistencia/destruyéndolo), incrementa la puntuación del jugador y el proyectil se destruye.
  - **Control de proyectiles**: Para evitar la saturación en pantalla, **no se permite realizar un nuevo disparo mientras haya proyectiles activos en la escena**.

---

### ✨ 3. Power-Up Adicional: Escudo Protector de Fondo (`FloorShield`)
- **Icono**: Emblema de barrera energética.
- **Duración**: 8 segundos.
- **Mecánica y Descripción Detallada**:
  - Al recolectar este power-up, se despliega una **barrera láser/campo de fuerza resplandeciente cian** en la parte más baja del área de juego.
  - Durante los 8 segundos de su tiempo de vida, si el jugador no logra posicionar la paleta a tiempo y una pelota cae por debajo del área inferior, el **Escudo de Fondo absorbe el impacto de la pelota y la rebota de vuelta hacia arriba**, impidiendo que el jugador pierda una vida.
  - Otorga una red de seguridad estratégica ideal para combinar con el power-up de múltiples pelotas (`TwoMoreBall`), permitiendo una jugabilidad agresiva sin riesgo de perder vidas por descuidos momentáneos.

---

## 🛠️ Estructura del Código

- `src/powerups/BallCatch.py`: Clase del power-up de captura de pelota.
- `src/powerups/Cannons.py`: Clase del power-up de cañones.
- `src/powerups/FloorShield.py`: Clase del power-up de escudo protector de fondo.
- `src/Projectile.py`: Proyectiles láser disparados por las torretas de la paleta.
- `src/Paddle.py`: Lógica de renderizado y temporizadores para el estado adherente y cañones.
- `src/Ball.py`: Lógica para anclaje a la paleta, movimiento relativo y liberación de pelota.
- `src/states/PlayState.py`: Gestión global del bucle de juego, colisiones, generación aleatoria y respuesta a controles.
